# modules/triage_rules.py
"""
Rule-based triage logic that maps intake forms to hospital sorting criteria.

This module provides transparent, explainable triage recommendations based on:
- Chief complaint (chest pain, stroke symptoms, respiratory issues, etc.)
- Severity level (1-5 scale)
- Age band (child/adult/senior)
- Vital signs (optional: HR, BP, RR, temp, O2sat)

Output includes recommended sorting method, weights, and clear explanations.
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class VitalSigns:
    """Container for patient vital signs."""
    heart_rate: Optional[float] = None  # beats per minute
    systolic_bp: Optional[float] = None  # mmHg
    diastolic_bp: Optional[float] = None  # mmHg
    respiratory_rate: Optional[float] = None  # breaths per minute
    temperature: Optional[float] = None  # Celsius
    oxygen_saturation: Optional[float] = None  # percentage
    
    def is_critical(self) -> bool:
        """Check if any vitals indicate critical condition."""
        critical = False
        if self.heart_rate is not None:
            critical |= (self.heart_rate < 40 or self.heart_rate > 140)
        if self.systolic_bp is not None:
            critical |= (self.systolic_bp < 90 or self.systolic_bp > 180)
        if self.oxygen_saturation is not None:
            critical |= (self.oxygen_saturation < 90)
        if self.respiratory_rate is not None:
            critical |= (self.respiratory_rate < 10 or self.respiratory_rate > 30)
        return critical
    
    def is_unstable(self) -> bool:
        """Check if vitals indicate unstable but not critical condition."""
        unstable = False
        if self.heart_rate is not None:
            unstable |= (self.heart_rate < 50 or self.heart_rate > 120)
        if self.systolic_bp is not None:
            unstable |= (self.systolic_bp < 100 or self.systolic_bp > 160)
        if self.oxygen_saturation is not None:
            unstable |= (self.oxygen_saturation < 94)
        if self.respiratory_rate is not None:
            unstable |= (self.respiratory_rate < 12 or self.respiratory_rate > 24)
        return unstable and not self.is_critical()


@dataclass
class TriageProfile:
    """Output of triage decision logic."""
    recommended_sort: str  # quality/time/rating/mortality
    weights: Dict[str, float]  # sorting weight adjustments
    explanation: str  # human-readable explanation
    urgency_level: int  # 1-5 (5 = most urgent)
    quality_column: str  # which quality column to use (overall, heart attack, stroke, pneu)


# Complaint mapping to quality columns
COMPLAINT_MAP = {
    "chest pain": "adj_total_heartattack",
    "heart attack": "adj_total_heartattack",
    "cardiac": "adj_total_heartattack",
    "angina": "adj_total_heartattack",
    
    "stroke": "adj_total_stroke",
    "stroke symptoms": "adj_total_stroke",
    "slurred speech": "adj_total_stroke",
    "facial droop": "adj_total_stroke",
    "weakness": "adj_total_stroke",
    "numbness": "adj_total_stroke",
    
    "respiratory": "adj_total_pneu",
    "fever": "adj_total_pneu",
    "cough": "adj_total_pneu",
    "shortness of breath": "adj_total_pneu",
    "trouble breathing": "adj_total_pneu",
    "pneumonia": "adj_total_pneu",
    "covid": "adj_total_pneu",
    
    "other": "total_quality_points",
    "overall": "total_quality_points",
    "general": "total_quality_points",
}


def normalize_complaint(complaint: str) -> str:
    """Normalize complaint string to match keys in COMPLAINT_MAP."""
    complaint_lower = complaint.lower().strip()
    # Try exact match first
    if complaint_lower in COMPLAINT_MAP:
        return complaint_lower
    # Try partial matches
    for key in COMPLAINT_MAP.keys():
        if key in complaint_lower or complaint_lower in key:
            return key
    return "overall"


def parse_age_band(age: Optional[int]) -> str:
    """Convert age to age band."""
    if age is None:
        return "adult"
    if age < 18:
        return "child"
    elif age >= 65:
        return "senior"
    else:
        return "adult"


def get_triage_recommendation(
    chief_complaint: str,
    severity: int = 3,
    age: Optional[int] = None,
    vital_signs: Optional[VitalSigns] = None,
) -> TriageProfile:
    """
    Implement transparent rule-based triage logic.
    
    Args:
        chief_complaint: Patient's chief complaint (free text)
        severity: Severity level 1-5 (1=minor, 5=critical)
        age: Patient age in years (optional)
        vital_signs: VitalSigns object (optional)
    
    Returns:
        TriageProfile with recommended sorting, weights, and explanation
    
    Rules:
    1. Critical complaints (chest pain, stroke) → prefer time or quality
    2. High severity (4-5) or critical vitals → prefer time
    3. Stable vitals + low severity → prefer quality/rating
    4. Age bands influence priority but not sorting method
    """
    # Normalize inputs
    severity = max(1, min(5, severity))  # Clamp to 1-5
    normalized_complaint = normalize_complaint(chief_complaint)
    age_band = parse_age_band(age)
    quality_column = COMPLAINT_MAP.get(normalized_complaint, "total_quality_points")
    
    # Check vitals if provided
    vitals_critical = vital_signs.is_critical() if vital_signs else False
    vitals_unstable = vital_signs.is_unstable() if vital_signs else False
    
    # Decision logic
    urgency_level = severity
    
    # Critical scenarios: prefer fastest time
    if vitals_critical or severity >= 5:
        recommended_sort = "detail_avg_time_in_ed_minutes"
        weights = {"time": 1.0, "quality": 0.3}
        explanation = (
            f"URGENT: For {chief_complaint} with critical severity/vitals, "
            f"prioritizing fastest ED time to minimize wait. Use {quality_column} for quality assessment."
        )
        urgency_level = 5
    
    # High urgency time-sensitive complaints (chest pain, stroke)
    elif normalized_complaint in ["chest pain", "heart attack", "cardiac", "angina", "stroke", "stroke symptoms"]:
        if severity >= 4 or vitals_unstable:
            recommended_sort = "detail_avg_time_in_ed_minutes"
            weights = {"time": 0.8, "quality": 0.5}
            explanation = (
                f"HIGH URGENCY: For {chief_complaint} with high severity, "
                f"prioritizing fast ED time while considering quality ({quality_column}). "
                f"Time-sensitive condition requiring immediate care."
            )
            urgency_level = max(urgency_level, 4)
        else:
            # Lower severity: balance quality and time
            recommended_sort = "adjusted_quality_points"
            weights = {"quality": 0.8, "time": 0.5}
            explanation = (
                f"MODERATE: For {chief_complaint} with moderate severity, "
                f"prioritizing specialized quality care ({quality_column}) while keeping ED time reasonable. "
                f"Balance between expertise and speed."
            )
            urgency_level = max(urgency_level, 3)
    
    # Respiratory complaints
    elif normalized_complaint in ["respiratory", "fever", "pneumonia", "covid", "shortness of breath", "trouble breathing"]:
        if severity >= 4 or vitals_unstable:
            recommended_sort = "detail_avg_time_in_ed_minutes"
            weights = {"time": 0.7, "quality": 0.5}
            explanation = (
                f"HIGH PRIORITY: For {chief_complaint} with elevated severity, "
                f"prioritizing fast ED time. Use {quality_column} for quality assessment."
            )
            urgency_level = max(urgency_level, 4)
        else:
            recommended_sort = "adjusted_quality_points"
            weights = {"quality": 0.7, "time": 0.4}
            explanation = (
                f"MODERATE: For {chief_complaint} with stable vitals, "
                f"prioritizing quality of respiratory care ({quality_column}) with reasonable wait times."
            )
            urgency_level = max(urgency_level, 3)
    
    # Low severity or stable conditions: prefer quality or rating
    elif severity <= 2 and not vitals_unstable:
        recommended_sort = "detail_overall_patient_rating"
        weights = {"rating": 0.8, "quality": 0.5}
        explanation = (
            f"ROUTINE: For {chief_complaint} with low severity and stable vitals, "
            f"prioritizing patient experience and overall quality. "
            f"Time is less critical."
        )
        urgency_level = min(urgency_level, 2)
    
    # Default: balanced quality-focused approach
    else:
        recommended_sort = "adjusted_quality_points"
        weights = {"quality": 0.8, "time": 0.4, "rating": 0.3}
        explanation = (
            f"STANDARD: For {chief_complaint} with severity {severity}, "
            f"prioritizing quality care ({quality_column}) with balanced consideration of wait time and ratings."
        )
    
    # Age band considerations (informational, doesn't change sort)
    if age_band == "child":
        explanation += " [Pediatric case - ensure facility has pediatric capabilities]"
    elif age_band == "senior":
        explanation += " [Geriatric case - may need specialized elder care]"
    
    logger.info(
        "Triage recommendation: complaint=%s, severity=%d, age_band=%s, sort=%s, urgency=%d",
        normalized_complaint, severity, age_band, recommended_sort, urgency_level
    )
    
    return TriageProfile(
        recommended_sort=recommended_sort,
        weights=weights,
        explanation=explanation,
        urgency_level=urgency_level,
        quality_column=quality_column
    )


def triage_from_form(form_data: Dict) -> TriageProfile:
    """
    Convenience function to extract triage recommendation from form data.
    
    Expected form fields:
    - chief_complaint: str
    - severity: int (1-5)
    - age: int (optional)
    - heart_rate: float (optional)
    - systolic_bp: float (optional)
    - diastolic_bp: float (optional)
    - respiratory_rate: float (optional)
    - temperature: float (optional)
    - oxygen_saturation: float (optional)
    
    Returns:
        TriageProfile with recommendation
    """
    chief_complaint = form_data.get("chief_complaint", "other")
    severity = int(form_data.get("severity", 3))
    age = form_data.get("age")
    if age is not None:
        age = int(age)
    
    # Parse vital signs if provided
    vital_signs = None
    if any(k in form_data for k in ["heart_rate", "systolic_bp", "oxygen_saturation", "respiratory_rate"]):
        vital_signs = VitalSigns(
            heart_rate=form_data.get("heart_rate"),
            systolic_bp=form_data.get("systolic_bp"),
            diastolic_bp=form_data.get("diastolic_bp"),
            respiratory_rate=form_data.get("respiratory_rate"),
            temperature=form_data.get("temperature"),
            oxygen_saturation=form_data.get("oxygen_saturation"),
        )
    
    return get_triage_recommendation(
        chief_complaint=chief_complaint,
        severity=severity,
        age=age,
        vital_signs=vital_signs
    )

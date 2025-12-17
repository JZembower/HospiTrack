# tests/test_triage.py
"""Tests for triage logic (rule-based and ML)."""

import pytest
from modules.triage_rules import (
    get_triage_recommendation,
    normalize_complaint,
    parse_age_band,
    VitalSigns,
    triage_from_form
)


class TestComplaintNormalization:
    """Test complaint normalization."""
    
    def test_chest_pain(self):
        assert normalize_complaint("chest pain") == "chest pain"
        assert normalize_complaint("Chest Pain") == "chest pain"
        assert normalize_complaint("cardiac chest pain") == "chest pain"
    
    def test_stroke(self):
        assert normalize_complaint("stroke") == "stroke"
        assert normalize_complaint("stroke symptoms") == "stroke symptoms"
    
    def test_respiratory(self):
        assert normalize_complaint("shortness of breath") == "shortness of breath"
        assert normalize_complaint("fever") == "fever"
    
    def test_fallback(self):
        assert normalize_complaint("unknown complaint") == "overall"


class TestAgeBand:
    """Test age band parsing."""
    
    def test_child(self):
        assert parse_age_band(5) == "child"
        assert parse_age_band(17) == "child"
    
    def test_adult(self):
        assert parse_age_band(18) == "adult"
        assert parse_age_band(45) == "adult"
        assert parse_age_band(64) == "adult"
    
    def test_senior(self):
        assert parse_age_band(65) == "senior"
        assert parse_age_band(80) == "senior"
    
    def test_none(self):
        assert parse_age_band(None) == "adult"


class TestVitalSigns:
    """Test vital signs evaluation."""
    
    def test_critical_vitals(self):
        vitals = VitalSigns(
            heart_rate=150,
            systolic_bp=190,
            oxygen_saturation=85
        )
        assert vitals.is_critical() is True
    
    def test_unstable_vitals(self):
        vitals = VitalSigns(
            heart_rate=125,
            systolic_bp=165,
            oxygen_saturation=93
        )
        assert vitals.is_unstable() is True
        assert vitals.is_critical() is False
    
    def test_stable_vitals(self):
        vitals = VitalSigns(
            heart_rate=80,
            systolic_bp=120,
            oxygen_saturation=98
        )
        assert vitals.is_critical() is False
        assert vitals.is_unstable() is False


class TestTriageRecommendation:
    """Test triage recommendation logic."""
    
    def test_chest_pain_high_severity(self):
        profile = get_triage_recommendation(
            chief_complaint="chest pain",
            severity=5
        )
        assert profile.recommended_sort == "detail_avg_time_in_ed_minutes"
        assert profile.urgency_level == 5
        assert "chest pain" in profile.explanation.lower()
    
    def test_chest_pain_low_severity(self):
        profile = get_triage_recommendation(
            chief_complaint="chest pain",
            severity=2
        )
        # Should balance quality and time
        assert profile.recommended_sort in ["adjusted_quality_points", "detail_avg_time_in_ed_minutes"]
        assert profile.urgency_level >= 2
    
    def test_stroke_urgent(self):
        profile = get_triage_recommendation(
            chief_complaint="stroke symptoms",
            severity=4
        )
        assert profile.recommended_sort == "detail_avg_time_in_ed_minutes"
        assert profile.urgency_level >= 4
    
    def test_low_severity_stable(self):
        profile = get_triage_recommendation(
            chief_complaint="minor cut",
            severity=1
        )
        # Should prefer rating for low severity
        assert profile.urgency_level <= 2
    
    def test_critical_vitals(self):
        vitals = VitalSigns(heart_rate=180, oxygen_saturation=85)
        profile = get_triage_recommendation(
            chief_complaint="general illness",
            severity=3,
            vital_signs=vitals
        )
        # Critical vitals should override severity
        assert profile.recommended_sort == "detail_avg_time_in_ed_minutes"
        assert profile.urgency_level == 5
    
    def test_pediatric_case(self):
        profile = get_triage_recommendation(
            chief_complaint="fever",
            severity=3,
            age=5
        )
        assert "Pediatric" in profile.explanation or "child" in profile.explanation.lower()
    
    def test_geriatric_case(self):
        profile = get_triage_recommendation(
            chief_complaint="fall",
            severity=3,
            age=75
        )
        assert "Geriatric" in profile.explanation or "elder" in profile.explanation.lower()


class TestTriageFromForm:
    """Test triage from form data."""
    
    def test_minimal_form(self):
        form_data = {
            "chief_complaint": "headache",
            "severity": 2
        }
        profile = triage_from_form(form_data)
        assert profile is not None
        assert profile.recommended_sort is not None
        assert profile.explanation is not None
    
    def test_full_form_with_vitals(self):
        form_data = {
            "chief_complaint": "chest pain",
            "severity": 4,
            "age": 55,
            "heart_rate": 110,
            "systolic_bp": 140,
            "oxygen_saturation": 94
        }
        profile = triage_from_form(form_data)
        assert profile.urgency_level >= 3
        assert profile.quality_column == "adj_total_heartattack"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

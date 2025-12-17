# modules/triage_ml.py
"""
ML-based triage module using synthetic/demo data.

⚠️ IMPORTANT: This model is trained on SYNTHETIC DATA for demonstration purposes only.
NOT for clinical use. Always consult medical professionals for actual triage decisions.

Features:
- Train RandomForest model on triage CSV data
- Predict triage level from patient features
- Handle missing values appropriately
- Provide feature importance explanations
- Save/load trained model
"""

import os
import pickle
import logging
from typing import Dict, Optional, Tuple, List
import warnings

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

logger = logging.getLogger(__name__)

# Suppress sklearn warnings
warnings.filterwarnings('ignore', category=UserWarning)

DEMO_WARNING = """
⚠️ DEMONSTRATION MODE ONLY ⚠️
This triage model is trained on SYNTHETIC/RESEARCH DATA and is NOT validated for clinical use.
Results are for demonstration purposes only. Always consult qualified medical professionals 
for actual patient triage and medical decisions.
"""

MODEL_PATH = "models/triage_model.pkl"
ENCODERS_PATH = "models/triage_encoders.pkl"


class TriageMLModel:
    """
    ML-based triage level predictor.
    
    Uses RandomForest classifier to predict triage urgency level (1-5)
    based on patient demographics, chief complaint, vitals, and arrival mode.
    """
    
    def __init__(self, demo_mode: bool = True):
        """
        Initialize the triage model.
        
        Args:
            demo_mode: If True, display warnings about synthetic data
        """
        self.demo_mode = demo_mode
        self.model: Optional[RandomForestClassifier] = None
        self.feature_names: List[str] = []
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.feature_importance: Optional[pd.Series] = None
        
        if demo_mode:
            logger.warning(DEMO_WARNING)
    
    def train(self, data_path: str) -> Dict:
        """
        Train the triage model on data from CSV file.
        
        Args:
            data_path: Path to triage CSV file
        
        Returns:
            Dictionary with training metrics
        """
        logger.info("Loading triage data from: %s", data_path)
        
        # Load data (semicolon-separated) with encoding handling
        try:
            df = pd.read_csv(data_path, sep=';', encoding='utf-8')
        except UnicodeDecodeError:
            logger.warning("UTF-8 decoding failed, trying latin-1 encoding")
            df = pd.read_csv(data_path, sep=';', encoding='latin-1')
        
        logger.info("Loaded %d records with %d columns", len(df), len(df.columns))
        
        # Feature engineering
        features_df = self._prepare_features(df)
        
        # Target variable: KTAS_expert (triage level)
        if 'KTAS_expert' not in df.columns:
            raise ValueError("Missing target column 'KTAS_expert' in training data")
        
        y = df['KTAS_expert'].values
        X = features_df.values
        self.feature_names = list(features_df.columns)
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info("Training set: %d samples, Test set: %d samples", len(X_train), len(X_test))
        
        # Train RandomForest model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        )
        
        logger.info("Training RandomForest model...")
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info("Training complete. Test accuracy: %.3f", accuracy)
        logger.info("\nClassification Report:\n%s", classification_report(y_test, y_pred))
        
        # Feature importance
        self.feature_importance = pd.Series(
            self.model.feature_importances_,
            index=self.feature_names
        ).sort_values(ascending=False)
        
        logger.info("\nTop 5 Most Important Features:")
        for feat, imp in self.feature_importance.head(5).items():
            logger.info("  %s: %.4f", feat, imp)
        
        return {
            "accuracy": float(accuracy),
            "n_train": len(X_train),
            "n_test": len(X_test),
            "n_features": len(self.feature_names),
            "feature_importance": self.feature_importance.to_dict()
        }
    
    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features from raw data with proper encoding and missing value handling.
        
        Args:
            df: Raw dataframe with patient data
        
        Returns:
            Feature dataframe ready for model training/prediction
        """
        features = pd.DataFrame()
        
        # Age (numeric)
        if 'Age' in df.columns:
            features['age'] = df['Age'].fillna(df['Age'].median())
        
        # Sex (binary: 1=male, 2=female)
        if 'Sex' in df.columns:
            features['sex'] = df['Sex'].fillna(1).astype(int)
        
        # Arrival mode (categorical)
        if 'Arrival mode' in df.columns:
            arrival_data = df['Arrival mode'].fillna(3).astype(str)
            arrival_le = self._get_or_create_encoder('arrival_mode', arrival_data)
            features['arrival_mode'] = arrival_le.transform(arrival_data)
        
        # Injury indicator (binary)
        if 'Injury' in df.columns:
            features['injury'] = df['Injury'].fillna(2).astype(int)
        
        # Chief complaint (categorical - encode top complaints)
        if 'Chief_complain' in df.columns:
            # Simplify chief complaints into categories
            complaints = df['Chief_complain'].fillna('other').astype(str).str.lower()
            features['complaint_chest'] = complaints.str.contains('chest|cardiac|heart', na=False).astype(int)
            features['complaint_respiratory'] = complaints.str.contains('breath|respiratory|cough|fever', na=False).astype(int)
            features['complaint_neuro'] = complaints.str.contains('head|neuro|dizz|stroke', na=False).astype(int)
            features['complaint_abdominal'] = complaints.str.contains('abd|stomach|nausea', na=False).astype(int)
            features['complaint_pain'] = complaints.str.contains('pain', na=False).astype(int)
        
        # Mental status (categorical)
        if 'Mental' in df.columns:
            features['mental_status'] = df['Mental'].fillna(1).astype(int)
        
        # Pain indicator (binary)
        if 'Pain' in df.columns:
            features['has_pain'] = df['Pain'].fillna(1).astype(int)
        
        # NRS pain scale (numeric 0-10)
        if 'NRS_pain' in df.columns:
            features['nrs_pain'] = pd.to_numeric(df['NRS_pain'], errors='coerce').fillna(0)
        
        # Vital signs (numeric) - use pd.to_numeric with errors='coerce' for robust conversion
        if 'SBP' in df.columns:
            features['systolic_bp'] = pd.to_numeric(df['SBP'], errors='coerce').fillna(120)
        if 'DBP' in df.columns:
            features['diastolic_bp'] = pd.to_numeric(df['DBP'], errors='coerce').fillna(80)
        if 'HR' in df.columns:
            features['heart_rate'] = pd.to_numeric(df['HR'], errors='coerce').fillna(80)
        if 'RR' in df.columns:
            features['respiratory_rate'] = pd.to_numeric(df['RR'], errors='coerce').fillna(18)
        if 'BT' in df.columns:
            features['body_temp'] = pd.to_numeric(df['BT'], errors='coerce').fillna(36.5)
        if 'Saturation' in df.columns:
            features['o2_saturation'] = pd.to_numeric(df['Saturation'], errors='coerce').fillna(98)
        
        # Derived features
        if 'systolic_bp' in features.columns and 'diastolic_bp' in features.columns:
            features['pulse_pressure'] = features['systolic_bp'] - features['diastolic_bp']
        
        if 'age' in features.columns:
            features['age_band_child'] = (features['age'] < 18).astype(int)
            features['age_band_senior'] = (features['age'] >= 65).astype(int)
        
        # Abnormal vitals flags
        if 'heart_rate' in features.columns:
            features['hr_abnormal'] = ((features['heart_rate'] < 50) | (features['heart_rate'] > 120)).astype(int)
        if 'systolic_bp' in features.columns:
            features['bp_abnormal'] = ((features['systolic_bp'] < 100) | (features['systolic_bp'] > 160)).astype(int)
        if 'o2_saturation' in features.columns:
            features['o2_low'] = (features['o2_saturation'] < 94).astype(int)
        
        return features
    
    def _get_or_create_encoder(self, name: str, data: pd.Series) -> LabelEncoder:
        """Get existing encoder or create new one."""
        if name not in self.label_encoders:
            le = LabelEncoder()
            le.fit(data.fillna('unknown').astype(str))
            self.label_encoders[name] = le
        return self.label_encoders[name]
    
    def predict(self, patient_data: Dict) -> Tuple[int, float, str]:
        """
        Predict triage level for a patient.
        
        Args:
            patient_data: Dictionary with patient features
        
        Returns:
            Tuple of (predicted_level, confidence, explanation)
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first or load() existing model.")
        
        # Convert dict to DataFrame for feature preparation
        df = pd.DataFrame([patient_data])
        features_df = self._prepare_features(df)
        
        # Ensure all training features are present
        for feat in self.feature_names:
            if feat not in features_df.columns:
                features_df[feat] = 0  # Default value for missing features
        
        # Reorder to match training
        features_df = features_df[self.feature_names]
        
        # Predict
        X = features_df.values
        prediction = self.model.predict(X)[0]
        proba = self.model.predict_proba(X)[0]
        confidence = float(proba.max())
        
        # Generate explanation
        explanation = self._generate_explanation(patient_data, int(prediction), confidence)
        
        return int(prediction), confidence, explanation
    
    def _generate_explanation(self, patient_data: Dict, prediction: int, confidence: float) -> str:
        """Generate human-readable explanation for prediction."""
        urgency_map = {
            1: "Resuscitation - Immediate",
            2: "Emergent - Within 10 min",
            3: "Urgent - Within 30 min",
            4: "Less Urgent - Within 60 min",
            5: "Non-Urgent - Within 120 min"
        }
        
        urgency_label = urgency_map.get(prediction, f"Level {prediction}")
        
        explanation = f"ML Model Prediction: {urgency_label} (confidence: {confidence:.2%})\n"
        
        # Key contributing factors
        if self.feature_importance is not None:
            explanation += "\nKey factors considered: "
            top_features = self.feature_importance.head(3).index.tolist()
            explanation += ", ".join(top_features)
        
        # Warning
        if self.demo_mode:
            explanation += f"\n\n{DEMO_WARNING}"
        
        return explanation
    
    def save(self, model_path: Optional[str] = None, encoders_path: Optional[str] = None):
        """Save trained model and encoders to disk."""
        model_path = model_path or MODEL_PATH
        encoders_path = encoders_path or ENCODERS_PATH
        
        # Create directory if needed
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'feature_names': self.feature_names,
                'feature_importance': self.feature_importance,
                'demo_mode': self.demo_mode
            }, f)
        logger.info("Model saved to: %s", model_path)
        
        # Save encoders
        with open(encoders_path, 'wb') as f:
            pickle.dump(self.label_encoders, f)
        logger.info("Encoders saved to: %s", encoders_path)
    
    def load(self, model_path: Optional[str] = None, encoders_path: Optional[str] = None):
        """Load trained model and encoders from disk."""
        model_path = model_path or MODEL_PATH
        encoders_path = encoders_path or ENCODERS_PATH
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load model
        with open(model_path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.feature_names = data['feature_names']
            self.feature_importance = data.get('feature_importance')
            self.demo_mode = data.get('demo_mode', True)
        logger.info("Model loaded from: %s", model_path)
        
        # Load encoders if available
        if os.path.exists(encoders_path):
            with open(encoders_path, 'rb') as f:
                self.label_encoders = pickle.load(f)
            logger.info("Encoders loaded from: %s", encoders_path)


def train_triage_model(data_path: str, save_model: bool = True) -> TriageMLModel:
    """
    Convenience function to train and optionally save triage model.
    
    Args:
        data_path: Path to training data CSV
        save_model: Whether to save trained model to disk
    
    Returns:
        Trained TriageMLModel instance
    """
    model = TriageMLModel(demo_mode=True)
    metrics = model.train(data_path)
    
    if save_model:
        model.save()
    
    logger.info("Training metrics: %s", metrics)
    return model


def load_triage_model() -> Optional[TriageMLModel]:
    """
    Load pre-trained triage model if available.
    
    Returns:
        Trained TriageMLModel instance or None if not found
    """
    if not os.path.exists(MODEL_PATH):
        logger.warning("No trained model found at: %s", MODEL_PATH)
        return None
    
    model = TriageMLModel(demo_mode=True)
    model.load()
    return model

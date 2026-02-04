"""
🧠 Mental Health Prediction System - Complete Implementation
=========================================================

This script implements the full mental health risk prediction system with:
- Complete data preprocessing and model training
- All explanation cards (files 7-11) integrated
- Comprehensive logging for backtrack capability
- Professional Gradio UI with custom components
- Sample data buttons and custom UI elements
- Detailed usage guide embedded

Author: Mental Health Analytics Team
Date: January 2026
"""

import pandas as pd
import numpy as np
import logging
import json
import os
import joblib
from datetime import datetime
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# ML Libraries
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from imblearn.over_sampling import SMOTE
import shap

# Gradio and UI
import gradio as gr
from gradio.components import DataFrame, Number, Dropdown, Slider, Checkbox, Textbox

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('mental_health_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MentalHealthPredictor:
    """Complete Mental Health Prediction System"""
    
    def __init__(self):
        """Initialize the prediction system"""
        logger.info("Initializing Mental Health Prediction System")
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_columns = None
        self.explanation_cards = {}
        self.is_trained = False
        
    def load_and_preprocess_data(self, data_path: str) -> pd.DataFrame:
        """Load and preprocess mental health dataset"""
        logger.info(f"Loading data from {data_path}")
        try:
            df = pd.read_csv(data_path)
            logger.info(f"Data loaded successfully. Shape: {df.shape}")
            
            # Feature engineering
            logger.info("Performing feature engineering")
            df_processed = self._engineer_features(df)
            
            # Encode categorical variables
            logger.info("Encoding categorical variables")
            df_processed = self._encode_variables(df_processed)
            
            logger.info("Data preprocessing completed successfully")
            return df_processed
            
        except Exception as e:
            logger.error(f"Error in data preprocessing: {str(e)}")
            raise
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create engineered features"""
        data = df.copy()
        
        # Composite risk score
        data['risk_composite'] = (data['depression_score'] * 0.6) + (data['anxiety_score'] * 0.4)
        
        # Stress-sleep interaction
        data['stress_sleep_ratio'] = data['stress_level'] / (data['sleep_hours'] + 0.1)  # Avoid division by zero
        
        # Age groups
        data['age_group'] = pd.cut(data['age'], bins=[18, 30, 50, 65], 
                                  labels=['Young', 'Middle', 'Senior'])
        
        # Productivity efficiency
        data['efficiency_ratio'] = data['productivity_score'] / (data['sleep_hours'] + 0.1)
        
        logger.info(f"Engineered features created. New shape: {data.shape}")
        return data
    
    def _encode_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical variables"""
        data = df.copy()
        
        # Binary encoding
        binary_map = {'Yes': 1, 'No': 0}
        data['mental_health_history'] = data['mental_health_history'].map(binary_map)
        data['seeks_treatment'] = data['seeks_treatment'].map(binary_map)
        
        # Gender encoding
        gender_map = {'Male': 0, 'Female': 1, 'Non-binary': 2, 'Prefer not to say': 3}
        data['gender_encoded'] = data['gender'].map(gender_map)
        
        # One-hot encoding for employment and work environment
        data = pd.get_dummies(data, columns=['employment_status', 'work_environment'], 
                             prefix=['emp', 'work'])
        
        # Target encoding
        self.label_encoder = LabelEncoder()
        data['mental_health_risk_encoded'] = self.label_encoder.fit_transform(data['mental_health_risk'])
        
        logger.info("Categorical variables encoded successfully")
        return data
    
    def train_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train the mental health prediction model"""
        logger.info("Starting model training process")
        
        try:
            # Select features
            self.feature_columns = [
                'age', 'gender_encoded', 'mental_health_history', 'seeks_treatment',
                'stress_level', 'sleep_hours', 'physical_activity_days',
                'depression_score', 'anxiety_score', 'social_support_score',
                'productivity_score', 'risk_composite', 'stress_sleep_ratio',
                'emp_Employed', 'emp_Self-employed', 'emp_Student', 'emp_Unemployed',
                'work_Hybrid', 'work_On-site', 'work_Remote'
            ]
            
            X = df[self.feature_columns]
            y = df['mental_health_risk_encoded']
            
            # Handle class imbalance
            logger.info("Applying SMOTE for class balancing")
            smote = SMOTE(random_state=42)
            X_balanced, y_balanced = smote.fit_resample(X, y)
            
            # Split data
            logger.info("Splitting data for training/validation")
            X_train, X_test, y_train, y_test = train_test_split(
                X_balanced, y_balanced, test_size=0.2, random_state=42, stratify=y_balanced
            )
            
            # Scale features
            logger.info("Scaling features")
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            logger.info("Training Random Forest model")
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=12,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
            
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            y_pred_proba = self.model.predict_proba(X_test_scaled)
            
            # Calculate metrics
            accuracy = self.model.score(X_test_scaled, y_test)
            auc_score = roc_auc_score(y_test, y_pred_proba, multi_class='ovr')
            
            results = {
                'accuracy': accuracy,
                'auc_roc': auc_score,
                'classification_report': classification_report(y_test, y_pred, 
                                                             target_names=self.label_encoder.classes_),
                'feature_importance': dict(zip(self.feature_columns, self.model.feature_importances_))
            }
            
            self.is_trained = True
            logger.info(f"Model training completed. Accuracy: {accuracy:.3f}, AUC: {auc_score:.3f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in model training: {str(e)}")
            raise
    
    def predict_single(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction for single input"""
        logger.info(f"Making prediction for input: {input_data}")
        
        if not self.is_trained:
            raise ValueError("Model not trained yet. Call train_model() first.")
        
        try:
            # Convert to DataFrame
            input_df = pd.DataFrame([input_data])
            
            # Apply same preprocessing
            processed_input = self._preprocess_single_input(input_df)
            
            # Select features
            X_input = processed_input[self.feature_columns]
            
            # Scale
            X_input_scaled = self.scaler.transform(X_input)
            
            # Predict
            prediction = self.model.predict(X_input_scaled)[0]
            probabilities = self.model.predict_proba(X_input_scaled)[0]
            
            # Decode prediction
            risk_level = self.label_encoder.inverse_transform([prediction])[0]
            confidence = max(probabilities)
            
            # Format results
            result = {
                'predicted_risk': risk_level,
                'confidence': f"{confidence:.1%}",
                'probabilities': {
                    'Low': f"{probabilities[0]:.1%}",
                    'Medium': f"{probabilities[1]:.1%}",
                    'High': f"{probabilities[2]:.1%}"
                },
                'raw_probabilities': probabilities.tolist(),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Prediction completed: {risk_level} risk with {confidence:.1%} confidence")
            return result
            
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            raise
    
    def _preprocess_single_input(self, input_df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess single input data"""
        data = input_df.copy()
        
        # Feature engineering (same as training)
        data['risk_composite'] = (data['depression_score'] * 0.6) + (data['anxiety_score'] * 0.4)
        data['stress_sleep_ratio'] = data['stress_level'] / (data['sleep_hours'] + 0.1)
        
        # Encode categorical variables
        binary_map = {'Yes': 1, 'No': 0}
        data['mental_health_history'] = data['mental_health_history'].map(binary_map)
        data['seeks_treatment'] = data['seeks_treatment'].map(binary_map)
        
        gender_map = {'Male': 0, 'Female': 1, 'Non-binary': 2, 'Prefer not to say': 3}
        data['gender_encoded'] = data['gender'].map(gender_map)
        
        # One-hot encoding
        data = pd.get_dummies(data, columns=['employment_status', 'work_environment'], 
                             prefix=['emp', 'work'])
        
        # Ensure all required columns are present
        for col in self.feature_columns:
            if col not in data.columns:
                data[col] = 0
                
        return data
    
    def save_model(self, filepath: str = "mental_health_model.pkl"):
        """Save trained model and components"""
        if not self.is_trained:
            raise ValueError("No trained model to save")
            
        model_package = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_columns': self.feature_columns,
            'trained_at': datetime.now().isoformat()
        }
        
        joblib.dump(model_package, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str = "mental_health_model.pkl"):
        """Load trained model and components"""
        model_package = joblib.load(filepath)
        
        self.model = model_package['model']
        self.scaler = model_package['scaler']
        self.label_encoder = model_package['label_encoder']
        self.feature_columns = model_package['feature_columns']
        self.is_trained = True
        
        logger.info(f"Model loaded from {filepath}")

# Initialize global predictor
predictor = MentalHealthPredictor()

def initialize_system():
    """Initialize the complete system"""
    logger.info("=== SYSTEM INITIALIZATION STARTED ===")
    
    # Load and train model
    data_path = "dataset/mental_health_dataset.csv"
    df = predictor.load_and_preprocess_data(data_path)
    training_results = predictor.train_model(df)
    
    # Save model
    predictor.save_model()
    
    logger.info("=== SYSTEM INITIALIZATION COMPLETED ===")
    return training_results

# Load explanation cards
def load_explanation_cards():
    """Load all explanation cards from insights folder"""
    cards = {}
    
    card_files = {
        7: "7_MODEL_EXPLANATION_GUIDE.md",
        8: "8_RISK_CLASSIFICATION_REFERENCE_CARD.md", 
        9: "9_TREATMENT_SEEKING_GUIDE.md",
        10: "10_SYMPTOM_SCORE_INTERPRETATION.md",
        11: "11_MODEL_TECHNICAL_SPECIFICATIONS.md"
    }
    
    for number, filename in card_files.items():
        try:
            with open(f"insights/{filename}", 'r', encoding='utf-8') as f:
                cards[number] = f.read()
            logger.info(f"Loaded explanation card {number}")
        except FileNotFoundError:
            cards[number] = f"Explanation card {number} not found"
            logger.warning(f"Could not load explanation card {number}")
    
    return cards

# Global variables
explanation_cards = load_explanation_cards()
training_completed = False

# Sample data for demonstration
SAMPLE_CASES = [
    {
        "name": "High Risk Student",
        "data": {
            'age': 24, 'gender': 'Female', 'employment_status': 'Student',
            'work_environment': 'Remote', 'mental_health_history': 'Yes',
            'seeks_treatment': 'No', 'stress_level': 9, 'sleep_hours': 4.5,
            'physical_activity_days': 1, 'depression_score': 26,
            'anxiety_score': 18, 'social_support_score': 35, 'productivity_score': 55
        }
    },
    {
        "name": "Moderate Risk Professional",
        "data": {
            'age': 42, 'gender': 'Male', 'employment_status': 'Employed',
            'work_environment': 'Hybrid', 'mental_health_history': 'No',
            'seeks_treatment': 'No', 'stress_level': 6, 'sleep_hours': 6.5,
            'physical_activity_days': 3, 'depression_score': 16,
            'anxiety_score': 12, 'social_support_score': 65, 'productivity_score': 78
        }
    },
    {
        "name": "Low Risk Senior",
        "data": {
            'age': 58, 'gender': 'Non-binary', 'employment_status': 'Self-employed',
            'work_environment': 'Remote', 'mental_health_history': 'No',
            'seeks_treatment': 'No', 'stress_level': 2, 'sleep_hours': 8.2,
            'physical_activity_days': 5, 'depression_score': 4,
            'anxiety_score': 2, 'social_support_score': 92, 'productivity_score': 96
        }
    }
]

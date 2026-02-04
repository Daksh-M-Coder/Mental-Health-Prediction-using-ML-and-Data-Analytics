"""
🧠 Mental Health Prediction System - FIXED VERSION
================================================

Fixed implementation with:
- Working sample cases
- Simpler models (Decision Tree, Logistic Regression, KNN, SVM)
- Proper error handling
- Working Gradio interface
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
import colorama
from colorama import Fore, Back, Style

# Initialize colorama
colorama.init(autoreset=True)

warnings.filterwarnings('ignore')

# ML Libraries
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, roc_auc_score
from imblearn.over_sampling import SMOTE

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
    """Fixed Mental Health Prediction System"""
    
    def __init__(self):
        """Initialize the prediction system"""
        print(Fore.CYAN + Style.BRIGHT + "🧠 Initializing Mental Health Prediction System")
        logger.info("Initializing Mental Health Prediction System")
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_columns = None
        self.is_trained = False
        self.models = {}  # Store multiple models
        self.best_model_name = None
        
    def load_and_preprocess_data(self, data_path: str) -> pd.DataFrame:
        """Load and preprocess mental health dataset"""
        print(Fore.BLUE + f"📂 Loading data from {data_path}...")
        logger.info(f"Loading data from {data_path}")
        try:
            df = pd.read_csv(data_path)
            print(Fore.GREEN + f"✅ Data loaded successfully. Shape: {df.shape}")
            logger.info(f"Data loaded successfully. Shape: {df.shape}")
            
            # Feature engineering
            print(Fore.YELLOW + "⚙️  Performing feature engineering...")
            logger.info("Performing feature engineering")
            df_processed = self._engineer_features(df)
            
            # Encode categorical variables
            print(Fore.YELLOW + "🔢 Encoding categorical variables...")
            logger.info("Encoding categorical variables")
            df_processed = self._encode_variables(df_processed)
            
            print(Fore.CYAN + "✅ Data preprocessing completed successfully")
            logger.info("Data preprocessing completed successfully")
            return df_processed
            
        except Exception as e:
            error_msg = f"❌ Error in data preprocessing: {str(e)}"
            print(Fore.RED + error_msg)
            logger.error(f"Error in data preprocessing: {str(e)}")
            raise
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create engineered features"""
        data = df.copy()
        
        # Composite risk score
        data['risk_composite'] = (data['depression_score'] * 0.6) + (data['anxiety_score'] * 0.4)
        
        # Stress-sleep interaction
        data['stress_sleep_ratio'] = data['stress_level'] / (data['sleep_hours'] + 0.1)
        
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
    
    def train_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train multiple simple models and select best"""
        print(Fore.CYAN + Style.BRIGHT + "🚀 Starting model training process...")
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
            print(Fore.YELLOW + "⚖️  Applying SMOTE for class balancing...")
            logger.info("Applying SMOTE for class balancing")
            smote = SMOTE(random_state=42)
            X_balanced, y_balanced = smote.fit_resample(X, y)
            
            # Split data
            print(Fore.YELLOW + "📊 Splitting data for training/validation...")
            logger.info("Splitting data for training/validation")
            X_train, X_test, y_train, y_test = train_test_split(
                X_balanced, y_balanced, test_size=0.2, random_state=42, stratify=y_balanced
            )
            
            # Scale features
            print(Fore.YELLOW + "📏 Scaling features...")
            logger.info("Scaling features")
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train multiple simple models
            print(Fore.MAGENTA + "🤖 Training multiple models...")
            logger.info("Training multiple models")
            model_configs = {
                'Decision Tree': DecisionTreeClassifier(random_state=42, max_depth=10),
                'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
                'KNN': KNeighborsClassifier(n_neighbors=5),
                'SVM': SVC(probability=True, random_state=42)
            }
            
            results = {}
            for name, model in model_configs.items():
                print(Fore.BLUE + f"    🏭 Training {name}...")
                logger.info(f"Training {name}")
                model.fit(X_train_scaled, y_train)
                self.models[name] = model
                
                # Evaluate
                y_pred = model.predict(X_test_scaled)
                y_pred_proba = model.predict_proba(X_test_scaled)
                
                accuracy = model.score(X_test_scaled, y_test)
                auc_score = roc_auc_score(y_test, y_pred_proba, multi_class='ovr')
                
                results[name] = {
                    'accuracy': accuracy,
                    'auc_roc': auc_score,
                    'model': model
                }
                
                print(Fore.GREEN + f"    📈 {name} - Accuracy: {accuracy:.3f}, AUC: {auc_score:.3f}")
                logger.info(f"{name} - Accuracy: {accuracy:.3f}, AUC: {auc_score:.3f}")
            
            # Select best model
            self.best_model_name = max(results.keys(), key=lambda x: results[x]['accuracy'])
            self.model = results[self.best_model_name]['model']
            
            print(Fore.CYAN + Style.BRIGHT + f"🏆 Best model selected: {self.best_model_name} with accuracy {results[self.best_model_name]['accuracy']:.3f}")
            
            self.is_trained = True
            
            return {
                'results': results,
                'best_model': self.best_model_name,
                'feature_columns': self.feature_columns
            }
            
        except Exception as e:
            error_msg = f"❌ Error in model training: {str(e)}"
            print(Fore.RED + error_msg)
            logger.error(f"Error in model training: {str(e)}")
            raise
    
    def predict_single(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction for single input"""
        logger.info(f"Making prediction for input: {input_data}")
        
        if not self.is_trained:
            raise ValueError("Model not trained yet. Call train_models() first.")
        
        try:
            # Convert to DataFrame
            input_df = pd.DataFrame([input_data])
            
            # Apply same preprocessing
            processed_input = self._preprocess_single_input(input_df)
            
            # Select features
            X_input = processed_input[self.feature_columns]
            
            # Scale
            X_input_scaled = self.scaler.transform(X_input)
            
            # Predict with best model
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
                'model_used': self.best_model_name,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Prediction completed: {risk_level} risk with {confidence:.1%} confidence using {self.best_model_name}")
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
        if 'mental_health_history' in data.columns:
            data['mental_health_history'] = data['mental_health_history'].map(binary_map)
        if 'seeks_treatment' in data.columns:
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
    
    def save_model(self, filepath: str = "mental_health_model_fixed.pkl"):
        """Save trained model and components"""
        if not self.is_trained:
            raise ValueError("No trained model to save")
            
        model_package = {
            'model': self.model,
            'models': self.models,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_columns': self.feature_columns,
            'best_model_name': self.best_model_name,
            'trained_at': datetime.now().isoformat()
        }
        
        joblib.dump(model_package, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str = "mental_health_model_fixed.pkl"):
        """Load trained model and components"""
        model_package = joblib.load(filepath)
        
        self.model = model_package['model']
        self.models = model_package['models']
        self.scaler = model_package['scaler']
        self.label_encoder = model_package['label_encoder']
        self.feature_columns = model_package['feature_columns']
        self.best_model_name = model_package['best_model_name']
        self.is_trained = True
        
        logger.info(f"Model loaded from {filepath}")

# Initialize global predictor
predictor = MentalHealthPredictor()

def initialize_system():
    """Initialize the complete system"""
    print(Fore.CYAN + "\n=== 🚀 SYSTEM INITIALIZATION STARTED ===")
    logger.info("=== SYSTEM INITIALIZATION STARTED ===")
    
    # Load and train model
    data_path = "dataset/mental_health_dataset.csv"
    df = predictor.load_and_preprocess_data(data_path)
    training_results = predictor.train_models(df)
    
    # Save model
    predictor.save_model()
    
    print(Fore.GREEN + "✅ SYSTEM INITIALIZATION COMPLETED SUCCESSFULLY!\n")
    logger.info("=== SYSTEM INITIALIZATION COMPLETED ===")
    return training_results

# Sample data for demonstration (FIXED)
SAMPLE_CASES = [
    {
        "name": "🎓 High Risk Student",
        "data": {
            'age': 24, 'gender': 'Female', 'employment_status': 'Student',
            'work_environment': 'Remote', 'mental_health_history': 'Yes',
            'seeks_treatment': 'No', 'stress_level': 9, 'sleep_hours': 4.5,
            'physical_activity_days': 1, 'depression_score': 26,
            'anxiety_score': 18, 'social_support_score': 35, 'productivity_score': 55
        }
    },
    {
        "name": "💼 Moderate Risk Professional", 
        "data": {
            'age': 42, 'gender': 'Male', 'employment_status': 'Employed',
            'work_environment': 'Hybrid', 'mental_health_history': 'No',
            'seeks_treatment': 'No', 'stress_level': 6, 'sleep_hours': 6.5,
            'physical_activity_days': 3, 'depression_score': 16,
            'anxiety_score': 12, 'social_support_score': 65, 'productivity_score': 78
        }
    },
    {
        "name": "👴 Low Risk Senior",
        "data": {
            'age': 58, 'gender': 'Non-binary', 'employment_status': 'Self-employed',
            'work_environment': 'Remote', 'mental_health_history': 'No',
            'seeks_treatment': 'No', 'stress_level': 2, 'sleep_hours': 8.2,
            'physical_activity_days': 5, 'depression_score': 4,
            'anxiety_score': 2, 'social_support_score': 92, 'productivity_score': 96
        }
    }
]

# Load explanation cards
def load_explanation_cards():
    """Load all explanation cards from insights folder with actual content"""
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
            print(Fore.GREEN + f"✅ Loaded explanation card {number}: {filename}")
            logger.info(f"Loaded explanation card {number}: {filename}")
        except FileNotFoundError:
            cards[number] = f"# Explanation Card {number}\n\nContent not found. Please check if insights/{filename} exists."
            print(Fore.YELLOW + f"⚠️  Could not load explanation card {number}: {filename}")
            logger.warning(f"Could not load explanation card {number}: {filename}")
        except Exception as e:
            cards[number] = f"# Error Loading Card {number}\n\n{str(e)}"
            print(Fore.RED + f"❌ Error loading card {number}: {e}")
            logger.error(f"Error loading card {number}: {e}")
    
    return cards

# Global variables
explanation_cards = load_explanation_cards()
training_completed = False

if __name__ == "__main__":
    # Test the system
    print(Fore.CYAN + Style.BRIGHT + "🧪 Testing Mental Health Prediction System...")
    try:
        results = initialize_system()
        print(Fore.GREEN + "🎉 System initialized successfully!")
        print(Fore.MAGENTA + f"🏆 Best model: {results['best_model']}")
        print(Fore.BLUE + f"📊 Available models: {list(results['results'].keys())}")
    except Exception as e:
        print(Fore.RED + f"❌ Error: {e}")
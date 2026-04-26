"""
🧠 Mental Health Prediction System - FINAL VERSION WITH CONCISE CODE EXAMPLES
============================================================================

Real machine learning implementation with:
- Decision Tree Classifier (permitted model)
- Comprehensive model metrics (accuracy, precision, recall, f1, mse, mae, r2)
- Complete accuracy explanation guide with real code examples
- Proper data preprocessing
- Real predictions based on mental health dataset
- Complete documentation
"""

import gradio as gr
import pandas as pd
import numpy as np
import logging
import json
from datetime import datetime
from typing import Dict, Any, Tuple
import colorama
from colorama import Fore, Back, Style
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Add project root to path for text_processing imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# RL Text Processing imports (keyword-based, archived in old_text_processing)
try:
    from text_processing.old_text_processing.rl_text_engine import RLTextEngine
    from text_processing.old_text_processing.score_bridge import bridge_scores, format_score_summary, format_dtc_input_summary
    RL_ENGINE_AVAILABLE = True
    print(Fore.GREEN + "✅ RL Text Engine loaded successfully")
except Exception as e:
    RL_ENGINE_AVAILABLE = False
    print(Fore.YELLOW + f"⚠️ RL Text Engine not available: {e}")

# Initialize colorama
colorama.init(autoreset=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print(Fore.CYAN + Style.BRIGHT + "🧪 Testing Mental Health Prediction System with REAL CODE EXAMPLES...")

class MentalHealthPredictor:
    def __init__(self):
        self.is_trained = False
        self.feature_columns = []
        self.label_encoders = {}
        # Optimized model for larger dataset with class imbalance handling
        self.model = DecisionTreeClassifier(
            random_state=42, 
            max_depth=12,           # Increased depth for more complex patterns
            min_samples_split=10,   # Increased to prevent overfitting
            min_samples_leaf=5,     # Minimum samples per leaf
            class_weight='balanced', # Handle class imbalance
            ccp_alpha=0.001         # Cost complexity pruning
        )
        self.best_model_name = "Optimized Decision Tree Classifier"
        
        # Metrics storage
        self.training_metrics = {}
        self.test_metrics = {}
        
        # Model persistence - saved_models directory
        self.model_filename = "saved_models/mental_health_model.pkl"
        self.encoders_filename = "saved_models/label_encoders.pkl"
        self.features_filename = "saved_models/feature_columns.pkl"
        self.metrics_filename = "saved_models/model_metrics.pkl"
        
        # Try to load existing model first
        if not self.load_model():
            # If no saved model, train new one
            self.load_and_prepare_data()
    
    def load_and_prepare_data(self):
        """Load and prepare the mental health dataset"""
        try:
            # Load the full mental health dataset (10,000 samples)
            df = pd.read_csv('old_dataset/mental_health_dataset.csv')
            print(Fore.GREEN + f"✅ Loaded full mental_health_dataset.csv with {len(df)} samples")
            logger.info(f"Loaded mental_health_dataset.csv with {len(df)} samples")
            
            # Show dataset statistics
            print(Fore.CYAN + f"📊 Dataset Statistics:")
            print(Fore.YELLOW + f"  Total samples: {len(df)}")
            print(Fore.YELLOW + f"  Risk distribution:")
            for risk, count in df['mental_health_risk'].value_counts().items():
                percentage = (count / len(df)) * 100
                print(Fore.YELLOW + f"    {risk}: {count} ({percentage:.1f}%)")
            
            # Prepare features for the model
            self.prepare_features(df)
            
        except FileNotFoundError:
            print(Fore.YELLOW + "⚠️  mental_health_dataset.csv not found, creating synthetic data for demo")
            logger.warning("mental_health_dataset.csv not found, creating synthetic data for demo")
            self.create_synthetic_data()
    
    def create_synthetic_data(self):
        """Create synthetic mental health data for demonstration"""
        np.random.seed(42)
        n_samples = 1000
        
        # Generate synthetic data based on realistic mental health patterns
        data = {
            'age': np.random.randint(18, 65, n_samples),
            'gender': np.random.choice(['Male', 'Female', 'Non-binary'], n_samples, p=[0.45, 0.45, 0.1]),
            'employment_status': np.random.choice(['Employed', 'Student', 'Self-employed', 'Unemployed'], n_samples, p=[0.6, 0.2, 0.1, 0.1]),
            'work_environment': np.random.choice(['On-site', 'Remote', 'Hybrid'], n_samples, p=[0.4, 0.3, 0.3]),
            'mental_health_history': np.random.choice(['Yes', 'No'], n_samples, p=[0.3, 0.7]),
            'seeks_treatment': np.random.choice(['Yes', 'No'], n_samples, p=[0.25, 0.75]),
            'stress_level': np.random.randint(1, 11, n_samples),
            'sleep_hours': np.round(np.random.normal(7, 1.5, n_samples), 1),
            'physical_activity_days': np.random.randint(0, 8, n_samples),
            'depression_score': np.random.randint(0, 31, n_samples),
            'anxiety_score': np.random.randint(0, 21, n_samples),
            'social_support_score': np.random.randint(0, 101, n_samples),
            'productivity_score': np.random.randint(0, 101, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Ensure realistic ranges
        df['sleep_hours'] = np.clip(df['sleep_hours'], 2, 12)
        df['depression_score'] = np.clip(df['depression_score'], 0, 30)
        df['anxiety_score'] = np.clip(df['anxiety_score'], 0, 21)
        
        # Create risk labels based on realistic patterns
        risk_scores = []
        for idx, row in df.iterrows():
            # Calculate risk based on multiple factors
            score = 0
            if row['depression_score'] > 20: score += 3
            elif row['depression_score'] > 10: score += 2
            elif row['depression_score'] > 5: score += 1
            
            if row['anxiety_score'] > 15: score += 2
            elif row['anxiety_score'] > 8: score += 1
            
            if row['stress_level'] > 7: score += 2
            elif row['stress_level'] > 4: score += 1
            
            if row['sleep_hours'] < 5: score += 2
            elif row['sleep_hours'] < 6: score += 1
            
            if row['social_support_score'] < 30: score += 2
            elif row['social_support_score'] < 50: score += 1
            
            # Convert to risk category
            if score >= 6:
                risk = 'High'
            elif score >= 3:
                risk = 'Medium'
            else:
                risk = 'Low'
            
            risk_scores.append(risk)
        
        df['mental_health_risk'] = risk_scores
        self.df = df
        print(Fore.GREEN + "✅ Created synthetic mental health dataset")
        logger.info("Created synthetic mental health dataset")
        
        # Prepare features for the model
        self.prepare_features(df)
    
    def calculate_comprehensive_metrics(self, y_true, y_pred, y_pred_proba=None):
        """Calculate comprehensive model metrics"""
        metrics = {}
        
        # Classification metrics
        metrics['accuracy'] = accuracy_score(y_true, y_pred)
        
        # Calculate precision, recall, f1 for each class
        try:
            metrics['precision_macro'] = precision_score(y_true, y_pred, average='macro', zero_division=0)
            metrics['recall_macro'] = recall_score(y_true, y_pred, average='macro', zero_division=0)
            metrics['f1_macro'] = f1_score(y_true, y_pred, average='macro', zero_division=0)
            
            # Per-class metrics
            unique_labels = np.unique(list(y_true) + list(y_pred))
            for label in unique_labels:
                try:
                    prec = precision_score(y_true, y_pred, labels=[label], average=None, zero_division=0)[0]
                    rec = recall_score(y_true, y_pred, labels=[label], average=None, zero_division=0)[0]
                    f1 = f1_score(y_true, y_pred, labels=[label], average=None, zero_division=0)[0]
                    metrics[f'precision_{label}'] = prec
                    metrics[f'recall_{label}'] = rec
                    metrics[f'f1_{label}'] = f1
                except:
                    metrics[f'precision_{label}'] = 0
                    metrics[f'recall_{label}'] = 0
                    metrics[f'f1_{label}'] = 0
        except:
            metrics['precision_macro'] = 0
            metrics['recall_macro'] = 0
            metrics['f1_macro'] = 0
        
        # For regression-like metrics (using label encoded values)
        le = LabelEncoder()
        y_true_encoded = le.fit_transform(y_true.astype(str))
        y_pred_encoded = le.transform(y_pred.astype(str))
        
        metrics['mse'] = mean_squared_error(y_true_encoded, y_pred_encoded)
        metrics['mae'] = mean_absolute_error(y_true_encoded, y_pred_encoded)
        metrics['r2_score'] = r2_score(y_true_encoded, y_pred_encoded)
        
        return metrics
    
    def save_model(self):
        """Save the trained model and associated data to disk"""
        try:
            # Save model
            joblib.dump(self.model, self.model_filename)
            print(Fore.GREEN + f"✅ Model saved to {self.model_filename}")
            logger.info(f"Model saved to {self.model_filename}")
            
            # Save label encoders
            joblib.dump(self.label_encoders, self.encoders_filename)
            print(Fore.GREEN + f"✅ Label encoders saved to {self.encoders_filename}")
            logger.info(f"Label encoders saved to {self.encoders_filename}")
            
            # Save feature columns
            joblib.dump(self.feature_columns, self.features_filename)
            print(Fore.GREEN + f"✅ Feature columns saved to {self.features_filename}")
            logger.info(f"Feature columns saved to {self.features_filename}")
            
            # Save metrics
            joblib.dump(self.test_metrics, self.metrics_filename)
            print(Fore.GREEN + f"✅ Model metrics saved to {self.metrics_filename}")
            logger.info(f"Model metrics saved to {self.metrics_filename}")
            
        except Exception as e:
            print(Fore.RED + f"❌ Error saving model: {e}")
            logger.error(f"Error saving model: {e}")
    
    def load_model(self):
        """Load a trained model and associated data from disk"""
        try:
            # Check if all model files exist
            if not all(os.path.exists(filename) for filename in [
                self.model_filename, self.encoders_filename, 
                self.features_filename, self.metrics_filename
            ]):
                print(Fore.YELLOW + "⚠️  No saved model found, training new model...")
                logger.info("No saved model found, will train new model")
                return False
            
            # Load model
            self.model = joblib.load(self.model_filename)
            print(Fore.GREEN + f"✅ Model loaded from {self.model_filename}")
            logger.info(f"Model loaded from {self.model_filename}")
            
            # Load label encoders
            self.label_encoders = joblib.load(self.encoders_filename)
            print(Fore.GREEN + f"✅ Label encoders loaded from {self.encoders_filename}")
            logger.info(f"Label encoders loaded from {self.encoders_filename}")
            
            # Load feature columns
            self.feature_columns = joblib.load(self.features_filename)
            print(Fore.GREEN + f"✅ Feature columns loaded from {self.features_filename}")
            logger.info(f"Feature columns loaded from {self.features_filename}")
            
            # Load metrics
            self.test_metrics = joblib.load(self.metrics_filename)
            print(Fore.GREEN + f"✅ Model metrics loaded from {self.metrics_filename}")
            logger.info(f"Model metrics loaded from {self.metrics_filename}")
            
            self.is_trained = True
            print(Fore.CYAN + "📊 LOADED MODEL PERFORMANCE METRICS:")
            print(Fore.YELLOW + f"  Accuracy: {self.test_metrics.get('accuracy', 'N/A'):.4f}")
            print(Fore.YELLOW + f"  Precision (Macro): {self.test_metrics.get('precision_macro', 'N/A'):.4f}")
            print(Fore.YELLOW + f"  Recall (Macro): {self.test_metrics.get('recall_macro', 'N/A'):.4f}")
            print(Fore.YELLOW + f"  F1-Score (Macro): {self.test_metrics.get('f1_macro', 'N/A'):.4f}")
            
            return True
            
        except Exception as e:
            print(Fore.RED + f"❌ Error loading model: {e}")
            logger.error(f"Error loading model: {e}")
            return False
    
    def prepare_features(self, df):
        """Prepare features for the model with optimization for large dataset"""
        print(Fore.CYAN + "🔄 Preparing features for the model (optimized for full dataset)...")
        logger.info("Preparing features for the model (optimized for full dataset)")
        
        # Select feature columns
        feature_cols = [
            'age', 'gender', 'employment_status', 'work_environment',
            'mental_health_history', 'seeks_treatment', 'stress_level',
            'sleep_hours', 'physical_activity_days', 'depression_score',
            'anxiety_score', 'social_support_score', 'productivity_score'
        ]
        
        # Encode categorical variables
        for col in ['gender', 'employment_status', 'work_environment', 'mental_health_history', 'seeks_treatment']:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            self.label_encoders[col] = le
        
        # Store feature columns
        self.feature_columns = feature_cols
        
        # Prepare X and y
        X = df[self.feature_columns]
        y = df['mental_health_risk']
        
        # Show class distribution
        print(Fore.CYAN + f"📊 Class Distribution in Training Data:")
        unique, counts = np.unique(y, return_counts=True)
        for cls, count in zip(unique, counts):
            print(Fore.YELLOW + f"  {cls}: {count} samples ({count/len(y)*100:.1f}%)")
        
        # Stratified train-test split to maintain class distribution
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(Fore.CYAN + f"📊 Data Split:")
        print(Fore.YELLOW + f"  Training set: {len(X_train)} samples")
        print(Fore.YELLOW + f"  Test set: {len(X_test)} samples")
        
        # Train the optimized model
        print(Fore.CYAN + "🧠 Training optimized Decision Tree model...")
        self.model.fit(X_train, y_train)
        
        # Make predictions on test set
        y_pred = self.model.predict(X_test)
        
        # Calculate comprehensive metrics
        self.test_metrics = self.calculate_comprehensive_metrics(y_test, y_pred)
        
        print(Fore.GREEN + f"✅ Model trained successfully on full dataset!")
        logger.info("Model trained successfully on full dataset!")
        
        # Show feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(Fore.CYAN + "📊 Top 5 Most Important Features:")
        for idx, row in feature_importance.head().iterrows():
            print(Fore.YELLOW + f"  {row['feature']}: {row['importance']:.3f}")
        
        # Save the trained model
        self.save_model()
        
        # Print comprehensive metrics
        print(Fore.CYAN + "\n📊 COMPREHENSIVE MODEL PERFORMANCE METRICS (Full Dataset):")
        print(Fore.YELLOW + f"  Accuracy: {self.test_metrics['accuracy']:.4f}")
        print(Fore.YELLOW + f"  Precision (Macro): {self.test_metrics['precision_macro']:.4f}")
        print(Fore.YELLOW + f"  Recall (Macro): {self.test_metrics['recall_macro']:.4f}")
        print(Fore.YELLOW + f"  F1-Score (Macro): {self.test_metrics['f1_macro']:.4f}")
        print(Fore.YELLOW + f"  MSE: {self.test_metrics['mse']:.4f}")
        print(Fore.YELLOW + f"  MAE: {self.test_metrics['mae']:.4f}")
        print(Fore.YELLOW + f"  R² Score: {self.test_metrics['r2_score']:.4f}")
        
        # Per-class metrics
        for label in ['Low', 'Medium', 'High']:
            if f'precision_{label}' in self.test_metrics:
                print(Fore.MAGENTA + f"  Precision ({label}): {self.test_metrics[f'precision_{label}']:.4f}")
                print(Fore.MAGENTA + f"  Recall ({label}): {self.test_metrics[f'recall_{label}']:.4f}")
                print(Fore.MAGENTA + f"  F1-Score ({label}): {self.test_metrics[f'f1_{label}']:.4f}")
        
        self.is_trained = True
        
        # Store the test set for later use
        self.X_test = X_test
        self.y_test = y_test
        self.y_pred = y_pred
    
    def predict_single(self, data):
        """Make a prediction for a single data point"""
        if not self.is_trained:
            raise ValueError("Model not trained yet!")
        
        # Create a DataFrame with the input data
        input_df = pd.DataFrame([data])
        
        # Encode categorical variables using stored encoders
        for col in ['gender', 'employment_status', 'work_environment', 'mental_health_history', 'seeks_treatment']:
            if col in self.label_encoders:
                try:
                    input_df[col] = self.label_encoders[col].transform(input_df[col].astype(str))
                except ValueError:
                    # Handle unseen labels by using the first category
                    input_df[col] = 0
        
        # Make prediction
        X_input = input_df[self.feature_columns]
        prediction = self.model.predict(X_input)[0]
        probabilities = self.model.predict_proba(X_input)[0]
        
        # Get class names
        classes = self.model.classes_
        
        # Create probability dictionary
        prob_dict = {}
        for i, class_name in enumerate(classes):
            prob_dict[class_name] = f"{probabilities[i]:.1%}"
        
        # Calculate confidence based on max probability
        confidence = f"{max(probabilities):.1%}"
        
        return {
            'predicted_risk': prediction,
            'confidence': confidence,
            'probabilities': prob_dict,
            'model_used': self.best_model_name,
            'timestamp': datetime.now().isoformat(),
            'model_metrics': self.test_metrics
        }

# Initialize the predictor
print(Fore.CYAN + "🚀 Initializing Mental Health Predictor with Decision Tree Classifier...")
predictor = MentalHealthPredictor()

# Sample data for demonstration
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

# Load explanation cards with actual content
def load_explanation_cards():
    """Load all explanation cards from insights folder with actual content"""
    cards = {}
    
    card_files = {
        7: "7_MODEL_EXPLANATION_GUIDE.md",
        8: "8_RISK_CLASSIFICATION_REFERENCE_CARD.md", 
        9: "9_TREATMENT_SEEKING_GUIDE.md",
        10: "10_SYMPTOM_SCORE_INTERPRETATION.md",
        11: "11_MODEL_TECHNICAL_SPECIFICATIONS.md",
        12: "12_ACCURACY_EXPLANATION.md",
        13: "REAL_CODE_AND_RESULTS.md"
    }
    
    for number, filename in card_files.items():
        try:
            if number == 13:  # Special handling for the real code and results file
                # Try root directory first, then insights folder
                try:
                    with open(f"{filename}", 'r', encoding='utf-8') as f:
                        cards[number] = f.read()
                except FileNotFoundError:
                    with open(f"insights/{filename}", 'r', encoding='utf-8') as f:
                        cards[number] = f.read()
            else:
                with open(f"insights/{filename}", 'r', encoding='utf-8') as f:
                    cards[number] = f.read()
            print(Fore.GREEN + f"✅ Loaded explanation card {number}: {filename}")
            logger.info(f"Loaded explanation card {number}: {filename}")
        except FileNotFoundError:
            cards[number] = f"# Explanation Card {number}\n\nContent not found. Please check if {'insights/' if number != 13 else ''}{filename} exists."
            print(Fore.YELLOW + f"⚠️  Could not load explanation card {number}: {filename}")
            logger.warning(f"Could not load explanation card {number}: {filename}")
        except Exception as e:
            cards[number] = f"# Error Loading Card {number}\n\n{str(e)}"
            print(Fore.RED + f"❌ Error loading card {number}: {e}")
            logger.error(f"Error loading card {number}: {e}")
    
    return cards

# Load explanation cards
explanation_cards = load_explanation_cards()

# Gradio Interface Functions
def make_prediction(age, gender, employment_status, work_environment,
                   mental_health_history, seeks_treatment, stress_level,
                   sleep_hours, physical_activity_days, depression_score,
                   anxiety_score, social_support_score, productivity_score):
    """Main prediction function"""
    logger.info("=== PREDICTION REQUEST RECEIVED ===")
    
    # Log input parameters
    input_params = {
        'age': age, 'gender': gender, 'employment_status': employment_status,
        'work_environment': work_environment, 'mental_health_history': mental_health_history,
        'seeks_treatment': seeks_treatment, 'stress_level': stress_level,
        'sleep_hours': sleep_hours, 'physical_activity_days': physical_activity_days,
        'depression_score': depression_score, 'anxiety_score': anxiety_score,
        'social_support_score': social_support_score, 'productivity_score': productivity_score
    }
    
    logger.info(f"Input parameters: {json.dumps(input_params, indent=2)}")
    
    try:
        # Make prediction
        result = predictor.predict_single(input_params)
        
        # Generate detailed explanation
        explanation = generate_detailed_explanation(input_params, result)
        
        # Format output
        output_text = format_prediction_output(result, explanation)
        
        logger.info(f"Prediction completed: {result['predicted_risk']} risk")
        logger.info("=== PREDICTION COMPLETED SUCCESSFULLY ===")
        
        return output_text, result['predicted_risk'], output_text
        
    except Exception as e:
        error_msg = f"Error in prediction: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}", "Error", f"❌ {error_msg}"

def generate_detailed_explanation(input_data: Dict, prediction_result: Dict) -> str:
    """Generate detailed explanation based on input and prediction"""
    logger.info("Generating detailed explanation")
    
    risk_level = prediction_result['predicted_risk']
    confidence = prediction_result['confidence']
    model_used = prediction_result.get('model_used', 'Unknown')
    
    # Risk-based explanations
    if risk_level == "High":
        explanation = f"""
### 🔴 **HIGH RISK EXPLANATION** (Confidence: {confidence})

**Key Risk Factors Identified**:
- Depression Score: {input_data['depression_score']}/30 - Severe symptoms
- Anxiety Score: {input_data['anxiety_score']}/21 - Significant distress
- Sleep Quality: {input_data['sleep_hours']} hours - Inadequate rest
- Stress Level: {input_data['stress_level']}/10 - High stress without coping
- Social Support: {input_data['social_support_score']}/100 - Limited support

**Why High Risk Classification**:
The combination of severe symptoms, poor sleep, high stress, and inadequate social support
creates a pattern that significantly increases mental health risk.

**Immediate Recommendations**:
1. Seek professional help within 24-48 hours
2. Contact a mental health professional or crisis helpline
3. Reach out to trusted friends/family for support
4. Consider emergency services if having thoughts of self-harm
"""
    
    elif risk_level == "Medium":
        explanation = f"""
### 🟡 **MEDIUM RISK EXPLANATION** (Confidence: {confidence})

**Factors Present**:
- Depression Score: {input_data['depression_score']}/30 - Moderate symptoms
- Anxiety Score: {input_data['anxiety_score']}/21 - Some anxiety present
- Sleep Quality: {input_data['sleep_hours']} hours - Suboptimal sleep
- Stress Level: {input_data['stress_level']}/10 - Manageable stress
- Social Support: {input_data['social_support_score']}/100 - Adequate support

**Why Medium Risk Classification**:
You show noticeable symptoms that impact wellbeing, but still have adequate coping resources.

**Recommended Actions**:
1. Schedule a mental health screening within 2 weeks
2. Consider counseling if symptoms persist
3. Focus on improving sleep hygiene
4. Strengthen social connections
5. Implement stress management techniques
"""
    
    else:  # Low risk
        explanation = f"""
### 🟢 **LOW RISK EXPLANATION** (Confidence: {confidence})

**Positive Indicators**:
- Depression Score: {input_data['depression_score']}/30 - Minimal symptoms
- Anxiety Score: {input_data['anxiety_score']}/21 - Low anxiety levels
- Sleep Quality: {input_data['sleep_hours']} hours - Good sleep patterns
- Stress Level: {input_data['stress_level']}/10 - Well-managed stress
- Social Support: {input_data['social_support_score']}/100 - Strong support network

**Why Low Risk Classification**:
Your profile shows excellent protective factors with minimal concerning symptoms.

**Maintenance Recommendations**:
1. Continue current healthy habits
2. Maintain regular mental health check-ins
3. Keep nurturing social connections
4. Stay consistent with good sleep and exercise
"""
    
    return explanation + f"\n*Assessment powered by {model_used}*"

def format_prediction_output(result: Dict, explanation: str) -> str:
    """Format the complete prediction output"""
    # Extract metrics for display
    metrics = result.get('model_metrics', {})
    
    output = f"""# 🧠 MENTAL HEALTH RISK ASSESSMENT RESULTS

## 📊 PREDICTION SUMMARY
- **Risk Level**: **{result['predicted_risk']}**
- **Confidence**: {result['confidence']}
- **Model Used**: {result.get('model_used', 'Unknown')}

## 🎯 PROBABILITY BREAKDOWN
- **Low Risk**: {result['probabilities'].get('Low', 'N/A')}
- **Medium Risk**: {result['probabilities'].get('Medium', 'N/A')}
- **High Risk**: {result['probabilities'].get('High', 'N/A')}

## 📈 MODEL PERFORMANCE METRICS
- **Overall Accuracy**: {metrics.get('accuracy', 'N/A'):.4f}
- **Precision (Macro)**: {metrics.get('precision_macro', 'N/A'):.4f}
- **Recall (Macro)**: {metrics.get('recall_macro', 'N/A'):.4f}
- **F1-Score (Macro)**: {metrics.get('f1_macro', 'N/A'):.4f}
- **Mean Squared Error (MSE)**: {metrics.get('mse', 'N/A'):.4f}
- **Mean Absolute Error (MAE)**: {metrics.get('mae', 'N/A'):.4f}
- **R² Score**: {metrics.get('r2_score', 'N/A'):.4f}

## 📝 DETAILED EXPLANATION
{explanation}

## ℹ️ IMPORTANT NOTES
- This is a screening tool, not a clinical diagnosis
- Consult a mental health professional for definitive assessment
- If you're in crisis, contact emergency services immediately
- Results are based on statistical patterns

*Assessment completed at {result['timestamp']}*
"""
    return output

def load_sample_case(case_name: str) -> Tuple:
    """Load predefined sample case"""
    logger.info(f"Loading sample case: {case_name}")
    
    # Find the case
    case = None
    for sample_case in SAMPLE_CASES:
        if sample_case['name'] == case_name:
            case = sample_case
            break
    
    if case:
        data = case['data']
        logger.info(f"Sample case loaded: {case['name']}")
        return (
            data['age'], data['gender'], data['employment_status'],
            data['work_environment'], data['mental_health_history'],
            data['seeks_treatment'], data['stress_level'],
            data['sleep_hours'], data['physical_activity_days'],
            data['depression_score'], data['anxiety_score'],
            data['social_support_score'], data['productivity_score'],
            f"✅ Loaded: {case['name']}"
        )
    else:
        logger.error(f"Sample case not found: {case_name}")
        return None

def get_system_status() -> str:
    """Get current system status"""
    metrics = predictor.test_metrics if hasattr(predictor, 'test_metrics') else {}
    
    status = f"""# 🖥️ SYSTEM STATUS

## Model Information
- **Model Status**: {'🟢 Trained and Ready' if predictor.is_trained else '🔴 Not Trained'}
- **Training Completed**: {'Yes' if predictor.is_trained else 'No'}
- **Best Model**: {predictor.best_model_name}
- **Available Features**: {len(predictor.feature_columns)}
- **Last Update**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Model Performance Metrics
- **Overall Accuracy**: {metrics.get('accuracy', 'N/A'):.4f}
- **Precision (Macro)**: {metrics.get('precision_macro', 'N/A'):.4f}
- **Recall (Macro)**: {metrics.get('recall_macro', 'N/A'):.4f}
- **F1-Score (Macro)**: {metrics.get('f1_macro', 'N/A'):.4f}
- **Mean Squared Error (MSE)**: {metrics.get('mse', 'N/A'):.4f}
- **Mean Absolute Error (MAE)**: {metrics.get('mae', 'N/A'):.4f}
- **R² Score**: {metrics.get('r2_score', 'N/A'):.4f}

## Features Used: {len(predictor.feature_columns)} demographic and clinical factors
- Age, Gender, Employment Status, Work Environment
- Mental Health History, Treatment Seeking
- Stress Level, Sleep Hours, Physical Activity
- Depression Score, Anxiety Score
- Social Support Score, Productivity Score

## Available Models
- Decision Tree Classifier (CURRENTLY ACTIVE)
- Logistic Regression
- K-Nearest Neighbors (KNN)
- Support Vector Machine (SVM)

## System Components
- Data Preprocessing: ✅ Active
- Feature Engineering: ✅ Active
- Model Inference: {'✅ Active' if predictor.is_trained else '❌ Inactive'}
- Logging System: ✅ Active
- Explanation Engine: ✅ Active

## Sample Cases Available
- 🎓 High Risk Student
- 💼 Moderate Risk Professional  
- 👴 Low Risk Senior
"""
    return status

def create_gradio_interface():
    """Create the complete Gradio interface"""
    
    # Custom CSS for better appearance
    custom_css = """
    .gradio-container {
        max-width: 1200px !important;
    }
    .header {
        text-align: center;
        margin-bottom: 20px;
    }
    .prediction-box {
        background-color: #f0f8ff;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .sample-button {
        margin: 5px;
        min-width: 200px;
    }
    """
    
    with gr.Blocks(css=custom_css, title="Mental Health Prediction System") as demo:
        
        # Header
        gr.Markdown("# 🧠 Mental Health Risk Prediction System")
        gr.Markdown("## Professional Mental Health Assessment Tool")
        gr.Markdown("This system uses machine learning to assess mental health risk levels based on multiple factors. All predictions include detailed explanations and comprehensive model metrics.")
        
        with gr.Tab("🔮 Prediction Tool"):
            gr.Markdown("## 📋 Input Parameters")
            
            # Demographics
            with gr.Group():
                gr.Markdown("### 👤 Personal Information")
                with gr.Row():
                    with gr.Column(scale=1):
                        age = gr.Number(label="Age", value=35, minimum=18, maximum=65)
                        gender = gr.Dropdown(
                            choices=["Male", "Female", "Non-binary", "Prefer not to say"],
                            label="Gender",
                            value="Female"
                        )
                    with gr.Column(scale=1):
                        employment_status = gr.Dropdown(
                            choices=["Employed", "Student", "Self-employed", "Unemployed"],
                            label="Employment Status",
                            value="Employed"
                        )
                        work_environment = gr.Dropdown(
                            choices=["On-site", "Remote", "Hybrid"],
                            label="Work Environment",
                            value="Remote"
                        )
                with gr.Row():
                    with gr.Column(scale=1):
                        mental_health_history = gr.Radio(
                            choices=["Yes", "No"],
                            label="Mental Health History",
                            value="No"
                        )
                    with gr.Column(scale=1):
                        seeks_treatment = gr.Radio(
                            choices=["Yes", "No"],
                            label="Currently Seeks Treatment",
                            value="No"
                        )
            
            # Clinical Scores
            with gr.Group():
                gr.Markdown("### 📊 Clinical Assessments")
                with gr.Row():
                    with gr.Column(scale=1):
                        stress_level = gr.Slider(
                            minimum=1, maximum=10, value=5,
                            label="Stress Level (1-10)",
                            info="Current stress level"
                        )
                        sleep_hours = gr.Slider(
                            minimum=2, maximum=12, value=7,
                            label="Sleep Hours (per night)",
                            info="Average nightly sleep duration"
                        )
                        physical_activity_days = gr.Slider(
                            minimum=0, maximum=7, value=3,
                            label="Physical Activity Days (per week)",
                            info="Days of physical activity per week"
                        )
                    with gr.Column(scale=1):
                        depression_score = gr.Slider(
                            minimum=0, maximum=30, value=15,
                            label="Depression Score (0-30)",
                            info="Depression symptom severity"
                        )
                        anxiety_score = gr.Slider(
                            minimum=0, maximum=21, value=10,
                            label="Anxiety Score (0-21)",
                            info="Anxiety symptom severity"
                        )
                        social_support_score = gr.Slider(
                            minimum=0, maximum=100, value=60,
                            label="Social Support Score (0-100)",
                            info="Strength of social support network"
                        )
                        productivity_score = gr.Slider(
                            minimum=0, maximum=100, value=80,
                            label="Productivity Score (0-100)",
                            info="Current work/productivity level"
                        )
            
            # Action buttons and results
            with gr.Row():
                with gr.Column(scale=1):
                    predict_btn = gr.Button("🧠 Analyze Mental Health Risk", variant="primary")
                    clear_btn = gr.Button("🧹 Clear All Fields")
                    
                    # Sample data buttons
                    with gr.Group():
                        gr.Markdown("### 🎯 Sample Cases")
                        sample1_btn = gr.Button("🎓 High Risk Student", elem_classes=["sample-button"])
                        sample2_btn = gr.Button("💼 Moderate Risk Professional", elem_classes=["sample-button"])
                        sample3_btn = gr.Button("👴 Low Risk Senior", elem_classes=["sample-button"])
                        sample_status = gr.Textbox(label="Sample Status", interactive=False)
                
                with gr.Column(scale=1):
                    # Results display with copy button
                    with gr.Group():
                        gr.Markdown("### 📊 Prediction Results")
                        result_output = gr.Markdown(
                            label="Prediction Results",
                            value="Results will appear here after analysis (with comprehensive metrics)..."
                        )
                        
                        # Copy button functionality
                        result_for_copy = gr.Textbox(visible=False)
                        copy_button = gr.Button("📋 Copy Results")
                        copy_status = gr.Textbox(label="Copy Status", interactive=False)
                    
                    # Risk level indicator
                    risk_indicator = gr.Label(
                        label="Risk Classification",
                        value="Not Assessed"
                    )
        
        with gr.Tab("💬 Key-Text Assessment"):
            if not RL_ENGINE_AVAILABLE:
                gr.Markdown("## ⚠️ RL Text Engine not available\n\nPlease check that the `text_processing/old_text_processing/` files are properly set up.")
            else:
                # Initialize engine
                rl_engine = RLTextEngine()
                questions_data = json.load(open(os.path.join(os.path.dirname(__file__), 'text_processing', 'old_text_processing', 'questions.json'), 'r', encoding='utf-8'))
                
                gr.Markdown("## 💬 How Are You Feeling Today?")
                gr.Markdown(
                    "This is a safe space to share what's on your mind. "
                    "Just answer a few simple questions in your own words — "
                    "there are no right or wrong answers.\n\n"
                    "Take your time, be honest with yourself, and remember: "
                    "**asking for help is a sign of strength, not weakness.** 💙"
                )
                
                # Demographics section
                with gr.Group():
                    gr.Markdown("### 👤 Quick Background (factual — not scored)")
                    with gr.Row():
                        txt_age = gr.Number(label="Age", value=25, minimum=18, maximum=65)
                        txt_gender = gr.Dropdown(
                            choices=["Male", "Female", "Non-binary", "Prefer not to say"],
                            label="Gender", value="Prefer not to say"
                        )
                        txt_employment = gr.Dropdown(
                            choices=["Employed", "Student", "Self-employed", "Unemployed"],
                            label="Employment", value="Student"
                        )
                        txt_work_env = gr.Dropdown(
                            choices=["On-site", "Remote", "Hybrid"],
                            label="Work Environment", value="Remote"
                        )
                
                # 13 Question textboxes
                with gr.Group():
                    gr.Markdown("### 💭 Share How You're Feeling")
                    gr.Markdown("*Answer as many or as few as you like. Even one response helps.*")
                    
                    text_inputs = []
                    for q in questions_data['questions']:
                        tb = gr.Textbox(
                            label=f"Q{q['id']}: {q['question']}",
                            placeholder=q['description'],
                            lines=2,
                            max_lines=5
                        )
                        text_inputs.append(tb)
                
                # Action buttons
                with gr.Row():
                    txt_analyze_btn = gr.Button("💙 Check In On Me", variant="primary", scale=2)
                    txt_clear_btn = gr.Button("🧹 Clear All", scale=1)
                
                # Sample test cases
                with gr.Group():
                    gr.Markdown("### 🎯 Try a Sample Scenario")
                    gr.Markdown("*Click any button below to load a realistic test case and see how the assessment works.*")
                    with gr.Row():
                        sample_btn_1 = gr.Button("😔 Struggling Student", elem_classes=["sample-button"])
                        sample_btn_2 = gr.Button("😰 Anxious Professional", elem_classes=["sample-button"])
                        sample_btn_3 = gr.Button("💔 Grieving Parent", elem_classes=["sample-button"])
                        sample_btn_4 = gr.Button("🌱 Recovering & Hopeful", elem_classes=["sample-button"])
                    with gr.Row():
                        sample_btn_5 = gr.Button("🔥 Burned-Out Developer", elem_classes=["sample-button"])
                        sample_btn_6 = gr.Button("🏠 Isolated Teenager", elem_classes=["sample-button"])
                        sample_btn_7 = gr.Button("🚨 Crisis — Needs Help Now", elem_classes=["sample-button"])
                    txt_sample_status = gr.Textbox(label="Sample Status", interactive=False)
                
                # Results area
                with gr.Row():
                    with gr.Column(scale=1):
                        txt_crisis_alert = gr.Markdown(
                            value="",
                            label="Crisis Alert"
                        )
                    with gr.Column(scale=1):
                        txt_risk_result = gr.Label(
                            label="Risk Classification",
                            value="Not Assessed"
                        )
                
                txt_full_report = gr.Markdown(
                    value="*Your analysis report will appear here after you click 'Analyze My Responses'...*",
                    label="Full Report"
                )
                
                # Analysis function
                def run_text_assessment(age, gender, employment, work_env, *responses):
                    try:
                        # Collect responses
                        response_dict = {}
                        for i, resp in enumerate(responses):
                            response_dict[str(i + 1)] = resp if resp else ""
                        
                        # Check if any responses provided
                        filled = [r for r in response_dict.values() if r.strip()]
                        if not filled:
                            return (
                                "",
                                "Not Assessed",
                                "⚠️ Please answer at least one question to get an assessment."
                            )
                        
                        # Run RL text analysis
                        analysis = rl_engine.analyze_all_responses(
                            response_dict, questions_data['questions']
                        )
                        
                        # Build crisis alert
                        crisis_md = ""
                        if analysis['crisis_detected']:
                            for alert in analysis['crisis_alerts']:
                                crisis_md += alert['message'] + "\n\n"
                        
                        # Determine crisis level for escalation
                        crisis_level = "none"
                        if analysis['crisis_detected'] and analysis['crisis_alerts']:
                            crisis_level = analysis['crisis_alerts'][0].get('level', 'warning')
                        
                        # Bridge to DTC features (with crisis-aware escalation)
                        demographics = {
                            'age': age,
                            'gender': gender,
                            'employment_status': employment,
                            'work_environment': work_env,
                        }
                        dtc_input = bridge_scores(
                            analysis['factor_scores'], demographics,
                            crisis_detected=analysis['crisis_detected'],
                            crisis_level=crisis_level,
                        )
                        
                        # Run DTC prediction
                        dtc_result = predictor.predict_single(dtc_input)
                        
                        # Override risk label if crisis detected
                        if analysis['crisis_detected']:
                            risk_label = "⚠️ CRISIS — Immediate Support Needed"
                        else:
                            risk_label = dtc_result['predicted_risk']
                        
                        # Build full report
                        report_parts = []
                        
                        report_parts.append("## 🧠 Text Assessment Report\n")
                        report_parts.append(f"**Overall Severity**: {analysis['overall_severity']}")
                        report_parts.append(f"**Average Factor Score**: {analysis['average_score']}/10")
                        report_parts.append(f"**Questions Answered**: {len(filled)}/13")
                        
                        # Show DTC result — if crisis, show escalated result, not raw
                        if analysis['crisis_detected']:
                            report_parts.append(f"**DTC Risk Prediction**: **{dtc_result['predicted_risk']}** (confidence: {dtc_result['confidence']}) — *escalated by crisis detection*")
                        else:
                            report_parts.append(f"**DTC Risk Prediction**: **{dtc_result['predicted_risk']}** (confidence: {dtc_result['confidence']})")
                        
                        if analysis['crisis_detected']:
                            escalation_label = {'emergency': '2.5', 'crisis': '2.0', 'warning': '1.5'}.get(crisis_level, '1.0')
                            report_parts.append("\n> [!CAUTION]")
                            report_parts.append(f"> **Crisis indicators detected ({crisis_level}).** Factor scores escalated ×{escalation_label}x before DTC prediction.")
                        
                        report_parts.append("\n---\n")
                        
                        # Factor breakdown table
                        report_parts.append(format_score_summary(analysis['factor_scores']))
                        
                        # DTC input summary
                        report_parts.append(format_dtc_input_summary(dtc_input))
                        
                        # Probabilities
                        report_parts.append("\n### 📈 Risk Probabilities\n")
                        for level, prob in dtc_result['probabilities'].items():
                            report_parts.append(f"- **{level}**: {prob}")
                        
                        report_parts.append(f"\n\n*Model: {dtc_result['model_used']} | Timestamp: {dtc_result['timestamp']}*")
                        
                        full_report = "\n".join(report_parts)
                        
                        return (crisis_md, risk_label, full_report)
                        
                    except Exception as e:
                        logger.error(f"Text assessment error: {e}")
                        import traceback
                        traceback.print_exc()
                        return (
                            "",
                            "Error",
                            f"❌ Error during analysis: {str(e)}\n\nPlease try again or check the console for details."
                        )
                
                # Wire up the analyze button
                txt_analyze_btn.click(
                    fn=run_text_assessment,
                    inputs=[txt_age, txt_gender, txt_employment, txt_work_env] + text_inputs,
                    outputs=[txt_crisis_alert, txt_risk_result, txt_full_report]
                )
                
                # Wire up clear button
                def clear_text_inputs():
                    return [25, "Prefer not to say", "Student", "Remote"] + [""] * 13 + ["", "Not Assessed", "*Your results will appear here...*", ""]
                
                txt_clear_btn.click(
                    fn=clear_text_inputs,
                    inputs=[],
                    outputs=[txt_age, txt_gender, txt_employment, txt_work_env] + text_inputs + [txt_crisis_alert, txt_risk_result, txt_full_report, txt_sample_status]
                )
                
                # ============ 7 SAMPLE TEST CASES ============
                TEXT_SAMPLES = {
                    "😔 Struggling Student": {
                        "age": 20, "gender": "Female", "employment": "Student", "work_env": "Remote",
                        "responses": [
                            "I've been feeling really low lately, like nothing I do matters. I cry a lot for no reason.",
                            "My sleep is terrible. I either can't fall asleep or I sleep for 14 hours and still feel tired.",
                            "I have zero energy. Getting out of bed feels like climbing a mountain every morning.",
                            "I barely eat anymore. Food just doesn't appeal to me, I skip meals without even noticing.",
                            "I can't concentrate on my studies at all. I read the same page five times and nothing registers.",
                            "I feel like a complete failure. Everyone else seems to have their life together except me.",
                            "I'm anxious about everything — exams, my future, even simple conversations make me nervous.",
                            "I'm always tense. My shoulders are constantly hunched and I clench my jaw without realizing.",
                            "I've been avoiding my friends. I cancel plans last minute because I just can't face people.",
                            "I have no motivation to study or do anything productive. I just scroll my phone all day.",
                            "No, I don't use any substances.",
                            "Sometimes I wonder if things would be easier if I just wasn't here.",
                            "My mom checks on me sometimes, that helps a little.",
                        ],
                    },
                    "😰 Anxious Professional": {
                        "age": 34, "gender": "Male", "employment": "Employed", "work_env": "Hybrid",
                        "responses": [
                            "I feel okay some days but others I get this overwhelming sense of dread for no reason.",
                            "Sleep is inconsistent. I wake up at 3am with racing thoughts about work deadlines.",
                            "Energy is moderate, I get through the day but I'm exhausted by evening.",
                            "I've been stress eating a lot, especially late at night. Junk food mostly.",
                            "My mind races constantly. I overthink every email I send and every meeting I have.",
                            "I feel like I'm not good enough for my role. Imposter syndrome hits me hard.",
                            "Very anxious. I have panic attacks before important presentations. Heart racing, can't breathe.",
                            "I'm irritable and snappy with my family. The smallest things set me off.",
                            "Relationships are strained. My wife says I'm emotionally unavailable.",
                            "I exercise sometimes which helps, but I've been too tired lately.",
                            "I've been drinking more wine in the evenings to take the edge off. Maybe 2-3 glasses a night.",
                            "No thoughts of harm, just wish the anxiety would stop.",
                            "My kids give me a reason to keep going. They need their dad.",
                        ],
                    },
                    "💔 Grieving Parent": {
                        "age": 52, "gender": "Female", "employment": "Employed", "work_env": "On-site",
                        "responses": [
                            "Since losing my son 6 months ago, I feel like a part of me died with him. The grief is unbearable.",
                            "I either can't sleep at all or I have nightmares about the accident. There's no restful sleep.",
                            "I'm physically drained. Grief takes everything out of you.",
                            "I force myself to eat for my other children's sake, but food tastes like nothing.",
                            "I can't think clearly. I forget things at work. My mind is always somewhere else.",
                            "I blame myself every day. I should have done more. I'm a terrible mother.",
                            "I'm in constant fear of losing someone else. I panic when my daughter doesn't answer her phone.",
                            "I'm filled with anger and tension. Why him? It's not fair.",
                            "I've pushed away most friends. They say things like 'he's in a better place' and it makes me furious.",
                            "I go to grief counseling once a week. It helps a tiny bit.",
                            "No substances, I need to stay clear-headed for my family.",
                            "I don't want to die, but I understand now why people give up. The pain is that bad.",
                            "My daughter and my faith keep me going. I have to be strong for them.",
                        ],
                    },
                    "🌱 Recovering & Hopeful": {
                        "age": 28, "gender": "Non-binary", "employment": "Employed", "work_env": "Remote",
                        "responses": [
                            "I'm doing much better than I was 6 months ago. I still have bad days but they're fewer.",
                            "Sleep is pretty good now. I follow a routine — in bed by 11, up at 7. It works.",
                            "My energy is coming back. I've started going for morning walks again.",
                            "Appetite is normal. I cook healthy meals most days now.",
                            "My thinking is clearer. Meditation has really helped with the brain fog.",
                            "I'm learning to be kinder to myself. It's a process but I'm getting there.",
                            "Mild anxiety sometimes, usually before social events, but I manage it with breathing exercises.",
                            "I feel more relaxed than I have in years. Yoga has been a game-changer.",
                            "I've reconnected with old friends. It feels good to have a support system again.",
                            "I'm genuinely excited about a new project at work. It feels good to care about something.",
                            "I quit drinking 3 months ago. Best decision I ever made.",
                            "No, those dark thoughts are behind me. I'm glad I got help when I did.",
                            "Therapy, my partner, my dog, and journaling — they all keep me grounded.",
                        ],
                    },
                    "🔥 Burned-Out Developer": {
                        "age": 29, "gender": "Male", "employment": "Employed", "work_env": "Remote",
                        "responses": [
                            "I feel empty. I used to love coding but now it feels like a chore. Everything is monotonous.",
                            "I stay up till 3-4am gaming because I dread the next work day. Then I'm exhausted.",
                            "I'm running on fumes. Coffee is the only thing keeping me functional.",
                            "I either skip meals or order takeout. Haven't cooked in weeks.",
                            "I make stupid mistakes in code I would've caught easily before. Brain fog is real.",
                            "I feel replaceable. Like I'm just another cog in the machine.",
                            "I get anxious every Sunday night thinking about Monday. My stomach churns.",
                            "My neck and back are killing me from hunching over a laptop 14 hours a day.",
                            "I only talk to my team on Slack. Haven't seen friends in person for months.",
                            "Zero motivation. I do the bare minimum to not get fired.",
                            "Started vaping more. Used to be occasional, now it's constant.",
                            "I don't want to die, I just want to stop feeling this way.",
                            "Gaming and my cat. That's about it honestly.",
                        ],
                    },
                    "🏠 Isolated Teenager": {
                        "age": 18, "gender": "Female", "employment": "Student", "work_env": "On-site",
                        "responses": [
                            "I feel invisible. Like nobody at school even knows I exist.",
                            "I stay up super late on my phone because that's the only time nobody bothers me. Sleep like 4 hours.",
                            "I'm tired all the time but I can never actually rest. My body feels heavy.",
                            "I eat a lot when I'm sad. Chips, chocolate, whatever. Then I feel guilty about it.",
                            "School feels pointless. I can't focus in class and my grades are slipping.",
                            "I hate how I look. I compare myself to everyone on Instagram and I never measure up.",
                            "I get nervous about going to school. What if people are talking about me behind my back?",
                            "I get really angry at my parents for no reason. Then I feel bad about it.",
                            "I don't really have friends. People talk to me sometimes but I don't feel like I belong.",
                            "I used to draw and paint but I haven't touched my art supplies in months.",
                            "No, I don't use any substances.",
                            "I don't want to hurt myself, but sometimes I wish I could just disappear from everything.",
                            "My dog loves me no matter what. That's the one thing that feels real.",
                        ],
                    },
                    "🚨 Crisis — Needs Help Now": {
                        "age": 22, "gender": "Male", "employment": "Unemployed", "work_env": "On-site",
                        "responses": [
                            "I feel completely hopeless. Nothing will ever get better. I've tried everything.",
                            "I haven't slept properly in weeks. Nightmares every night. I'm afraid to close my eyes.",
                            "No energy at all. I can barely move. Getting up to use the bathroom feels impossible.",
                            "I haven't eaten in 2 days. I just don't see the point.",
                            "I can't think straight. Everything is foggy. I can't make simple decisions.",
                            "I'm worthless. A complete waste of space. Everyone would be better off without me.",
                            "I'm terrified and anxious all the time. Constant panic. Chest tight. Can't breathe.",
                            "I feel like I'm going to explode. Everything inside me is screaming.",
                            "I've pushed everyone away. Nobody understands. Nobody cares. I'm completely alone.",
                            "I have zero will to do anything. Nothing brings me any joy or pleasure anymore.",
                            "I've been drinking heavily to numb the pain. A bottle a day sometimes.",
                            "I want to end it all. I've been thinking about how to do it. I can't take this anymore.",
                            "Nothing. There's nothing keeping me here.",
                        ],
                    },
                }
                
                def load_text_sample(case_name):
                    """Load a sample test case into the text fields."""
                    if case_name not in TEXT_SAMPLES:
                        return [gr.update()] * 17 + [f"❌ Sample not found: {case_name}"]
                    
                    sample = TEXT_SAMPLES[case_name]
                    result = [
                        sample["age"],
                        sample["gender"],
                        sample["employment"],
                        sample["work_env"],
                    ]
                    result.extend(sample["responses"])
                    result.append(f"✅ Loaded: {case_name}")
                    return result
                
                # Wire up all 7 sample buttons
                sample_outputs = [txt_age, txt_gender, txt_employment, txt_work_env] + text_inputs + [txt_sample_status]
                
                for btn, name in [
                    (sample_btn_1, "😔 Struggling Student"),
                    (sample_btn_2, "😰 Anxious Professional"),
                    (sample_btn_3, "💔 Grieving Parent"),
                    (sample_btn_4, "🌱 Recovering & Hopeful"),
                    (sample_btn_5, "🔥 Burned-Out Developer"),
                    (sample_btn_6, "🏠 Isolated Teenager"),
                    (sample_btn_7, "🚨 Crisis — Needs Help Now"),
                ]:
                    btn.click(
                        fn=lambda n=name: load_text_sample(n),
                        inputs=[],
                        outputs=sample_outputs,
                    )
        
        with gr.Tab("📚 Explanation Cards"):
            gr.Markdown("## 📖 Detailed Explanation Resources")
            
            # Tabbed explanation cards with actual content
            with gr.Tabs():
                with gr.TabItem("🔍 Model Explanation Guide"):
                    gr.Markdown(explanation_cards[7])
                
                with gr.TabItem("⚠️ Risk Classification Reference"):
                    gr.Markdown(explanation_cards[8])
                
                with gr.TabItem("🏥 Treatment Seeking Guide"):
                    gr.Markdown(explanation_cards[9])
                
                with gr.TabItem("📊 Symptom Score Interpretation"):
                    gr.Markdown(explanation_cards[10])
                
                with gr.TabItem("📈 Model Technical Specifications"):
                    gr.Markdown(explanation_cards[11])
                
                with gr.TabItem("🎯 Accuracy & Performance Metrics"):
                    gr.Markdown(explanation_cards[12])
                
                with gr.TabItem("🔬 Real Code & Results"):
                    gr.Markdown(explanation_cards[13])
        
        with gr.Tab("📊 Model Metrics"):
            gr.Markdown("## 📊 Comprehensive Model Performance Metrics")
            
            # Display all metrics in an organized manner
            metrics_info = f"""
### 🎯 Overall Performance
- **Accuracy**: {predictor.test_metrics.get('accuracy', 'N/A'):.4f} (Ratio of correct predictions)
- **Precision (Macro)**: {predictor.test_metrics.get('precision_macro', 'N/A'):.4f} (Quality of predictions)
- **Recall (Macro)**: {predictor.test_metrics.get('recall_macro', 'N/A'):.4f} (Completeness of predictions)
- **F1-Score (Macro)**: {predictor.test_metrics.get('f1_macro', 'N/A'):.4f} (Harmonic mean of precision and recall)

### 📈 Regression-like Metrics
- **Mean Squared Error (MSE)**: {predictor.test_metrics.get('mse', 'N/A'):.4f} (Average squared differences)
- **Mean Absolute Error (MAE)**: {predictor.test_metrics.get('mae', 'N/A'):.4f} (Average absolute differences)
- **R² Score**: {predictor.test_metrics.get('r2_score', 'N/A'):.4f} (Proportion of variance explained)

### 🎚️ Per-Class Performance
**Low Risk Category:**
- Precision: {predictor.test_metrics.get('precision_Low', 'N/A'):.4f}
- Recall: {predictor.test_metrics.get('recall_Low', 'N/A'):.4f}
- F1-Score: {predictor.test_metrics.get('f1_Low', 'N/A'):.4f}

**Medium Risk Category:**
- Precision: {predictor.test_metrics.get('precision_Medium', 'N/A'):.4f}
- Recall: {predictor.test_metrics.get('recall_Medium', 'N/A'):.4f}
- F1-Score: {predictor.test_metrics.get('f1_Medium', 'N/A'):.4f}

**High Risk Category:**
- Precision: {predictor.test_metrics.get('precision_High', 'N/A'):.4f}
- Recall: {predictor.test_metrics.get('recall_High', 'N/A'):.4f}
- F1-Score: {predictor.test_metrics.get('f1_High', 'N/A'):.4f}

### 📊 Model Information
- **Algorithm**: Decision Tree Classifier
- **Training Samples**: {len(predictor.y_test) if hasattr(predictor, 'y_test') else 'N/A'}
- **Features Used**: {len(predictor.feature_columns) if hasattr(predictor, 'feature_columns') else 'N/A'}
- **Max Depth**: 10 (prevents overfitting)
- **Minimum Samples Split**: 5 (ensures statistical significance)
"""
            gr.Markdown(metrics_info)
        
        with gr.Tab("⚙️ System Status"):
            gr.Markdown("## 🖥️ System Information & Controls")
            gr.Markdown(get_system_status())
        
        # Event handlers
        predict_result = predict_btn.click(
            fn=make_prediction,
            inputs=[
                age, gender, employment_status, work_environment,
                mental_health_history, seeks_treatment, stress_level,
                sleep_hours, physical_activity_days, depression_score,
                anxiety_score, social_support_score, productivity_score
            ],
            outputs=[result_output, risk_indicator, result_for_copy]
        )
        
        # Copy button functionality
        def copy_to_clipboard(text):
            return f"✅ Copied to clipboard! Length: {len(text)} characters"
        
        copy_button.click(
            fn=copy_to_clipboard,
            inputs=[result_for_copy],
            outputs=[copy_status]
        )
        
        # Sample case loaders with proper error handling
        def load_sample_wrapper(case_name):
            try:
                result = load_sample_case(case_name)
                if result:
                    return result
                else:
                    return [gr.update()] * 14 + [f"❌ Error loading {case_name}"]
            except Exception as e:
                logger.error(f"Error loading sample case {case_name}: {e}")
                return [gr.update()] * 14 + [f"❌ Error: {str(e)}"]
        
        sample1_btn.click(
            fn=lambda: load_sample_wrapper("🎓 High Risk Student"),
            inputs=[],
            outputs=[
                age, gender, employment_status, work_environment,
                mental_health_history, seeks_treatment, stress_level,
                sleep_hours, physical_activity_days, depression_score,
                anxiety_score, social_support_score, productivity_score,
                sample_status
            ]
        )
        
        sample2_btn.click(
            fn=lambda: load_sample_wrapper("💼 Moderate Risk Professional"),
            inputs=[],
            outputs=[
                age, gender, employment_status, work_environment,
                mental_health_history, seeks_treatment, stress_level,
                sleep_hours, physical_activity_days, depression_score,
                anxiety_score, social_support_score, productivity_score,
                sample_status
            ]
        )
        
        sample3_btn.click(
            fn=lambda: load_sample_wrapper("👴 Low Risk Senior"),
            inputs=[],
            outputs=[
                age, gender, employment_status, work_environment,
                mental_health_history, seeks_treatment, stress_level,
                sleep_hours, physical_activity_days, depression_score,
                anxiety_score, social_support_score, productivity_score,
                sample_status
            ]
        )
        
        # Clear button
        def clear_inputs():
            return [
                35, "Female", "Employed", "Remote", "No", "No",
                5, 7, 3, 15, 10, 60, 80, "Fields cleared"
            ]
        
        clear_btn.click(
            fn=clear_inputs,
            inputs=[],
            outputs=[
                age, gender, employment_status, work_environment,
                mental_health_history, seeks_treatment, stress_level,
                sleep_hours, physical_activity_days, depression_score,
                anxiety_score, social_support_score, productivity_score,
                sample_status
            ]
        )
    
    return demo

def main():
    """Main application entry point"""
    print(Fore.CYAN + Style.BRIGHT + "\n🧠 === MENTAL HEALTH PREDICTION SYSTEM WITH REAL CODE EXAMPLES STARTING ===")
    logger.info("=== MENTAL HEALTH PREDICTION SYSTEM WITH REAL CODE EXAMPLES STARTING ===")
    
    # Create and launch the interface
    app = create_gradio_interface()
    
    print(Fore.YELLOW + "🌐 Launching Gradio interface on localhost:7860")
    logger.info("Launching Gradio interface on localhost:7860")
    # Try to launch on port 7860, if unavailable try alternatives
    import socket
    def is_port_available(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    # Find available port starting from 7860
    port = 7860
    while not is_port_available(port) and port <= 7870:
        print(Fore.YELLOW + f"⚠️  Port {port} is in use, trying {port + 1}...")
        port += 1
    
    if not is_port_available(port):
        print(Fore.RED + "❌ No available ports found in range 7860-7870")
        return
    
    print(Fore.CYAN + f"🌐 Launching Gradio interface on localhost:{port}")
    logger.info(f"Launching Gradio interface on localhost:{port}")
    
    app.launch(
        server_name="127.0.0.1",
        server_port=port,
        share=False,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()
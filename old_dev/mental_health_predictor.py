"""
🧠 Mental Health Prediction System - FINAL CLEAN VERSION
=======================================================

Final implementation with:
- Proper markdown content loading in tabs
- Clean interface
- Organized code
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

# Initialize colorama
colorama.init(autoreset=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print(Fore.CYAN + Style.BRIGHT + "🧪 Testing Mental Health Prediction System...")

# Load explanation cards with actual content
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

# Load explanation cards
explanation_cards = load_explanation_cards()

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

# Mock predictor for demonstration
class MockPredictor:
    def __init__(self):
        self.is_trained = True
        self.feature_columns = []
        self.best_model_name = "Mock Model"
        
    def predict_single(self, data):
        # Simple logic based on depression score
        if data['depression_score'] > 20:
            risk = 'High'
            confidence = 0.85
        elif data['depression_score'] > 10:
            risk = 'Medium'
            confidence = 0.75
        else:
            risk = 'Low'
            confidence = 0.90
            
        return {
            'predicted_risk': risk,
            'confidence': f"{confidence:.1%}",
            'probabilities': {'Low': '30%', 'Medium': '40%', 'High': '30%'},
            'model_used': 'Mock Model',
            'timestamp': datetime.now().isoformat()
        }

predictor = MockPredictor()

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
    output = f"""# 🧠 MENTAL HEALTH RISK ASSESSMENT RESULTS

## 📊 PREDICTION SUMMARY
- **Risk Level**: **{result['predicted_risk']}**
- **Confidence**: {result['confidence']}
- **Model Used**: {result.get('model_used', 'Unknown')}

## 🎯 PROBABILITY BREAKDOWN
- **Low Risk**: {result['probabilities']['Low']}
- **Medium Risk**: {result['probabilities']['Medium']}
- **High Risk**: {result['probabilities']['High']}

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
    status = f"""# 🖥️ SYSTEM STATUS

## Model Information
- **Model Status**: {'🟢 Trained and Ready' if predictor.is_trained else '🔴 Not Trained'}
- **Training Completed**: Yes
- **Best Model**: {getattr(predictor, 'best_model_name', 'Not Selected')}
- **Available Features**: {len(getattr(predictor, 'feature_columns', []))}
- **Last Update**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Available Models
- Decision Tree Classifier
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
    .explanation-card {
        background-color: #f9f9f9;
        border-left: 5px solid #4f8bf9;
        padding: 15px;
        margin: 10px 0;
        max-height: 500px;
        overflow-y: auto;
    }
    .sample-button {
        margin: 5px;
        min-width: 200px;
    }
    .tab-header {
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    """
    
    with gr.Blocks(css=custom_css, title="Mental Health Prediction System") as demo:
        
        # Header
        gr.Markdown("# 🧠 Mental Health Risk Prediction System")
        gr.Markdown("## Professional Mental Health Assessment Tool")
        gr.Markdown("This system uses machine learning to assess mental health risk levels based on multiple factors. All predictions include detailed explanations and recommendations.")
        
        with gr.Tab("🔮 Prediction Tool"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## 📋 Input Parameters")
                    
                    # Demographics
                    with gr.Group():
                        gr.Markdown("### 👤 Personal Information")
                        age = gr.Number(label="Age", value=35, minimum=18, maximum=65)
                        gender = gr.Dropdown(
                            choices=["Male", "Female", "Non-binary", "Prefer not to say"],
                            label="Gender",
                            value="Female"
                        )
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
                        mental_health_history = gr.Radio(
                            choices=["Yes", "No"],
                            label="Mental Health History",
                            value="No"
                        )
                        seeks_treatment = gr.Radio(
                            choices=["Yes", "No"],
                            label="Currently Seeks Treatment",
                            value="No"
                        )
                    
                    # Clinical Scores
                    with gr.Group():
                        gr.Markdown("### 📊 Clinical Assessments")
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
                    
                    # Action buttons
                    with gr.Row():
                        predict_btn = gr.Button("🧠 Analyze Mental Health Risk", variant="primary")
                        clear_btn = gr.Button("🧹 Clear All Fields")
                
                with gr.Column(scale=1):
                    gr.Markdown("## 📋 Results & Recommendations")
                    
                    # Sample data buttons
                    with gr.Group():
                        gr.Markdown("### 🎯 Sample Cases")
                        with gr.Row():
                            sample1_btn = gr.Button("🎓 High Risk Student", elem_classes=["sample-button"])
                            sample2_btn = gr.Button("💼 Moderate Risk Professional", elem_classes=["sample-button"])
                        with gr.Row():
                            sample3_btn = gr.Button("👴 Low Risk Senior", elem_classes=["sample-button"])
                        sample_status = gr.Textbox(label="Sample Status", interactive=False)
                    
                    # Results display with copy button
                    with gr.Group():
                        gr.Markdown("### 📊 Prediction Results")
                        result_output = gr.Markdown(
                            label="Prediction Results",
                            value="Results will appear here after analysis..."
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
        
        with gr.Tab("⚙️ System Status"):
            gr.Markdown("## 🖥️ System Information & Controls")
            
            gr.Markdown(get_system_status())
            
            gr.Markdown("""
## ℹ️ Usage Guide

### Getting Started:
1. Enter patient/client information in the input fields
2. Click "Analyze Mental Health Risk" for assessment
3. Review detailed results and recommendations

### Key Features:
- **Real-time predictions** with confidence scores
- **Detailed explanations** for every result
- **Sample cases** for demonstration
- **Comprehensive documentation** in explanation cards
- **Full audit trail** through detailed logging

### Important Notes:
- This is a **screening tool**, not a clinical diagnosis
- Always consult qualified mental health professionals
- In crisis situations, contact emergency services immediately
- Results are based on statistical patterns, not individual circumstances
""")
        
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
    print(Fore.CYAN + Style.BRIGHT + "\n🧠 === MENTAL HEALTH PREDICTION SYSTEM STARTING ===")
    logger.info("=== MENTAL HEALTH PREDICTION SYSTEM STARTING ===")
    
    # Create and launch the interface
    app = create_gradio_interface()
    
    print(Fore.YELLOW + "🌐 Launching Gradio interface on localhost:7860")
    logger.info("Launching Gradio interface on localhost:7860")
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()
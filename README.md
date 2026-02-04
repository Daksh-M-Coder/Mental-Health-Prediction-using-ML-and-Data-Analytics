# 🧠 Mental Health Risk Prediction System

## 📋 Project Overview

A comprehensive machine learning system for mental health risk assessment using Decision Tree Classifier. This project analyzes multiple demographic and clinical factors to predict mental health risk levels (Low/Medium/High) with detailed explanations and comprehensive performance metrics.

## 🎯 Key Features

- **🎯 Accurate Risk Prediction**: Classifies mental health risk into Low, Medium, or High categories
- **📊 Comprehensive Metrics**: Displays accuracy, precision, recall, F1-score, MSE, MAE, and R²
- **📝 Detailed Explanations**: Provides reasoning for each prediction with actionable insights
- **🎨 User-Friendly Interface**: Gradio web interface with tabbed navigation
- **📋 Sample Cases**: Predefined test cases for demonstration
- **💾 Copy Functionality**: Easy result sharing and documentation
- **🎨 Enhanced UI**: Color-coded terminal output and clean web interface

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Launch the Application
```bash
python mental_health_ml_system.py
```

The application will attempt to start at: `http://127.0.0.1:7860`
If port 7860 is busy, it will automatically try ports 7861-7870 until it finds an available port.

## 📊 System Architecture

### Core Components
1. **Data Processing**: Handles mental health dataset with 13 clinical and demographic features
2. **Machine Learning Model**: Decision Tree Classifier with optimized parameters
3. **Prediction Engine**: Real-time risk assessment with confidence scores
4. **Explanation System**: Detailed reasoning for each prediction
5. **Web Interface**: Gradio-based UI with multiple tabs and features

### Input Features
- **Demographics**: Age, Gender, Employment Status, Work Environment
- **Clinical History**: Mental Health History, Treatment Seeking Behavior
- **Current State**: Stress Level, Sleep Hours, Physical Activity
- **Symptom Scores**: Depression Score, Anxiety Score
- **Support Metrics**: Social Support Score, Productivity Score

## 🎯 Model Performance

### Overall Metrics
- **Accuracy**: 1.0000 (100% correct predictions)
- **Precision**: 1.0000 (Perfect prediction quality)
- **Recall**: 1.0000 (Perfect case identification)
- **F1-Score**: 1.0000 (Perfect balance)
- **MSE**: 0.0000 (No prediction errors)
- **MAE**: 0.0000 (No absolute errors)
- **R² Score**: 1.0000 (Perfect variance explanation)

### Per-Class Performance
All risk categories (Low, Medium, High) achieve perfect scores across all metrics.

## 📁 Repository Structure

```
Heathcare ML Pred/
├── dataset/                    # Mental health datasets
│   └── mental_health_dataset.csv
├── insights/                   # Documentation and explanation cards
│   ├── 0_FILE_LISTING_AND_NAVIGATION.md
│   ├── 1_EXECUTIVE_SUMMARY.md
│   ├── 2_MENTAL_HEALTH_DATASET_COMPREHENSIVE_ANALYSIS.md
│   ├── 3_STATISTICAL_VALIDATION_ANALYSIS.md
│   ├── 4_MACHINE_LEARNING_PIPELINE.md
│   ├── 5_PRACTICAL_IMPLEMENTATION.md
│   ├── 6_QUICK_REFERENCE_PREDICTION_SYSTEM.md
│   ├── 7_MODEL_EXPLANATION_GUIDE.md
│   ├── 8_RISK_CLASSIFICATION_REFERENCE_CARD.md
│   ├── 9_TREATMENT_SEEKING_GUIDE.md
│   ├── 10_SYMPTOM_SCORE_INTERPRETATION.md
│   ├── 11_MODEL_TECHNICAL_SPECIFICATIONS.md
│   ├── 12_ACCURACY_EXPLANATION.md
│   └── correlation_heatmap.png
├── old_dev/                    # Development files and previous versions
├── mental_health_ml_system.py  # Main application file
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── launch.bat                 # Windows launcher script
```

## 🛠️ Technical Implementation

### Machine Learning Pipeline
```python
# Model Configuration
model = DecisionTreeClassifier(
    random_state=42,
    max_depth=10,
    min_samples_split=5
)

# Feature Engineering
features = [
    'age', 'gender', 'employment_status', 'work_environment',
    'mental_health_history', 'seeks_treatment', 'stress_level',
    'sleep_hours', 'physical_activity_days', 'depression_score',
    'anxiety_score', 'social_support_score', 'productivity_score'
]

# Training Process
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)
model.fit(X_train, y_train)
```

### Performance Evaluation
```python
# Comprehensive Metrics Calculation
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='macro')
recall = recall_score(y_test, y_pred, average='macro')
f1 = f1_score(y_test, y_pred, average='macro')
mse = mean_squared_error(y_test_encoded, y_pred_encoded)
mae = mean_absolute_error(y_test_encoded, y_pred_encoded)
r2 = r2_score(y_test_encoded, y_pred_encoded)
```

## 📚 Documentation

### Explanation Cards
The system includes comprehensive documentation accessible through the web interface:

1. **Model Explanation Guide** - How the ML model works
2. **Risk Classification Reference** - Understanding risk categories
3. **Treatment Seeking Guide** - When to seek professional help
4. **Symptom Score Interpretation** - Understanding clinical scores
5. **Model Technical Specifications** - Technical details
6. **Accuracy & Performance Metrics** - Detailed metrics explanation
7. **Real Code & Results** - Actual implementation with outputs

### Sample Cases
- 🎓 High Risk Student (24-year-old female student)
- 💼 Moderate Risk Professional (42-year-old male employee)
- 👴 Low Risk Senior (58-year-old self-employed individual)

## 🔧 Development Setup

### Environment Requirements
- Python 3.8+
- Required packages: gradio, pandas, numpy, scikit-learn, colorama

### Installation
```bash
# Clone the repository
git clone <repository-url>

# Install dependencies
pip install -r requirements.txt

# Run the application
python mental_health_ml_system.py
```

## 📈 Future Enhancements

- [ ] Integration with additional mental health datasets
- [ ] Multi-model comparison dashboard
- [ ] Real-time data visualization
- [ ] API endpoint for external integration
- [ ] Mobile-responsive interface
- [ ] Advanced feature importance analysis

## 🤝 Contributing

This project is designed for educational and research purposes. Feel free to:
- Fork the repository
- Submit bug reports
- Suggest improvements
- Share use cases

## ⚠️ Important Disclaimers

- This is a **screening tool**, not a clinical diagnosis
- Results should supplement, not replace, professional medical advice
- Always consult qualified mental health professionals for definitive assessment
- In crisis situations, contact emergency services immediately

## 📞 Support

For questions or issues:
- Check the documentation in the `insights/` folder
- Review the system logs in the terminal output
- Examine the sample cases for usage examples

---

*Built with ❤️ for mental health awareness and early intervention*
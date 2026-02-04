# Dataset 1: Mental Illnesses Prevalence (Global)
## File: `1- mental-illnesses-prevalence.csv`

---

## 📋 DATASET OVERVIEW

**File Size**: 440.9 KB  
**Rows**: 6,421  
**Columns**: 8  
**Time Period**: 1990-2019 (30 years)  
**Countries Covered**: 195+ countries  
**Data Source**: Institute for Health Metrics and Evaluation (IHME)  

---

## 🔢 DATA STRUCTURE & VARIABLES

### Primary Key Variables:
- **Entity**: Country/territory name
- **Code**: ISO 3-letter country code (e.g., AFG, USA, IND)
- **Year**: Calendar year (1990-2019)

### Mental Health Conditions (All Age-standardized, Both Sexes):
1. **Schizophrenia disorders** (percentage of population)
2. **Depressive disorders** (percentage of population)  
3. **Anxiety disorders** (percentage of population)
4. **Bipolar disorders** (percentage of population)
5. **Eating disorders** (percentage of population)

---

## 📊 KEY STATISTICAL INSIGHTS

### **Prevalence Ranges (2019 Data)**:
| Disorder | Global Average | Min (Country) | Max (Country) |
|----------|---------------|---------------|---------------|
| Anxiety | ~3.8% | 2.1% (Japan) | 7.2% (Brazil) |
| Depression | ~4.4% | 2.8% (Netherlands) | 6.8% (India) |
| Bipolar | ~0.6% | 0.3% (Vietnam) | 1.2% (USA) |
| Schizophrenia | ~0.28% | 0.15% (China) | 0.45% (Australia) |
| Eating Disorders | ~0.4% | 0.1% (Ethiopia) | 1.1% (USA) |

### **Temporal Trends (1990-2019)**:
- **Anxiety disorders**: ↑ 15% globally (4.7% → 5.4%)
- **Depressive disorders**: ↑ 12% globally (4.9% → 5.5%)
- **Bipolar disorders**: Stable (~0.6-0.7%)
- **Schizophrenia**: ↓ 8% (0.32% → 0.29%)
- **Eating disorders**: ↑ 25% (0.3% → 0.38%)

---

## 🌍 GEOGRAPHIC PATTERNS

### **High-Burden Regions**:
1. **Eastern Europe**: Highest anxiety and depression rates
2. **South Asia**: Elevated depression and eating disorder prevalence
3. **Latin America**: High anxiety disorder rates
4. **Sub-Saharan Africa**: Lower overall rates but growing rapidly

### **Low-Burden Regions**:
1. **East Asia**: Generally lower prevalence across conditions
2. **Middle East**: Moderate rates with regional variation
3. **Scandinavia**: Among lowest rates globally

---

## 🎯 ANALYTICAL APPLICATIONS

### **Primary Use Cases**:
1. **Global Burden Mapping**: Create world maps showing prevalence by condition
2. **Trend Analysis**: Examine 30-year progression of mental health conditions
3. **Regional Comparison**: Compare burden between world regions
4. **Correlation Studies**: Link prevalence with economic/social factors
5. **Forecasting Models**: Predict future prevalence trends

### **Secondary Applications**:
- Healthcare resource planning
- Policy priority setting
- Research funding allocation
- Public health intervention targeting

---

## ⚠️ DATA QUALITY CONSIDERATIONS

### **Strengths**:
✅ Standardized methodology across countries  
✅ Age-standardized rates for fair comparison  
✅ Long temporal coverage (30 years)  
✅ Comprehensive geographic coverage  
✅ Peer-reviewed IHME methodology  

### **Limitations**:
⚠️ Self-reported survey data subject to response bias  
⚠️ Cultural differences in symptom recognition/reporting  
⚠️ Limited granularity (country-level only)  
⚠️ May underrepresent rural/underserved populations  
⚠️ Diagnostic criteria variations across cultures  

---

## 🛠️ TECHNICAL SPECIFICATIONS

### **Data Processing Requirements**:
- Handle missing country codes (some regions aggregate)
- Convert percentage to actual population numbers using census data
- Time series analysis for trend identification
- Geographic clustering for regional patterns

### **Recommended Visualizations**:
1. **Choropleth Maps**: Global prevalence distribution
2. **Line Charts**: 30-year trend lines by condition
3. **Heatmaps**: Condition correlation matrix
4. **Box Plots**: Regional distribution comparisons
5. **Scatter Plots**: Prevalence vs. GDP/capita relationships

---

## 🔍 DEEP DIVE QUESTIONS FOR ANALYSIS

1. Which countries show the steepest increases in mental health disorders?
2. Are there clusters of countries with similar prevalence patterns?
3. How do prevalence rates correlate with economic development?
4. What explains the geographic variation in eating disorder rates?
5. Are there threshold effects where prevalence accelerates?

*This dataset forms the foundation for all other mental health analyses*
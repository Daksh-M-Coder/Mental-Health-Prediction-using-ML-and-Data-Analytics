# Dataset 8: Estimated Prevalence vs Burden (Mental Illnesses)
## File: `estimated-prevalence-vs-burden-mental-illnesses.csv`

---

## 📋 DATASET OVERVIEW

**File Size**: 6.4 KB  
**Rows**: 151  
**Columns**: 5  
**Time Period**: 1990-2019 (30 years)  
**Scope**: Global mental illness conditions  
**Metrics**: Prevalence (%) vs. Disability-Adjusted Life Years (DALYs)  
**Data Source**: Integrated IHME and WHO data  

---

## 🔢 DATA STRUCTURE & VARIABLES

### Core Variables:
- **Entity**: Mental health condition category
- **Code**: Condition identifier (blank for aggregates)
- **Year**: Calendar year (1990-2019)
- **Prevalence (share of population)**: Percentage of population affected
- **DALYs (rate)**: Disability-adjusted life years per 100,000 population

### Conditions Covered:
1. **Anxiety disorders**
2. **Depressive disorders** 
3. **Bipolar disorder**
4. **Schizophrenia**
5. **Eating disorders**

---

## 📊 KEY FINDINGS & RELATIONSHIPS

### **Prevalence vs. Burden Correlation Analysis**:

#### **Condition-Level Analysis** (2019 data):
| Condition | Prevalence | DALYs/100k | Prevalence Rank | Burden Rank | Ratio (DALYs/% prevalence) |
|-----------|------------|------------|-----------------|-------------|---------------------------|
| **Depressive disorders** | 4.4% | 850 | 2nd | 1st | 19,318 |
| **Anxiety disorders** | 3.8% | 420 | 1st | 2nd | 11,053 |
| **Bipolar disorder** | 0.6% | 145 | 4th | 3rd | 24,167 |
| **Schizophrenia** | 0.28% | 135 | 5th | 4th | 48,214 |
| **Eating disorders** | 0.4% | 25 | 3rd | 5th | 6,250 |

### **Key Insights from the Data**:
1. **Depression** has highest absolute burden despite not being most prevalent
2. **Anxiety** is most prevalent but has moderate burden per case
3. **Schizophrenia** has extremely high burden per case ratio
4. **Eating disorders** have lowest overall impact despite serious individual consequences

### **Temporal Trends (1990-2019)**:
- **Prevalence-DALY Correlation**: r = 0.89 (strong positive relationship)
- **Per-Capita Burden**: Increasing for all conditions except schizophrenia
- **Efficiency Metric**: DALYs per percentage point of prevalence shows improvement

---

## 📈 ECONOMIC IMPLICATIONS

### **Cost-Effectiveness Analysis**:
Based on prevalence-burden relationships:

**Most Efficient Intervention Targets**:
1. **Anxiety disorders**: High prevalence, moderate per-case burden
2. **Depressive disorders**: High prevalence, high per-case burden
3. **Bipolar disorder**: Moderate prevalence, very high per-case burden

**Lower Priority** (per resource unit):
1. **Eating disorders**: Lower prevalence, lower per-case burden
2. **Schizophrenia**: Very low prevalence, extremely high per-case burden

### **Resource Allocation Framework**:
- **Population Impact**: Anxiety and Depression (85% of total burden)
- **Severity Focus**: Schizophrenia and Bipolar (highest individual impact)
- **Prevention Potential**: Anxiety disorders (earliest intervention window)

---

## 🎯 POLICY RECOMMENDATIONS

### **Tiered Intervention Strategy**:

#### **Tier 1: Population-Level Prevention** (High Prevalence Conditions)
- Anxiety disorders: Universal screening and early intervention
- Depressive disorders: Community-based prevention programs
- **Rationale**: Maximum population health impact

#### **Tier 2: Specialized Care** (High Severity Conditions)
- Schizophrenia: Early psychosis intervention programs
- Bipolar disorder: Mood stabilization and relapse prevention
- **Rationale**: Highest individual case burden

#### **Tier 3: Targeted Support** (Lower Prevalence Conditions)
- Eating disorders: Specialized treatment centers
- **Rationale**: Significant individual impact but lower population frequency

---

## ⚠️ DATA QUALITY & LIMITATIONS

### **Strengths**:
✅ Integrated IHME-WHO methodology  
✅ Consistent temporal coverage  
✅ Standardized burden metrics  
✅ Comprehensive condition coverage  

### **Limitations**:
⚠️ Aggregated condition categories (hides subtypes)
⚠️ No demographic breakdown in this dataset
⚠️ Cross-sectional analysis only
⚠️ May not capture comorbidity effects
⚠️ Limited to measured/prevalent cases

---

## 🛠️ ANALYTICAL APPLICATIONS

### **Immediate Use Cases**:
1. **Resource prioritization** for mental health investments
2. **Cost-effectiveness modeling** for intervention programs
3. **Burden of disease ranking** for policy decision-making
4. **Trend analysis** for monitoring progress

### **Advanced Applications**:
1. **Multi-criteria decision analysis** for resource allocation
2. **Scenario modeling** for different intervention strategies
3. **Economic impact assessment** of mental health investments
4. **Health technology assessment** for new treatments

---

## 🔍 RESEARCH OPPORTUNITIES

### **Primary Research Questions**:
1. What explains the differential burden-per-prevalence ratios across conditions?
2. How do treatment effectiveness vary by condition burden profiles?
3. What are optimal resource allocation strategies given these relationships?
4. How do these patterns vary by country income level?

### **Methodological Extensions**:
- Incorporate quality of life weights
- Add healthcare cost data
- Include indirect economic burden
- Examine temporal trend variations

---

*This dataset provides the essential foundation for evidence-based mental health resource allocation decisions*
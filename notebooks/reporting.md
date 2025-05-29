# Health Data Insights Report

The reporting visualizes real-time predictions of patient illness using Looker Studio, based on streaming medical data classified by a trained ML model. It helps monitor health trends across age groups, genders, and key lab metrics for analytical insights.

## 1. Patient Age Overview
- X-Axis: `age_group`
- Y-Axis: Record Count – the number of patient records in each age group

![chart1](https://github.com/user-attachments/assets/bdd205d4-4dc1-46b5-9392-111ec5f13045)

**Insight:**

- The equal and high record counts in the 18–34 and 65–79 age groups may reflect two key healthcare focuses: preventive care and early detection in younger adults, and chronic condition management in older adults.
- In contrast, the notably lower count in the 80+ group may suggest underrepresentation due to lower digital health adoption, limited access, or data gaps in very elderly populations.
- This could highlight the need for improved outreach or data collection strategies in that segment.

## 2. Lab Tests by Age Group
- Group by: `age_group`
- Metrics: `glucose`, `hemoglobin`, `leukocytes`, `creatinine`

![chart2](https://github.com/user-attachments/assets/18d35c96-f99d-46df-9771-97966785b28e)

**Insight:**

- Lab test values (glucose, hemoglobin, leukocytes) generally decline with increasing age, especially in the 80+ group, which shows the lowest values across all tests.
- This may indicate age-related physiological decline or reduced frequency of tests in the elderly.
- Creatinine remains low and stable, possibly due to normalization or low testing rates, which could warrant further clinical review.
- This trend suggests a potential need for closer monitoring of elderly patients, as declining lab values may reflect underlying health vulnerabilities.

## 3. Gender-Based Differences

- X-axis: `gender`
- Y-Axis: `hemoglobin` (blue), `creatinine` (orange)

![chart3](https://github.com/user-attachments/assets/8446c0bc-3d5f-4864-9d04-99180144e733)

**Insight:**

Hemoglobin Levels:

- Males (14.11) have slightly higher hemoglobin than females (14.05).
- Clinically expected due to higher red blood cell production in males (testosterone effect).

Creatinine Levels:
- Males (4.36) also show higher creatinine than females (4.24).
- This aligns with known physiological differences—more muscle mass generally leads to higher creatinine.

> Note: The insights below are derived from simulated patient data for testing analytical pipelines. While patterns may reflect known clinical trends, they should not be considered diagnostic or conclusive without validation on real-world data.
-----

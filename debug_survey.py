import pandas as pd
from utils.survey_enhancer import SurveyDataEnhancer
from utils.csv_analyzer import CSVAnalyzer

# Create the enhancer
enhancer = SurveyDataEnhancer()
analyzer = CSVAnalyzer()

# Load your survey data (adjust path as needed)
df = pd.read_csv('complex_survey.csv')  # or whatever your survey file is called

print(f"📊 Original survey has {len(df)} rows and {len(df.columns)} columns")
print(f"Column names: {list(df.columns)}")
print()

# Test survey enhancer
print("🔍 Testing Survey Enhancer:")
survey_texts, survey_info = enhancer.extract_survey_responses(df)
print(f"Survey enhancer found: {len(survey_texts)} responses")
print(f"Platform detected: {survey_info['platform_detected']}")
print(f"Open-ended count: {survey_info['open_ended_count']}")
print(f"Other specify count: {survey_info['other_specify_count']}")
print(f"Combined responses count: {survey_info['combined_responses_count']}")
print()

# Test CSV analyzer
print("🔍 Testing CSV Analyzer:")
csv_texts, csv_analysis = analyzer.auto_detect_and_process(df)
print(f"CSV analyzer found: {len(csv_texts)} responses")
if 'recommended_columns' in csv_analysis:
    print("Recommended columns:")
    for rec in csv_analysis['recommended_columns'][:5]:
        print(f"  - {rec['column']}: {rec['score']:.3f} - {rec['reason']}")
print()

# Show what we're actually extracting
print("🎯 Sample extracted responses:")
all_responses = survey_texts if len(survey_texts) > len(csv_texts) else csv_texts
for i, response in enumerate(all_responses[:10], 1):
    print(f"{i}. {response[:100]}...")
print()

# Show what columns have data
print("📈 Column data analysis:")
for col in df.columns:
    non_null = df[col].count()
    if non_null > 0:
        sample_values = df[col].dropna().head(3).tolist()
        print(f"  {col}: {non_null} non-null values")
        print(f"    Sample: {sample_values}")
        print()
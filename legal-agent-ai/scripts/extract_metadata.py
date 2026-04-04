import pandas as pd
import re
import os

def extract_metadata(input_csv, output_csv):
    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        print(f"Error reading {input_csv}: {e}")
        return

    states = ["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", 
              "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", 
              "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", 
              "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi", "Puducherry"]

    def get_state(text):
        if not isinstance(text, str): return "Central"
        for s in states:
            if s.lower() in text.lower():
                return s
        return "Central"
        
    def get_gender(text):
        if not isinstance(text, str): return "All"
        t = text.lower()
        if "women" in t or "female" in t or "widow" in t or "girl" in t:
            return "Female"
        if "men" in t or "male" in t or "boy" in t:
            # Need to be careful of women vs men, women contains men
            if "women" not in t and "women" not in t.replace("men", ""):
                 return "Male"
        return "All"

    def get_caste(text):
        if not isinstance(text, str): return "All"
        t = text.lower()
        if "scheduled tribe" in t or " st " in t: return "ST"
        if "scheduled caste" in t or " sc " in t: return "SC"
        if "backward class" in t or "obc" in t: return "OBC"
        return "All"

    print("Extracting metadata...")
    # Add structured columns
    df['state_name'] = df.apply(lambda row: get_state(str(row.get('eligibility', '')) + " " + str(row.get('details', ''))), axis=1)
    df['target_gender'] = df['eligibility'].apply(get_gender)
    df['target_caste'] = df.apply(lambda row: get_caste(str(row.get('eligibility', '')) + " " + str(row.get('scheme_name', ''))), axis=1)

    # Note: Age and Income require more complex parsing, skipping for basic prototype
    
    print(f"Extracted metadata. Sample Distribution for State:\n{df['state_name'].value_counts().head()}")
    df.to_csv(output_csv, index=False)
    print(f"Saved to {output_csv}")

if __name__ == "__main__":
    input_path = os.path.join(os.path.dirname(__file__), "../data/updated_data.csv")
    output_path = os.path.join(os.path.dirname(__file__), "../data/structured_schemes.csv")
    extract_metadata(input_path, output_path)

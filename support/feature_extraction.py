import os
import json
from typing import Dict, Any, List
import pandas as pd
from utils import SALESFORCE_SKILLS

PARSED_DIR = os.path.join("data", "parsed") #directory where parsed resumes are stored
OUTPUT_DIR = os.path.join("data", "features") #directory where extracted features will be stored

os.makedirs(OUTPUT_DIR, exist_ok=True) #make output directory if it doesn't exist

def load_parsed_resumes() -> List[Dict[str, Any]]: #load parsed resumes from JSON file
    path = os.path.join(PARSED_DIR, "all_parsed.json") #path to the JSON file
    if not os.path.exists(path): #check if the file exists
        raise FileNotFoundError("Run parse_resumes.py first to generate parsed resumes.") #raise error if file doesn't exist
    with open(path, "r", encoding="utf-8") as f: #open the file for reading
        return json.load(f) #load and return the JSON data

def build_feature_vector(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Convert parsed resume data into a structured feature vector."""
    features = {
        "file_name": parsed.get("file_name"), #get the file name
        "name": parsed.get("name"), #get the name
        "email": parsed.get("contacts", {}).get("email"), #get the email
        "phone": parsed.get("contacts", {}).get("phone"), #get the phone number
        "years_experience": parsed.get("years_experience") or 0 #get years of experience or default to 0
    }

    # Skill presence (binary features)
    skills = set(parsed.get("skills", [])) #get the set of skills
    for skill in SALESFORCE_SKILLS:
        features[f"skill_{skill}"] = 1 if skill in skills else 0 #binary feature for each skill

    return features #return the feature dictionary

def main():
    parsed_resumes = load_parsed_resumes() #load parsed resumes
    feature_vectors = [build_feature_vector(r) for r in parsed_resumes] #build feature vectors for each parsed resume

    df = pd.DataFrame(feature_vectors) #create a DataFrame from the feature vectors

    # Save as CSV + JSON
    csv_path = os.path.join(OUTPUT_DIR, "resume_features.csv") #path to save CSV file
    json_path = os.path.join(OUTPUT_DIR, "resume_features.json") #path to save JSON file

    df.to_csv(csv_path, index=False) #save DataFrame as CSV
    df.to_json(json_path, orient="records", indent=2) #save DataFrame as JSON

    print(f"Features extracted for {len(df)} resumes")
    print(f"Saved CSV: {csv_path}")
    print(f"Saved JSON: {json_path}")

if __name__ == "__main__":
    main()

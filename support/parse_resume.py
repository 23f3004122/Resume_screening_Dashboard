import os
import json
from typing import Dict, Any
from utils import (read_text_from_file, normalize_text, extract_contacts,
                   guess_name, extract_years_experience, extract_skills)

INPUT_DIR = os.path.join("data", "resumes") #directory where resumes are stored
OUTPUT_DIR = os.path.join("data", "parsed") #directory where parsed resumes will be stored

os.makedirs(OUTPUT_DIR, exist_ok=True) #make output directory if it doesn't exist

def parse_resume(file_path: str) -> Dict[str, Any]:
    """Extract structured data from a resume file."""
    try:
        text = read_text_from_file(file_path) #read text from the resume file
        text = normalize_text(text) #normalize the text

        data = {
            "file_name": os.path.basename(file_path), #just the file name, not full path
            "name": guess_name(text), #guess the name from the text
            "contacts": extract_contacts(text), #extract contacts from the text
            "years_experience": extract_years_experience(text), #extract years of experience from the text
            "skills": extract_skills(text), #extract skills from the text
            "raw_text": text[:2000]  # keep only first 2k chars to avoid huge JSON
        }
        return data
    except Exception as e:
        return {"file_name": os.path.basename(file_path), "error": str(e)}

def main():
    resumes = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith((".pdf", ".docx", ".txt"))] #list of resume files in the input directory
    all_parsed = [] #list to store all parsed resumes

    for resume in resumes:
        path = os.path.join(INPUT_DIR, resume) #full path to the resume file
        parsed = parse_resume(path) #parse the resume

        # Save individual JSON
        out_path = os.path.join(OUTPUT_DIR, f"{os.path.splitext(resume)[0]}.json") #Taking the file name without extension and adding .json
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)

        all_parsed.append(parsed)
        print(f"Parsed: {resume}")

    # Save combined JSON
    combined_path = os.path.join(OUTPUT_DIR, "all_parsed.json")
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(all_parsed, f, indent=2)

    print(f"Parsing complete. {len(all_parsed)} resumes processed.")
    print(f"Results saved in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

import os, json, csv
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity  

def read_job_description(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def load_parsed_texts(parsed_dir: str) -> List[Dict]:   # Load parsed JSON texts from a directory
    rows = []
    for fname in os.listdir(parsed_dir): # Iterate over files in the directory
        if not fname.endswith('.json'): # Skip non-JSON files
            continue
        with open(os.path.join(parsed_dir, fname), 'r', encoding='utf-8') as f: # Open each JSON file
            rec = json.load(f) # Load JSON content
        rows.append(rec) # Append the loaded record to the list
    return rows  

def compute_similarity(jd_text, resumes):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    # Treat resumes as plain text
    corpus = [jd_text] + [str(r) for r in resumes]

    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(corpus)

    # Cosine similarity between JD (first doc) and all resumes
    similarities = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()

    results = []
    for i, sim in enumerate(similarities):
        results.append({
            "resume_index": i,
            "similarity": float(sim)
        })

    return results




def bucketize(score: float) -> str: # Categorize similarity score into buckets
    if score >= 0.65:
        return "Highly Relevant"
    if score >= 0.45:
        return "Moderate"
    return "Irrelevant"     

def join_with_features(similarity_rows, features_csv):
    import pandas as pd

    try:
        features_df = pd.read_csv(features_csv)
    except FileNotFoundError:
        print("⚠️ Features CSV not found, skipping join.")
        return similarity_rows

    results = []
    for row in similarity_rows:
        # Try matching on "file", else fallback to index
        key = row.get('file', row['resume_index'])

        if 'file' in features_df.columns:
            feature_row = features_df[features_df['file'] == key]
        else:
            feature_row = features_df.iloc[[row['resume_index']]] if row['resume_index'] < len(features_df) else None

        if feature_row is not None and not feature_row.empty:
            merged = {**row, **feature_row.to_dict(orient="records")[0]}
        else:
            merged = row

        results.append(merged)

    # Rank by similarity
    results = sorted(results, key=lambda x: x['similarity'], reverse=True)
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Match and rank resumes against a job description.")
    parser.add_argument("--job_description", type=str, required=True, help="Path to the job description text file.")
    parser.add_argument("--parsed_dir", type=str, default="data/parsed", help="Directory containing parsed resume JSON files.")
    parser.add_argument("--features_csv", type=str, default="data/features/resume_features.csv", help="Path to the CSV file with extracted features.")
    parser.add_argument("--output_json", type=str, default="data/match_ranked.json", help="Output path for the ranked results JSON file.")

    args = parser.parse_args()

    jd_text = read_job_description(args.job_description) # Read job description text
    resumes = load_parsed_texts(args.parsed_dir) # Load parsed resume texts
    sim_rows = compute_similarity(jd_text, resumes) # Compute similarity scores
    ranked = join_with_features(sim_rows, args.features_csv) # Join with features and rank

    with open(args.output_json, 'w', encoding='utf-8') as f: # Write results to output JSON file
        json.dump(ranked, f, indent=2)

    print(f"Matching and ranking complete. Results saved to {args.output_json}")
    if not resumes:
        print("No resumes found in the specified directory.")
        exit(1)
import streamlit as st
import pandas as pd
import json
import os

# ---------- CONFIG ----------
RESULTS_FILE = "data/results.json"      # ✅ Now points to JSON file
PARSED_DIR = "data/parsed"              # Parsed JSON files


def load_results():
    """Load ranked results JSON (resume similarity scores)."""
    results_json = RESULTS_FILE
    if os.path.exists(results_json):
        with open(results_json, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)

        # Map resume_index -> filename (only .json parsed files)
        parsed_files = sorted([f for f in os.listdir(PARSED_DIR) if f.endswith(".json")])
        df["file"] = df["resume_index"].apply(
            lambda i: parsed_files[i] if i < len(parsed_files) else f"unknown_{i}"
        )
        return df
    else:
        return pd.DataFrame()


def load_resume_details(filename):
    """Load parsed JSON details for a given resume (expects JSON filename)."""
    filepath = os.path.join(PARSED_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="Salesforce Resume Screening", layout="wide")
st.title("📊 Automated Resume Screening Dashboard")
st.markdown("Easily explore parsed resumes and their relevance to the Salesforce Engineer job description.")


# Load data
results = load_results()

if results.empty:
    st.warning("⚠️ No results found. Please run `match_and_rank.py` first.")
else:
    # Sidebar filters
    st.sidebar.header("🔎 Filters")
    top_n = st.sidebar.slider("Number of top resumes to view:", 5, 50, 20)
    threshold = st.sidebar.slider("Minimum similarity score:", 0.0, 1.0, 0.3, 0.01)

    # Filter results
    filtered = results[results["similarity"] >= threshold].sort_values("similarity", ascending=False).head(top_n)

    st.subheader("🏆 Top Matching Resumes")
    st.dataframe(filtered[["file", "similarity"]])

    # Resume details
    st.subheader("📄 Resume Details")
    selected_file = st.selectbox("Choose a resume to view details:", filtered["file"].tolist())

    if selected_file:
        details = load_resume_details(selected_file)
        if details:
            st.markdown(f"### {details.get('name', 'Unknown Candidate')}")
            st.write(f"**Email:** {details.get('email', 'N/A')}")
            st.write(f"**Phone:** {details.get('phone', 'N/A')}")

            st.markdown("**Skills:**")
            st.write(", ".join(details.get("skills", [])))

            st.markdown("**Education:**")
            st.write(details.get("education", "N/A"))

            st.markdown("**Experience:**")
            st.write(details.get("experience", "N/A"))

            st.markdown("**Certifications:**")
            st.write(", ".join(details.get("certifications", [])))
        else:
            st.error("❌ No details found for this resume.")

    # Visualization
    st.subheader("📊 Skill Distribution")
    all_skills = []
    for f in filtered["file"].tolist():
        det = load_resume_details(f)
        all_skills.extend(det.get("skills", []))

    if all_skills:
        skills_df = pd.Series(all_skills).value_counts().reset_index()
        skills_df.columns = ["Skill", "Count"]
        st.bar_chart(skills_df.set_index("Skill"))
    else:
        st.info("No skills extracted to display.")

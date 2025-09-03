import streamlit as st
import pandas as pd
import json
import os
import subprocess

# ---------- CONFIG ----------
RESULTS_FILE = "data/results.json"      # JSON file containing ranked results
PARSED_DIR = "data/parsed"              # Parsed JSON resumes directory


def load_results():
    """Load ranked results JSON (resume similarity scores)."""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)

        # Map resume_index -> filename (from parsed dir)
        parsed_files = sorted([f for f in os.listdir(PARSED_DIR) if f.endswith(".json")])
        df["file"] = df["resume_index"].apply(
            lambda i: parsed_files[i] if i < len(parsed_files) else f"unknown_{i}"
        )
        return df
    else:
        return pd.DataFrame()


def load_resume_details(filename):
    """Load parsed JSON details for a given resume."""
    filepath = os.path.join(PARSED_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        # ✅ Handle both list & dict JSON
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        elif isinstance(data, dict):
            return data
    return {}


# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="Salesforce Resume Screening", layout="wide")
st.title("📊 Automated Resume Screening Dashboard")
st.markdown("Easily explore parsed resumes and their relevance to the Salesforce Engineer job description.")


# Sidebar filters
st.sidebar.header("🔎 Filters")
top_n = st.sidebar.slider("Number of top resumes to view:", 5, 50, 20)
threshold = st.sidebar.slider("Minimum similarity score:", 0.0, 1.0, 0.3, 0.01)

# One-click automation: Parse + Match + Rank
if st.sidebar.button("🚀 Re-parse & Rank Resumes"):
    from parse_resume import parse_resumes_batch

    try:
        # Step 1: Re-parse resumes
        parse_resumes_batch("data/resumes", "data/parsed")
        st.success("✅ Resumes re-parsed successfully.")

        # Step 2: Run matching & ranking
        subprocess.run(["python", "match_and_rank.py"], check=True)
        st.success("✅ Matching & ranking complete!")

        # Step 3: Reload results
        results = load_results()
        st.experimental_rerun()  # 🔄 Refresh dashboard with new results
    except Exception as e:
        st.error(f"❌ Automation failed: {e}")


# Load results
results = load_results()

if results.empty:
    st.warning("⚠️ No results found. Please run the automation button in the sidebar.")
else:
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
        # Handle name
        name = details.get("name")
        contacts = details.get("contacts", {})
        email = contacts.get("email", "N/A")
        phone = contacts.get("phone", "N/A")

        # Fallback: derive name from email if name is null
        if not name or name.lower() == "null":
            name = email.split("@")[0].replace(".", " ").title()

        st.markdown(f"### {name}")
        st.write(f"**Email:** {email}")
        st.write(f"**Phone:** {phone}")

        # Skills
        st.markdown("**Skills:**")
        st.write(", ".join(details.get("skills", [])))

        # Education
        st.markdown("**Education:**")
        st.write(details.get("education", "N/A"))

        # Experience
        st.markdown("**Experience:**")
        st.write(details.get("experience", "N/A"))

        # Certifications
        st.markdown("**Certifications:**")
        st.write(", ".join(details.get("certifications", [])))
    else:
        st.error("❌ No details found for this resume.")

    # Visualization
    st.subheader("📊 Skill Distribution")
    all_skills = []
    for f in filtered["file"].tolist():
        det = load_resume_details(f)
        if det:
            skills = det.get("skills", [])
            if isinstance(skills, list):
                all_skills.extend(skills)

    if all_skills:
        skills_df = pd.Series(all_skills).value_counts().reset_index()
        skills_df.columns = ["Skill", "Count"]
        st.bar_chart(skills_df.set_index("Skill"))
    else:
        st.info("No skills extracted to display.")

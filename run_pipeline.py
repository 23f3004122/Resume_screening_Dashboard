import subprocess

def run_command(command):
    print(f"\n👉 Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {command}")
        exit(1)

def main():
    # 1. Parse resumes
    run_command(
        "python support/parse_resume.py "
        "--resume_dir data/resumes "
        "--output_dir data/parsed"
    )

    # 2. Match and rank
    run_command(
    "python support/match_and_rank.py "
    "--job_description data/job_description.txt "
    "--parsed_dir data/parsed "
    "--output_json data/results.json"
)

    # 3. Launch dashboard
    print("\n✅ Pipeline finished. Launching dashboard...")
    run_command("streamlit run support/dashboard_streamlit.py")

if __name__ == "__main__":
    main()

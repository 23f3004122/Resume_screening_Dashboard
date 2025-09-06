import re
import os
from typing import List, Dict, Any

def try_import_pdf(): #Try to import pdfminer.six
    try:
        from pdfminer.high_level import extract_text as pdf_extract_text
        return pdf_extract_text
    except Exception:
        return None

def try_import_docx(): #Try to import python-docx
    try:
        import docx
        return docx
    except Exception:
        return None


# -------------------- REGEX --------------------
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")


# -------------------- STOPWORDS --------------------
STOPWORDS = set("""
a about above after again against all am an and any are aren't as at be because been before being below between both but by can't cannot
could couldn't did didn't do does doesn't doing don't down during each few for from further had hadn't has hasn't have haven't having he he'd 
he'll he's her here here's hers herself him himself his how how's i i'd i'll i'm i've if in into is isn't it it's its itself just ll ma me mightn't
more most mustn't my myself needn't no nor not of off on once only or other ought our ours ourselves out over own re s same shan't she she'd she'll 
she's should shouldn't so some such t than that that's the their theirs them themselves then there there's these they they'd they'll they're they've this
those through to too under until up ve very was wasn't we we'd we'll we're we've were weren't what what's when when's where where's which while who who's
whom why why's will with won't would wouldn't y you you'd you'll you're you've your yours yourself yourselves
""".split())


# -------------------- SKILLS --------------------
SALESFORCE_SKILLS = [
    "salesforce", "apex", "visualforce", "soql", "sosl", "lwc", "lightning", "lightning web components",
    "triggers", "flows", "process builder", "sales cloud", "service cloud", "marketing cloud",
    "community cloud", "experience cloud", "cpq", "field service", "einstein", "integration", "mulesoft",
    "heroku", "rest api", "soap api", "oauth", "salesforce admin", "platform developer", "ci/cd",
    "devops", "git", "bitbucket", "jira", "test classes", "unit testing", "sfdx", "data loader",
    "profiles", "permission sets", "sharing rules", "validation rules", "workflow", "reports", "dashboards",
    "objects", "fields", "page layouts", "record types", "approval process"
]


# -------------------- HELPERS --------------------
def read_text_from_file(path: str) -> str:
    path_lower = path.lower()
    if path_lower.endswith(".txt"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    elif path_lower.endswith(".pdf"):
        pdf_reader = try_import_pdf()
        if pdf_reader is None:
            raise ImportError("pdfminer.six is not installed. Install requirements.txt")
        return pdf_reader(path) # Extract text from PDF
    elif path_lower.endswith(".docx"):
        docx = try_import_docx()
        if docx is None:
            raise ImportError("python-docx is not installed. Install requirements.txt")
        doc = docx.Document(path) # Extract text from DOCX
        return "\n".join(p.text for p in doc.paragraphs) 
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read() # Fallback to plain text


def normalize_text(text: str) -> str: # Clean and normalize text
    text = text.replace("\x00", " ") # Remove null bytes , sometimes in PDFs
    text = re.sub(r"\s+", " ", text) # Remove extra whitespace
    return text.strip()


def tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z\-+/#]*", text.lower()) # Alphanumeric tokens with some punctuation
    return [t for t in tokens if t not in STOPWORDS] # Remove stopwords


# -------------------- EXTRACTION --------------------
def extract_contacts(text: str) -> Dict[str, Any]:
    cleaned = re.sub(r"(Email|E-mail|Mail|Phone|Mobile)[:\s]+", " ", text, flags=re.I) # Remove common prefixes , re.I for case insensitive

    emails = EMAIL_RE.findall(cleaned)
    phones = PHONE_RE.findall(cleaned)

    return {
        "email": emails[0].strip() if emails else None,
        "phone": phones[0].strip() if phones else None,
    }


def guess_name(text: str) -> str: 
    lines = text.split("\n")
    bad_headers = {"resume", "curriculum vitae", "cv", "profile", "summary"} # Common non-name headers
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # only alphabetic + space + small punctuation
        if all(c.isalpha() or c.isspace() or c in "-.'" for c in line): #This prevents names with numbers or special characters
            tokens = line.split()
            if 1 <= len(tokens) <= 4 and all(len(t) >= 1 for t in tokens):
                if line.lower() not in bad_headers:
                    return line
    return None


def extract_years_experience(text: str) -> float: # Extract years of experience, like 2 years, 3.5 years, 5+ years
    matches = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*years?", text, flags=re.I)
    if matches:
        try:
            vals = [float(m) for m in matches]
            return max(vals)
        except Exception:
            return None
    return None


def extract_skills(text: str) -> List[str]:
    found = set()
    t = text.lower()
    for skill in SALESFORCE_SKILLS:
        if skill in t:
            found.add(skill)
    return list(found)

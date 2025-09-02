import re #regular expressions
import os #operating system
from typing import List, Dict, Any

def try_import_pdf():
    try:
        from pdfminer.high_level import extract_text as pdf_extract_text #importing extract_text function from pdfminer.high_level module
        return pdf_extract_text
    except Exception:
        return None
    
def try_import_docx():
    try:
        import docx #importing docx module
        return docx
    except Exception:
        return None

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"\\+?\\d[\\d\\s().-]{7,}\\d")

STOPWORDS=set("""
a about above after again against all am an and any are aren't as at be because been before being below between both but by can't cannot
could couldn't did didn't do does doesn't doing don't down during each few for from further had hadn't has hasn't have haven't having he he'd 
he'll he's her here here's hers herself him himself his how how's i i'd i'll i'm i've if in into is isn't it it's its itself just ll ma me mightn't
more most mustn't my myself needn't no nor not of off on once only or other ought our ours ourselves out over own re s same shan't she she'd she'll 
she's should shouldn't so some such t than that that's the their theirs them themselves then there there's these they they'd they'll they're they've this
those through to too under until up ve very was wasn't we we'd we'll we're we've were weren't what what's when when's where where's which while who who's
whom why why's will with won't would wouldn't y you you'd you'll you're you've your yours yourself yourselves""".split()
)

SALESFORCE_SKILLS = [
    "salesforce", "apex", "visualforce", "soql", "sosl", "lwc", "lightning", "lightning web components",
    "triggers", "flows", "process builder", "sales cloud", "service cloud", "marketing cloud",
    "community cloud", "experience cloud", "cpq", "field service", "einstein", "integration", "mulesoft",
    "heroku", "rest api", "soap api", "oauth", "salesforce admin", "platform developer", "ci/cd",
    "devops", "git", "bitbucket", "jira", "test classes", "unit testing", "sfdx", "data loader",
    "profiles", "permission sets", "sharing rules", "validation rules", "workflow", "reports", "dashboards",
    "objects", "fields", "page layouts", "record types", "approval process"
]

def read_text_from_file(path: str) -> str:
    path_lower = path.lower()
    if path_lower.endswith('.txt'):
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    elif path_lower.endswith('.pdf'):
        pdf_reader = try_import_pdf()
        if pdf_reader is None:
            raise ImportError("pdfminer.six is not installed. Install requirements.txt")
        return pdf_reader(path)
    elif path_lower.endswith('.docx'):
        docx = try_import_docx()
        if docx is None:
            raise ImportError("python-docx is not installed. Install requirements.txt")
        doc = docx.Document(path)
        return "\\n".join(p.text for p in doc.paragraphs)
    else:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
        
def normalize_text(text: str) -> str: #function to normalize text by removing null characters and extra whitespace
    text = text.replace('\\x00', ' ') #replace null characters with space
    text = re.sub(r'\\s+', ' ', text) #replace multiple whitespace characters with a single space
    return text.strip()    
    

def tokenize(text: str) -> List[str]: #function to tokenize text into words
    tokens = re.findall(r"[A-Za-z][A-Za-z\\-\\+/#]*", text.lower()) #find all words in the text
    return [t for t in tokens if t not in STOPWORDS] #return list of tokens excluding stopwords 


def extract_contacts(text: str) -> Dict[str, Any]: #function to extract email and phone number from text
    emails = EMAIL_RE.findall(text) #find all email addresses in the text
    phones = PHONE_RE.findall(text) #find all phone numbers in the text
    return {"email": emails[0] if emails else None, "phone": phones[0] if phones else None} #return first email and phone number found, or None if not

def guess_name(text: str) -> str: #function to guess name from text
    lines = text.split('\\n') #split text into lines
    for line in lines: #iterate through each line
        line = line.strip() #strip leading and trailing whitespace
        if len(line) > 1 and all(c.isalpha() or c.isspace() or c in "-.'" for c in line): #check if line is not empty and contains only alphabetic characters, spaces, or certain punctuation
            tokens = line.split() #split line into tokens
            if 1 <= len(tokens) <= 4 and all(len(t) > 1 for t in tokens): #check if number of tokens is between 1 and 4 and all tokens are longer than 1 character
                return line #return the line as the guessed name
    return None #return None if no name is found

def extract_years_experience(text: str) -> float: #function to extract years of experience from text
    matches = re.findall(r"(\\d+(?:\\.\\d+)?)\\s*\\+?\\s*years?", text, flags=re.I) #find all occurrences of 'X years' or 'X+ years' in the text
    if matches: #if any matches are found
        try:
            vals = [float(m) for m in matches] #convert matches to float
            return max(vals) #return the maximum value found
        except Exception:
            return None #return None if conversion fails
    return None #return None if no matches are found    

def extract_skills(text: str) -> List[str]: #function to extract skills from text
    found = set() #initialize an empty set to store found skills
    t = text.lower() #convert text to lowercase
    for skill in SALESFORCE_SKILLS: #iterate through each skill in the predefined list
        if skill in t: #if the skill is found in the text
            found.add(skill) #add the skill to the set of found skills
    return list(found) #return the list of found skills 

from utils import guess_name, extract_contacts

sample = """Vihaan Sharma
Email: vihaan.sharma@example.com | Phone: +91-9896233790
"""

print("Name →", guess_name(sample))
print("Contacts →", extract_contacts(sample))

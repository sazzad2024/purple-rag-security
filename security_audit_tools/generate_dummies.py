from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_dummy_pdf(filename, title, content):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 720, title)
    c.setFont("Helvetica", 12)
    y = 700
    for line in content:
        c.drawString(72, y, line)
        y -= 20
    c.save()
    print(f"Created {filename}")

documents = [
    {
        "file": "nist_csf_2.0.pdf",
        "title": "NIST Cybersecurity Framework 2.0 (DUMMY)",
        "content": [
            "GOVERN (GV): The organization's cybersecurity risk management strategy is established.",
            "IDENTIFY (ID): The current cybersecurity risks are understood.",
            "PROTECT (PR): Safeguards to ensure delivery of critical infrastructure services.",
            "DETECT (DE): Develop and implement appropriate activities to identify the occurrence of a cybersecurity event.",
            "RESPOND (RS): Develop and implement appropriate activities to take action regarding a detected cybersecurity incident.",
            "RECOVER (RC): Develop and implement appropriate activities to maintain plans for resilience."
        ]
    },
    {
        "file": "CIS_Controls_v8_Guide.pdf",
        "title": "CIS Critical Security Controls v8 (DUMMY)",
        "content": [
            "Control 1: Inventory and Control of Enterprise Assets",
            "Control 2: Inventory and Control of Software Assets",
            "Control 3: Data Protection",
            "Control 4: Secure Configuration of Enterprise Assets and Software",
            "Control 5: Account Management"
        ]
    },
    {
        "file": "hipaa.pdf",
        "title": "HIPAA Security Rule (DUMMY)",
        "content": [
            "§ 164.306 Security standards: General rules.",
            "(1) Ensure the confidentiality, integrity, and availability of all electronic protected health information.",
            "(2) Protect against any reasonably anticipated threats or hazards to the security or integrity of such information."
        ]
    },
    {
        "file": "PCI-DSS-v4_0_1.pdf",
        "title": "PCI DSS v4.0.1 (DUMMY)",
        "content": [
            "Requirement 1: Install and Maintain Network Security Controls",
            "Requirement 2: Apply Secure Configurations to All System Components",
            "Requirement 3: Protect Stored Account Data",
            "Requirement 4: Protect Cardholder Data with Strong Cryptography"
        ]
    }
]

# Create them in the victim directory
target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'multi-framework-compliance-assistant'))

for doc in documents:
    path = os.path.join(target_dir, doc["file"])
    create_dummy_pdf(path, doc["title"], doc["content"])

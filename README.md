# Document Information Extractor
A Python script that extracts structured information from documents (PDF, TXT, DOCX) and returns the data in clean JSON format.
## Features
- **Multi-format Support**: Reads PDF, TXT, and DOCX files
- **Field Extraction**: Extracts name, email,phone,policy_number,plan_name,sum_assured,room_rent_limit,waiting_period,issued_date,
expiry_date,
- **Regex-based Parsing**: Uses robust regex patterns for field extraction
- **Named Entity Recognition**: Optional spaCy integration for advanced NLP
- **Clean JSON Output**: Returns structured data in JSON format
- **Error Handling**: Comprehensive error handling 
## Installation
1. Install required dependencies:
```bash
pip install -r requirements.txt
```
2. (Optional) Install spaCy model for NER functionality:
```bash
python -m spacy download en_core_web_lg
```
## Usage
### Command Line Interface
```bash
# Basic extraction
python main.py sample_insurance_policy.txt
# With Named Entity Recognition
python main.py sample_insurance_policy.txt --use-ner
```
### Programmatic Usage
```python
from main import DocumentInfoExtractor
# Create extractor
extractor = DocumentInfoExtractor(use_ner=True)
# Extract information
result = extractor.extract_from_file("path/to/document.pdf")
print(result)
```
### Testing
Run the test script to see the extractor in action:
```bash
python test.py
```
## Expected Output
```json
{
  "name": "Rahul Sharma",
  "email": "rahul.sharma@email.com",
  "phone": "+91-9876543210",
  "policy_number": "ABC12345",
  "plan_name": "Health Secure Plus",
  "sum_assured": 500000,
  "room_rent_limit": 5000,
  "waiting_period": "2 years for pre-existing diseases",
  "issued_date": "01-Aug-2023",
  "expiry_date": "31-Jul-2024",
  "ner_entities": {
    "NAME": [
      "Rahul Sharma"
    ],
    "EMAIL": [],
    "PHONE": [],
    "ORG": [],
    "policy_number": [],
    "plan_name": [],
    "sum_assured": [],
    "room_rent_limit": [],
    "waiting_period": [],
    "issued_date": [],
    "expiry_date": []
  }
}
```
## Dependencies
- PyPDF2: PDF text extraction
- python-docx: DOCX text extraction
- spacy: Named Entity Recognition (optional)
- regex: Advanced regex patterns

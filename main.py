import re
import json 
import PyPDF2
from pathlib import Path
from docx import Document 
import spacy 
from typing import Dict, Optional, List 



class DocumentReader:
    
    def read_pdf(self,file_path:str) ->str:
        try:
            with open(file_path,'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text+=page.extract_text() +"\n\n\n"
                return text 
            
        except Exception as e:
            print(f"There is error while reading pdf {file_path}:{e}")
            
            
    def read_text(self,file_path:str)->str:
        try:
            with open(file_path,'r',encoding='utf-8')  as file:
                return file.read()
        except Exception as e:
            print(f"Error reading text file {file_path}: {e}")
            
            
    def read_docx(self,file_path:str) -> str:
        try:
            docs = Document(file_path)
            text = ""
            for para in docs.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e: 
            print(f"Error reading Docx file {file_path} :{e}")
            
            
            
    def read_document(self,file_path:str)->str:
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found : {file_path}")
        
        
        extension = file_path.suffix.lower()
        if extension=='.pdf':
            return self.read_pdf(str(file_path))
        elif extension=='.txt':
            return self.read_text(str(file_path))
        
        elif extension=='.docx':
            return self.read_docx(str(file_path))
        
        else:
            raise ValueError(f"unsupported file format {extension}")
        
    

class ImportantFieldExtractor:
    def __init__(self):
        self.patterns = {
            'name': [
                r'(?:Name|Full Name|Policyholder|Insured):\s*([A-Za-z\s]+?)(?:\s+Email|\s*$)',
                r'^([A-Za-z\s]+?)(?:\s+Email|\s*$)'
            ],
            'email': [
                r'(?:Email|E-mail|Email Address):\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            ],
            'phone': [
                r'(?:Phone|Phone Number|Mobile|Contact):\s*([+]?[\d\s\-\(\)]+)',
                r'([+]?[\d\s\-\(\)]{10,})'
            ],
            'policy_number': [
                r'(?:Policy Number|Policy No|Policy ID|Policy):\s*([A-Za-z0-9]+)',
                r'([A-Z]{2,}\d{3,})'
            ],
           'plan_name': [
                r'Plan Name:\s*([A-Za-z\s]+?)(?=\n|$)',
                r'Insurance Plan:\s*([A-Za-z\s]+?)(?=\n|$)'
            ],
            'sum_assured': [
                r'Sum Assured:\s*[■$]?\s*([\d,]+)',
                r'Coverage Amount:\s*[■$]?\s*([\d,]+)'
            ],
            'room_rent_limit': [
                r'Room Rent Limit:\s*[■$]?\s*([\d,]+)\/day',
                r'Room Rent:\s*[■$]?\s*([\d,]+)\/day'
            ],
            'waiting_period': [
                r'Waiting Period:\s*([^\n]+)',
                r'Pre-existing Diseases?:\s*([^\n]+)',
                r'Pre-existing Disease Waiting:\s*([^\n]+)'
            ],
            'issued_date': [
                r'Issued Date:\s*([\d]{2}-[A-Za-z]{3}-[\d]{4})',
                r'Issue Date:\s*([\d]{2}-[A-Za-z]{3}-[\d]{4})'
            ],
            'expiry_date': [
                r'Expiry Date:\s*([\d]{2}-[A-Za-z]{3}-[\d]{4})',
                r'Valid Till:\s*([\d]{2}-[A-Za-z]{3}-[\d]{4})'
            ]
        }

    def extract_field(self, text: str, field_name: str):
        patterns = self.patterns.get(field_name, [])
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                return self._clean_input(value, field_name)
        return None

    def _clean_input(self, value: str, field_name: str) -> str:
        cleaners = {
            'name': lambda v: ' '.join(v.split()).title(),
            'email': lambda v: v.lower().strip(),
            'phone': lambda v: v.strip(),
            'policy_number': lambda v: v.upper().strip(),
            'plan_name': lambda v: v.strip().title(),
            'sum_assured': lambda v: int(v.replace(',', '').strip()),
            'room_rent_limit': lambda v: int(v.replace(',', '').strip()),
            'waiting_period': lambda v: v.strip(),
            'issued_date': lambda v: v.strip(),
            'expiry_date': lambda v: v.strip()
        }
        return cleaners.get(field_name, lambda v: v.strip())(value)

    def extract_all_fields(self, text: str):
        return {field: self.extract_field(text, field) for field in self.patterns}

    
    
    
class NERFieldExtractor:
    
    def __init__(self):
        try:
            self.nlp = spacy.load('en_core_web_lg')
        except OSError:
            print("Model 'en_core_web_lg' not found. ")
            self.nlp = None
            
    def extract_entities(self, text: str):
        if not self.nlp:
            return {}
        
        doc = self.nlp(text)
        entities = {
            'NAME': [],
            'EMAIL': [],
            'PHONE': [],
            'ORG': [],
            'policy_number': [],
            'plan_name': [],
            'sum_assured': [],
            'room_rent_limit': [],
            'waiting_period': [],
            'issued_date': [],
            'expiry_date': []
        }
        
        for ent in doc.ents: 
            if ent.label_ in ['PERSON', 'ORG']:
                if ent.label_=="PERSON":                                    
                    if '\n' in ent.text.strip():
                        entities["NAME"].append(ent.text.strip().split('\n')[0])
                    else:
                        entities["NAME"].append(ent.text.strip())
                else:
                    entities[ent.label_].append(ent.text.strip())
        
        return entities
    
class DocumentInfoExtractor:
    
    def __init__(self, use_ner: bool = False):
        self.reader = DocumentReader()
        self.extractor = ImportantFieldExtractor()
        self.ner_extractor = NERFieldExtractor() if use_ner else None
    
    def extract_from_file(self, file_path: str) -> Dict:
        try:
            # Read document
            text = self.reader.read_document(file_path)
            if not text:
                return {"error": "Could not extract text from document. Not able to find text from document"}
            
            extracted_fields = self.extractor.extract_all_fields(text)
            
            result = {
                "name": extracted_fields.get('name'),
                "email": extracted_fields.get('email'),
                "phone": extracted_fields.get('phone'),
                "policy_number": extracted_fields.get('policy_number'),
                "plan_name": extracted_fields.get('plan_name'),
                "sum_assured": extracted_fields.get('sum_assured'),
                "room_rent_limit": extracted_fields.get('room_rent_limit'),
                "waiting_period": extracted_fields.get('waiting_period'),
                "issued_date": extracted_fields.get('issued_date'),
                "expiry_date": extracted_fields.get('expiry_date')
            }
            
            if self.ner_extractor:
                ner_entities = self.ner_extractor.extract_entities(text)                
                result["ner_entities"] = ner_entities            
            return result
            
        except Exception as e:
            print(f"Error processing document {file_path}: {e}")
            return {"error": str(e)}

def main():
    import sys
    
    if len(sys.argv) < 2:
        return
    
    file_path = sys.argv[1]
    use_ner = "--use-ner" in sys.argv
    extractor = DocumentInfoExtractor(use_ner=use_ner)
    
    result = extractor.extract_from_file(file_path)
    
    print(json.dumps(result, indent=2))
 
 
if __name__ == "__main__":
    main()
        
        
            
import json
from main import DocumentInfoExtractor
 
def test_extraction():
    print("=== Testing with Regex Extraction ===")
    extractor_regex = DocumentInfoExtractor(use_ner=False)
    result_regex = extractor_regex.extract_from_file("data/sample_insurance_doc .pdf")
    print("Regex Extraction Result:")
    print(json.dumps(result_regex, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    print("=== Testing with NER Extraction ===")
    extractor_ner = DocumentInfoExtractor(use_ner=True)
    result_ner = extractor_ner.extract_from_file("data/sample_insurance_doc .pdf")
    print("NER Extraction Result:")
    print(json.dumps(result_ner, indent=2))
 
if __name__ == "__main__":
    test_extraction()
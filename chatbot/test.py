import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF using PyMuPDF."""
    try:
        document = fitz.open(pdf_path)
        text = "\n".join([page.get_text("text") for page in document])  # Ensure we extract readable text
        document.close()
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error reading {pdf_path}: {e}")

# Test with one PDF
pdf_path = "./pdfs/CV-Dr.-Nadeem-Majeed.pdf"  # Change to an actual PDF path
extracted_text = extract_text_from_pdf(pdf_path)

if extracted_text:
    print("✅ Text extracted successfully!")
    print(extracted_text[:500])  # Print the first 500 characters
else:
    print("❌ No text extracted!")
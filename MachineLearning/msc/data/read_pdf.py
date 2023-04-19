import re
from pypdf import PdfReader

def read_pdf(file_path):
    reader = PdfReader(file_path)                                   # Read the PDF file using PdfReader
    pages = []                                                      # Initialize an empty list to store processed pages
    for page in reader.pages:                                       # Iterate through each page in the PDF
        page_raw = page.extract_text()                              # Extract raw text from the page
        page_processed = re.sub('[^a-zA-ZæøåÆØÅ.]+', ' ', page_raw) # Replace non-alphabetic characters with space
        page_processed = re.sub(r'\s+\.', '.', page_processed)      # Remove spaces before periods
        pages.append(page_processed)                                # Add the processed page to the list of processed pages
    return pages                                                    # Return the list of processed pages

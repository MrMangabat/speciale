## Generate summary datasets from data/pdf folder
import os
import json

from msc.data.read_pdf import read_pdf
from msc.data.get_summary_openai import get_summary
from msc.utils.utility import get_root_path


def main():
    pdf_folder = os.path.join(get_root_path(), 'data', 'pdf')       # Set the path to the PDF folder
    for pdf in os.listdir(pdf_folder):                              # Iterate through each PDF file in the PDF folder
        processed_pdf = process_pdf(os.path.join(pdf_folder, pdf))  # Process the PDF using the process_pdf function
        # Save to json
        with open(os.path.join(get_root_path(), 'data', 'json', f'{processed_pdf["file_name"]}.json'.strip()), 'w') as f: # Construct the path to the JSON file and open it for writing
            json.dump(processed_pdf, f, indent=4)                                                                         # Write the processed PDF data to the JSON file with indentation
        print(f'Processed {pdf} and saved to json file')                                                                  # Print a message indicating that the PDF has been processed and saved to a JSON file
        # move PDF to data/processed_pdf
        os.rename(os.path.join(pdf_folder, pdf), os.path.join(get_root_path(), 'data', 'processed_pdf', pdf))   # Move the processed PDF to the processed_pdf folder
        print(f'Moved {pdf} to processed_pdf folder')                                                           # Print a message indicating that the PDF has been moved to the processed_pdf folder


def process_pdf(pdf_path):
    file_name = os.path.basename(pdf_path).strip(".pdf")                        # Extract the file name from the PDF path and remove the ".pdf" extension
    pages = read_pdf(pdf_path)                                                  # Read the PDF and get its content as pages
    summary = get_summary(pages)                                                # Generate a summary from the pages
    return {"text": ''.join(pages), "summary": summary, "file_name": file_name} # Return a dictionary containing the text, summary, and file name

    
if __name__ == '__main__':
    main()

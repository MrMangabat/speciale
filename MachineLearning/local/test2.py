import os

from msc.data.read_pdf import read_pdf
from msc.utils.utility import get_root_path
from msc.data.get_summary_openai import get_summary

root = get_root_path()
pdf_folder = os.path.join(root, 'data', 'pdf')
pdf = os.path.join(pdf_folder, os.listdir(pdf_folder)[0])
page_raw = read_pdf(pdf)

summary = get_summary(page_raw)
print(summary)

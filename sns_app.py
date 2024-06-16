import streamlit as st
import os
import re
from PyPDF2 import PdfReader, PdfWriter

def find_invoice_pages(reader, start_page):
    invoice_pages = []
    current_page = start_page -1
    page_text = reader.pages[current_page].extract_text()
    match = re.search(r'Page (\d+) of (\d+)', page_text)
    if match:
        current_invoice_page, total_invoice_pages = map(int, match.groups())
        for i in range(current_page, current_page + total_invoice_pages):
            invoice_pages.append(i)
        current_page += total_invoice_pages
    return invoice_pages

def extract_employee_invoice(pdf_file, start_page, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    prefixes = ["MR", "MRS", "MISS", "MS"]
    saved_files_info = {}

    with open(pdf_file, 'rb') as f:
        reader = PdfReader(f)

        if start_page >= len(reader.pages):
            st.error("Start page is out of range.")
            return

        current_page = start_page
        while current_page < len(reader.pages):
            page_text = reader.pages[current_page].extract_text()
            employee_name = None
            for prefix in prefixes:
                match = re.search(r'{}\.?\s\S+\s\S+'.format(prefix), page_text)
                if match:
                    employee_name = match.group()
                    break
            if not employee_name:
                match = re.search(r'\b(MARTIN MURRAY|DONALD PETTIGREW)\b', page_text)
                if match:
                    employee_name = match.group()

            if employee_name:
                invoice_pages = find_invoice_pages(reader, current_page)

                employee_pdf = PdfWriter()
                for page_num in invoice_pages:
                    employee_pdf.add_page(reader.pages[page_num])

                output_filename = os.path.join(output_folder, '{}.pdf'.format(employee_name))
                with open(output_filename, 'wb') as output_file:
                    employee_pdf.write(output_file)

                saved_files_info[employee_name] = saved_files_info.get(employee_name, 0) + 1
                unique_names_count = len(saved_files_info)

                current_page += len(invoice_pages)
            else:
                break

            start_page = current_page + 1

    return saved_files_info

def main():
    st.title("PDF Invoice Extractor")
    st.sidebar.header("Settings")
    input_pdf_file = st.sidebar.file_uploader("Upload PDF file")
    start_page = st.sidebar.number_input("Start Page", value=1)
    output_folder = "./output"  # You can change this to wherever you want to save the output PDFs

    if st.sidebar.button("Extract Invoices"):
        if input_pdf_file is not None:
            saved_files_info = extract_employee_invoice(input_pdf_file, start_page, output_folder)
            st.success("Invoices extracted successfully!")
            st.write("Information of files saved for each employee:", saved_files_info)
        else:
            st.error("Please upload a PDF file.")

if __name__ == "__main__":
    main()

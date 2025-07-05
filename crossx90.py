import pypdf
import re
import csv
import os

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from all pages of a PDF file.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF.
    """
    if not os.path.exists(pdf_path):
        return f"Error: The file '{pdf_path}' was not found."

    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"An error occurred while reading the PDF: {e}"

def parse_securities_data(pdf_text):
    """
    Parses the text of the 13F securities list to extract tabular data.

    Args:
        pdf_text (str): The text extracted from the PDF.

    Returns:
        list: A list of dictionaries, where each dictionary represents a security.
    """
    data = []
    last_cusip_base = ""
    last_check_digit = ""

    # Regex to find all content within double quotes on a line
    quote_pattern = re.compile(r'"(.*?)"')

    lines = pdf_text.split('\n')

    for line in lines:
        line = line.strip()
        if not line or 'Run Date:' in line or 'CUSIP NO' in line or '** List of Section 13F Securities **' in line:
            continue

        parts = quote_pattern.findall(line)
        
        if not parts:
            continue

        try:
            # A main entry has a CUSIP prefix with a space, e.g., "B38564 10 "
            if ' ' in parts[0] and len(parts[0].strip().replace(' ', '')) == 8:
                cusip_part1 = parts[0].strip().replace(' ', '')
                last_cusip_base = cusip_part1[:6]
                
                check_digit_part = parts[1].strip()
                # The check digit is the first numeric character
                check_digit_match = re.search(r'\d', check_digit_part)
                if check_digit_match:
                    last_check_digit = check_digit_match.group(0)
                
                cusip = cusip_part1 + last_check_digit
                issuer_name = parts[2].strip()
                issuer_desc = parts[3].strip()
                status = parts[4].strip() if len(parts) > 4 else ""
            # An option entry might start with a 2-digit number
            elif parts[0].strip().isdigit() and len(parts[0].strip()) <= 2 and last_cusip_base:
                cusip_part2 = parts[0].strip()
                # The check digit is often inherited from the parent security
                cusip = last_cusip_base + cusip_part2 + last_check_digit
                issuer_name = parts[1].strip()
                issuer_desc = parts[2].strip()
                status = parts[3].strip() if len(parts) > 3 else ""
            else:
                # Skip lines that do not match the expected patterns
                continue

            data.append({
                'Cusip': cusip,
                'issuer name': issuer_name,
                'issuer description': issuer_desc,
                'status': status
            })
        except IndexError:
            # This will catch lines that don't have the expected number of parts
            print(f"Warning: Could not parse line: {line}")
            continue
            
    return data

def write_to_csv(data, filename="extracted_data.csv"):
    """
    Writes the extracted data to a CSV file.

    Args:
        data (list): A list of dictionaries to write to the CSV.
        filename (str): The name of the output CSV file.
    """
    if not data:
        print("No data was extracted to write to CSV.")
        return

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Cusip', 'issuer name', 'issuer description', 'status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in data:
                writer.writerow(row)
        print(f"Successfully extracted data to '{filename}'")
    except IOError as e:
        print(f"Error writing to CSV file: {e}")

def main():
    """
    Main function to extract, parse, and save the securities data.
    """
    pdf_path = "13flist2025q2.pdf"
    
    # Step 1: Extract text from the PDF
    print(f"Extracting text from '{pdf_path}'...")
    pdf_text = extract_text_from_pdf(pdf_path)
    
    if "Error:" in pdf_text:
        print(pdf_text)
        return

    # Step 2: Parse the extracted text
    print("Parsing securities data...")
    extracted_data = parse_securities_data(pdf_text)

    # Step 3: Write the parsed data to a CSV file
    print("Writing data to CSV...")
    write_to_csv(extracted_data)

if __name__ == "__main__":
    # Before running, ensure you have pypdf installed:
    # pip install pypdf
    main()

import os
import xml.etree.ElementTree as ET
from datetime import datetime

def process_dtsx_files(input_folder, output_file):
    """
    Process all .dtsx files in the input folder and combine their full XML contents into a single output file.
    
    Args:
        input_folder (str): Path to the folder containing .dtsx files
        output_file (str): Path to the output file where combined content will be written
    """
    # Get all .dtsx files in the input folder
    dtsx_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.dtsx')]
    
    if not dtsx_files:
        print(f"No .dtsx files found in {input_folder}")
        return
    
    # Create the output file
    with open(output_file, 'w', encoding='utf-8') as out_f:
        # Write header
        out_f.write(f"COMBINED SSIS PACKAGES - FULL XML CONTENT\n")
        out_f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out_f.write(f"Source folder: {os.path.abspath(input_folder)}\n")
        out_f.write(f"Total packages found: {len(dtsx_files)}\n")
        out_f.write("=" * 100 + "\n\n")
        
        # Process each file
        for filename in dtsx_files:
            file_path = os.path.join(input_folder, filename)
            try:
                # Write file header
                out_f.write(f"SSIS PACKAGE: {filename}\n")
                out_f.write(f"FILE PATH: {os.path.abspath(file_path)}\n")
                out_f.write(f"FILE SIZE: {os.path.getsize(file_path)} bytes\n")
                out_f.write(f"LAST MODIFIED: {datetime.fromtimestamp(os.path.getmtime(file_path))}\n")
                out_f.write("-" * 100 + "\n")
                
                # Read the file content as text first to preserve original formatting
                with open(file_path, 'r', encoding='utf-8') as xml_file:
                    xml_content = xml_file.read()
                
                # Write the raw XML content
                out_f.write("FULL XML CONTENT:\n")
                out_f.write(xml_content + "\n")
                
                # Optional: Add pretty-printed XML (from parsed tree)
                try:
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    out_f.write("\nPRETTY-PRINTED XML (for reference):\n")
                    out_f.write("-" * 50 + "\n")
                    ET.indent(tree, space="  ", level=0)
                    out_f.write(ET.tostring(root, encoding='unicode') + "\n")
                except Exception as parse_error:
                    out_f.write(f"\nCould not pretty-print XML: {str(parse_error)}\n")
                
                out_f.write("\n" + "=" * 100 + "\n\n")
                print(f"Processed: {filename}")
                
            except Exception as e:
                out_f.write(f"ERROR PROCESSING {filename}: {str(e)}\n\n")
                print(f"Error processing {filename}: {str(e)}")
    
    print(f"\nSuccessfully processed {len(dtsx_files)} package(s). Output written to {output_file}")

if __name__ == "__main__":
    # Configuration - modify these paths as needed
    INPUT_FOLDER = "path/to/your/ssis/packages"  # Folder containing .dtsx files
    OUTPUT_FILE = "combined_ssis_full_xml.txt"    # Output file name
    
    # Ensure input folder exists
    if not os.path.exists(INPUT_FOLDER):
        print(f"Error: Input folder '{INPUT_FOLDER}' does not exist.")
    else:
        process_dtsx_files(INPUT_FOLDER, OUTPUT_FILE)

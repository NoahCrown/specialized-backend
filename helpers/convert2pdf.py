import subprocess
import platform
import os

def convert_to_pdf(input_file_path):
    """
    Converts a document to PDF using LibreOffice's command line interface.
    Args:
        input_file_path (str): The path to the input file (DOC, DOCX, etc.)
    Returns:
        str: The path to the converted PDF file.
    """
    base_path = os.path.abspath(os.path.dirname(__file__))
    output_directory = base_path  # Save the converted file in the same directory as the script
    input_file_name = os.path.basename(input_file_path)
    
    # Naming the output PDF file based on the input file but with .pdf extension
    pdf_file_name = os.path.splitext(input_file_name)[0] + '.pdf'
    pdf_file_path = os.path.join(output_directory, pdf_file_name)
    
    # Ensure the `soffice` path is correct for your OS and LibreOffice installation
    libreoffice_exec = get_libreoffice_executable()  # Adjust this function to get the correct path

    # Constructing the conversion command
    cmd = [
        libreoffice_exec,
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', output_directory,
        input_file_path
    ]

    try:
        # Execute the conversion command
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"Conversion successful: '{input_file_path}' to PDF.")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        raise

    return pdf_file_path

def get_libreoffice_executable():
    """
    Determine the path to the LibreOffice executable depending on the operating system.
    """
    if platform.system() == "Windows":
        return r"C:\Program Files\LibreOffice\program\soffice.exe"
    elif platform.system() == "Linux":
        return "/usr/bin/libreoffice"  # Default path on many Linux distributions
    else:
        raise OSError("Unsupported operating system")
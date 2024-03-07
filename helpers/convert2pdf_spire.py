from spire.doc import *
from spire.doc.common import *

def convert_to_pdf(input_file_path):

    base_path = os.path.abspath(os.path.dirname(__file__))
    output_directory = base_path  # Save the converted file in the same directory as the script
    input_file_name = os.path.basename(input_file_path)
    
    # Naming the output PDF file based on the input file but with .pdf extension
    pdf_file_name = os.path.splitext(input_file_name)[0] + '.pdf'
    pdf_file_path = os.path.join(output_directory, pdf_file_name)        
    # Create a Document object
    document = Document()
    # Load a Word DOCX file
    document.LoadFromFile(input_file_path)
    # Or load a Word DOC file
    #document.LoadFromFile("Sample.doc")

    # Save the file to a PDF file
    document.SaveToFile(pdf_file_path, FileFormat.PDF)
    document.Close()

    return pdf_file_path

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx', 'doc'}
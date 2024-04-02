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
    parameter = ToPdfParameterList()
    fonts = []
    fonts.append(PrivateFontPath("NotoSansJP",FontStyle.Regular,os.path.join(output_directory,".fonts/NotoSansJP-VariableFont_wght.ttf")))
    fonts.append(PrivateFontPath("NotoSansHK",FontStyle.Regular,os.path.join(output_directory,".fonts/NotoSansHK-VariableFont_wght.ttf")))
    fonts.append(PrivateFontPath("NotoSansKR",FontStyle.Regular,os.path.join(output_directory,".fonts/NotoSansKR-VariableFont_wght.ttf")))
    fonts.append(PrivateFontPath("NotoSansSC",FontStyle.Regular,os.path.join(output_directory,".fonts/NotoSansSC-VariableFont_wght.ttf")))
    fonts.append(PrivateFontPath("NotoSansTC",FontStyle.Regular,os.path.join(output_directory,".fonts/NotoSansTC-VariableFont_wght.ttf")))
    fonts.append(PrivateFontPath("NotoSansThai",FontStyle.Regular,os.path.join(output_directory,".fonts/NotoSansThai-VariableFont_wght.ttf")))
    fonts.append(PrivateFontPath("Arial",FontStyle.Regular,os.path.join(output_directory,".fonts/arial.ttf")))
    fonts.append(PrivateFontPath("MS Gothic",FontStyle.Regular,os.path.join(output_directory,".fonts/MS Gothic.ttf")))
    fonts.append(PrivateFontPath("Microsoft YaHei UI",FontStyle.Regular,os.path.join(output_directory,".fonts/MicrosoftYaHeiUI.ttf")))
    fonts.append(PrivateFontPath("SimSun",FontStyle.Regular,os.path.join(output_directory,".fonts/SimSun.ttf")))
    fonts.append(PrivateFontPath("Times New Roman",FontStyle.Regular,os.path.join(output_directory,".fonts/Times New Roman.ttf")))

    parameter.PrivateFontPaths = fonts
    # Embed fonts in PDF
    parameter.IsEmbeddedAllFonts = True
    parameter.UsePSCoversion = True
    document.SaveToFile(pdf_file_path, FileFormat.PDF)
    document.Dispose()
    document.Close()

    return pdf_file_path

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx', 'doc'}
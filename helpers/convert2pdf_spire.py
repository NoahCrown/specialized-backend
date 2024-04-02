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
    document.EmbedFontsInFile = True
    document.PrivateFontList.append(PrivateFontPath(fontName="NotoSansJP",fontPath=os.path.join(output_directory,".fonts/NotoSansJP-VariableFont_wght.ttf")))
    document.PrivateFontList.append(PrivateFontPath(fontName="NotoSansHK",fontPath=os.path.join(output_directory,".fonts/NotoSansHK-VariableFont_wght.ttf")))
    document.PrivateFontList.append(PrivateFontPath(fontName="NotoSansKR",fontPath=os.path.join(output_directory,".fonts/NotoSansKR-VariableFont_wght.ttf")))
    document.PrivateFontList.append(PrivateFontPath(fontName="NotoSansSC",fontPath=os.path.join(output_directory,".fonts/NotoSansSC-VariableFont_wght.ttf")))
    document.PrivateFontList.append(PrivateFontPath(fontName="NotoSansTC",fontPath=os.path.join(output_directory,".fonts/NotoSansTC-VariableFont_wght.ttf")))
    document.PrivateFontList.append(PrivateFontPath(fontName="NotoSansThai",fontPath=os.path.join(output_directory,".fonts/NotoSansThai-VariableFont_wght.ttf")))
    document.PrivateFontList.append(PrivateFontPath(fontName="Arial",fontPath=os.path.join(output_directory,".fonts/arial.ttf")))
    document.PrivateFontList.append(PrivateFontPath(fontName="MS Gothic",fontPath=os.path.join(output_directory,".fonts/MS Gothic.ttf")))
    document.PrivateFontList.append(PrivateFontPath(fontName="Microsoft YaHei UI",fontPath=os.path.join(output_directory,".fonts/MicrosoftYaHeiUI.ttf")))
    document.PrivateFontList.append(PrivateFontPath(fontName="SimSun",fontPath=os.path.join(output_directory,".fonts/SimSun.ttf")))
    document.PrivateFontList.append(PrivateFontPath(fontName="Times New Roman",fontPath=os.path.join(output_directory,".fonts/Times New Roman.ttf")))

    # Embed fonts in PDF
    parameter.IsEmbeddedAllFonts = True
    parameter.UsePSCoversion = True
    document.SaveToFile(pdf_file_path, FileFormat.PDF)
    document.Dispose()
    document.Close()

    return pdf_file_path

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx', 'doc'}
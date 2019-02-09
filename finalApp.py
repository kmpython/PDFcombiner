from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os
import shutil
import time

TEMP_DIR = os.path.join('./TempDirForPdfs/')
INPUT = os.path.join('.')

def retrieve_pdfs_to_combine():
    pdf_list = []

    for item in os.listdir(INPUT):
        if item.endswith('.pdf'):
            pdf_list.append(item)

    #if os.path.isdir('./TempDirForPdfs'):
    if os.path.isdir(TEMP_DIR):
        print("Temp directory already exists. It will be overridden !")
        shutil.rmtree(TEMP_DIR)
        os.mkdir(TEMP_DIR)
    else:
        os.mkdir(TEMP_DIR)
        time.sleep(5)

    return pdf_list


def perform_pdf_validations(pdf_lst):
    print("Validating files")
    file_position_list = []
    position_count_dict = {}
    abend_flag = False

    for pdf in pdf_lst:
        try:
            position , title = pdf.split('_')
            file_position_list.append(position)
        except:
            print("{0} title is invalid format. Correct format is XX_title-name-here.pdf".format(pdf))
            abend_flag = True

    for position in file_position_list:
        position_count_dict[position] = position_count_dict.get(position, 0) + 1

    for key , value in position_count_dict.items():
        if value > 1:
            print("position {0} conflict between  {1} files ".format(key, value))
            abend_flag = True
        else:
            continue

    if abend_flag:
        print("pdf title names and position validation failed ! check log for more details")
        exit(1)
    else:
        print("Looks good !")


def attach_page_numbers(pdf, output, current_page_num):

    print("Processing {0} file".format(pdf))

    existing_pdf = PdfFileReader(open(pdf, "rb") , strict=False)
    page_count_for_pdf = existing_pdf.getNumPages()

    for i in range(0, page_count_for_pdf):
        page = existing_pdf.getPage(i)
        size = page.mediaBox
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(int(size[2]) - 40, 15, str(current_page_num).zfill(4))
        can.save()
        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        current_page_num += 1

        # add the "watermark" (which is the new pdf) on the existing page
        page.mergePage(new_pdf.getPage(0))
        output.addPage(page)

    print("process success")

    return (output , current_page_num)


def generate_content_page(index_list):

    print("generating content page canvas")

    height = 700
    #content_canvas = canvas.Canvas(".\\TempDirForPdfs\\content.pdf", pagesize=letter)
    #content_canvas = canvas.Canvas(os.path.join('./TempDirForPdfs/CONTENT.pdf'), pagesize=letter)
    content_canvas = canvas.Canvas(os.path.join(TEMP_DIR, 'CONTENT.pdf'), pagesize=letter)
    content_canvas.drawCentredString(320, 750, "CONTENTS")

    for namepage in index_list:
        title_detl, page = namepage
        srno, title_name = title_detl.split('_')
        content_canvas.drawString(10, height, str(srno + ' ' + title_name + '..........' + str(page)))
        height -= 20

    print("content page canvas generated")

    return content_canvas


def merge_all_pdfs(contentCanvas , FinalPdfOutputStream):

    print("creating merged pdf")
    outputStream = open(os.path.join(TEMP_DIR, 'MERGED.pdf') , 'wb')
    FinalPdfOutputStream.write(outputStream)
    outputStream.close()
    print("merged pdf created")

    print("generating content pdf")
    contentCanvas.save()
    print("content pdf created")

    merger = PdfFileMerger()

    for generated_pdfs in [os.path.join(TEMP_DIR, 'CONTENT.pdf'), os.path.join(TEMP_DIR, 'MERGED.pdf')]:
        merger.append(generated_pdfs)

    return merger


def main():
    FinalOutputStream = PdfFileWriter()
    start_page_num = 1
    index_list = []

    pdf_lst = retrieve_pdfs_to_combine()

    perform_pdf_validations(pdf_lst)

    for pdf in pdf_lst:
        index_list.append((pdf, start_page_num))
        intermOutputStream, ending_page_num = attach_page_numbers(pdf ,FinalOutputStream, start_page_num)
        FinalOutputStream = intermOutputStream
        start_page_num = ending_page_num

    content_page_canvas = generate_content_page(index_list)

    final_pdf = merge_all_pdfs(content_page_canvas , FinalOutputStream)

    print("Finishing touches.....")
    final_pdf.write(os.path.join(TEMP_DIR, 'FINAL.pdf'))
    print("Final Pdf written")

    print("Hang tight..")
    #for file in [os.path.join(TEMP_DIR, 'MERGED.pdf') , os.path.join(TEMP_DIR, 'CONTENT.pdf'), os.path.join(TEMP_DIR, 'CONTENT.pdf')]:

    shutil.copy((os.path.join(TEMP_DIR, 'FINAL.pdf')), INPUT)
    print("PROCESS SUCCESS")


if __name__ == "__main__":
    main()
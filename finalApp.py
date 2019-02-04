from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os


def retrieve_pdfs_to_combine():
    pdf_list = []
    lst = os.listdir("D:\\Python_Projects\\NDAgenerator\\InputFolder\\")

    for item in lst:
        if item.endswith('.pdf'):
            pdf_list.append(item)

    return pdf_list


def perform_pdf_validations(pdf_lst):
    file_position_list = []
    position_count_dict = {}
    abend_flag = False

    for pdf in pdf_lst:
        try:
            position , title = pdf.split('_')
            file_position_list.append(position)
        except:
            print("{0} contains multiple _ in the title".format(pdf))
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


def attach_page_numbers(pdf, output, current_page_num):

    print("Processing {0} file".format(pdf))

    existing_pdf = PdfFileReader(open(pdf, "rb") , strict=False)
    page_count_for_pdf = existing_pdf.getNumPages()

    for i in range(0, page_count_for_pdf):
        page = existing_pdf.getPage(i)
        size = page.mediaBox
        # create a new PDF with Reportlab
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
    content_canvas = canvas.Canvas("content.pdf", pagesize=letter)
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
    outputStream = open("D:\\Python_Projects\\NDAgenerator\\pdf_merger_new.pdf", "wb")
    FinalPdfOutputStream.write(outputStream)
    outputStream.close()
    print("merged pdf created")

    print("generating content pdf")
    contentCanvas.save()
    print("content pdf created")

    merger = PdfFileMerger()

    for generated_pdfs in ["content.pdf", "pdf_merger_new.pdf"]:
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
    final_pdf.write("FINAL.pdf")
    print("PROCESS SUCCESS")


if __name__ == "__main__": main()
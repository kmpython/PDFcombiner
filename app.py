from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

pdf_list = []
index_list = []

lst = os.listdir("D:\\Python_Projects\\NDAgenerator\\")
for item in lst:
    if item.endswith('.pdf'):
        pdf_list.append(item)

pdf_list.sort()
page_num = 1
output = PdfFileWriter()

# read your existing PDF
for pdf in pdf_list:
    print(pdf)
    index_list.append((pdf, page_num))
    existing_pdf = PdfFileReader(open(pdf, "rb"), strict=False)
    page_count_for_pdf = existing_pdf.getNumPages()

    for i in range(0, page_count_for_pdf):
        page = existing_pdf.getPage(i)
        size = page.mediaBox

        # create a new PDF with Reportlab
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
#        can.drawString(530, 15, str(page_num).zfill(4))
        can.drawString(int(size[2]) - 40, 15, str(page_num).zfill(4))
        can.save()
        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        page_num += 1

#        page = existing_pdf.getPage(i)
        # add the "watermark" (which is the new pdf) on the existing page
        page.mergePage(new_pdf.getPage(0))
        output.addPage(page)


# finally, write "output" to a real file
print("finally writing the output...")
outputStream = open("D:\\Python_Projects\\NDAgenerator\\pdf_merger_new.pdf", "wb")
output.write(outputStream)
outputStream.close()
print("processed the pdfs...")


# generate content page
print("Generating content page ...")
height = 700
canvas = canvas.Canvas("content.pdf", pagesize=letter)
canvas.drawCentredString(320, 750, "CONTENTS")
for namepage in index_list:
    title_detl, page = namepage
    srno, title_name = title_detl.split('_')
    canvas.drawString(10, height, str(srno + ' ' + title_name + '..........' + str(page)))
    height -= 20
canvas.save()
print("content page created...")


# merge content pdf and combined pdf
print("finishing touches...")
merger = PdfFileMerger()
for generated_pdfs in ["content.pdf" , "pdf_merger_new.pdf"]:
    merger.append(generated_pdfs)
merger.write("final.pdf")
print("SUCCESS")

def main():
    pass

if __name__ == "__main__": main()
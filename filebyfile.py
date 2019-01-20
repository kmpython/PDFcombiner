from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

# creating list of pdfs to mearge
pdf_list = []
final_list = []
lst = os.listdir("D:\\Python_Projects\\NDAgenerator\\")
for item in lst:
    if item.endswith('.pdf'):
        pdf_list.append(item)

pdf_list.sort()
page_num = 1

# read your existing PDF
for pdf in pdf_list:
    print(pdf)
    output = PdfFileWriter()
    existing_pdf = PdfFileReader(open(pdf, "rb"))
    page_count_for_pdf = existing_pdf.getNumPages()

    for i in range(0, page_count_for_pdf):

        # create a new PDF with Reportlab
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(530, 15, str(page_num).zfill(4))
        can.save()
        packet.seek(0)
        new_pdf = PdfFileReader(packet)

        page_num += 1

        page = existing_pdf.getPage(i)
        # add the "watermark" (which is the new pdf) on the existing page
        page.mergePage(new_pdf.getPage(0))
        output.addPage(page)

    # finally, write "output" to a real file
    print("Processing the file")
    name, ext = pdf.split('.')
    outputStream = open(name+'_mod.'+ext, "wb")
    output.write(outputStream)
    outputStream.close()
    final_list.append(name+'_mod.'+ext)
    print("process success")

print("combining all files.....")
merger = PdfFileMerger()
for pdff in final_list:
    merger.append(pdff)

merger.write("result.pdf")
print("Finished")
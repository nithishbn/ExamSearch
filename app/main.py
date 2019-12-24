
from PyPDF2 import PdfFileReader
from PyPDF2.pdf import PageObject


def pdfToText(pdf: str) -> bool:
    """
    :param pdf: absolute path to pdf file
    :return boolean: successful
    """
    if pdf is None or len(pdf) <= 0:
        return False
    try:
        with open(pdf,'rb') as pdfFile:
            pdfRead = PdfFileReader(pdfFile)
            pageCount = pdfRead.getNumPages()
            for pageNum in range(1,pageCount):
                page = pdfRead.getPage(pageNum)
                print(page.extractText())
    except IOError as e:
        print(e)


if __name__ == '__main__':
    pdfToText(r"D:\Nithish\ExamSearch\data\2018\Oct-Nov\9700_w18_qp_11.pdf")
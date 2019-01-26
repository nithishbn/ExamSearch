import PyPDF2

# creating a pdf file object
pdfFileObj = open(r'C:\Users\narasimmanr\Documents\Nithish\examsearch\2018\Oct-Nov\9700_w18_qp_11.pdf', 'rb')

# creating a pdf reader object
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

# printing number of pages in pdf file
print(pdfReader.numPages)
num = pdfReader.numPages
for i in range(1,num):
    file = pdfReader.getPage(i)
    print(file.extractText())


# closing the pdf file object
pdfFileObj.close()
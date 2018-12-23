import os
import shutil
import subprocess
from PIL import Image as PI
import pyocr.builders

tool = pyocr.get_available_tools()[0]
lang = tool.get_available_languages()[0]
dirname = os.path.dirname(__file__)


# image_pdf = Image(filename="C:\\Users\\narasimmanr\\Documents\\PapaCambridgeScrapper\\2018\\May-June\\9700_s18_qp_11.pdf")
# # image_pdf = Image(filename="idk.pdf", resolution=150)
#


def pdfToImage(filePath):
    if os.path.exists(os.path.join(dirname, "img")):
        shutil.rmtree(os.path.join(dirname, "img"))
    if not os.path.exists(os.path.join(dirname, "img")):
        os.makedirs(os.path.join(dirname, "img"))
    subprocess.run(
        '"C:\Program Files\ImageMagick-6.9.10-Q16\convert.exe" -density 150 "{filePath}" "img\\img.png"'.format(
            filePath=filePath))


# -adaptive-resize 1900x
pdfToImage("2014/Nov/9700_w14_qp_22.pdf")
fileList = []
i = 0
while True:
    for subdir, dirs, files in os.walk(os.path.join(dirname, "img")):
        for file in sorted(files):
            if (file.endswith(".png")):
                i += 1
                file = os.path.join(subdir, file)
                fileList.append(file)
                print(file)
                txt = tool.image_to_string(
                    PI.open(file),
                    lang=lang,
                    builder=pyocr.builders.LineBoxBuilder()
                )
                os.remove(file)
                with open("./img/text{}.txt".format(i), "a") as textFile:
                    for line in txt:
                        textFile.write(line.content + "\n")

                print("-------------------------------------------------------------------------")
print(fileList)
print(i)
for j in range(1, i + 1):
    print(j)
    with open(dirname + "/img/text.txt", "a") as file:
        with open(dirname + "/img/text{}.txt".format(j), "r") as wrt:
            print(wrt)
            for line in wrt:
                print(line)
                file.write(line)
            print("-----------------------------------------------------------------------------")

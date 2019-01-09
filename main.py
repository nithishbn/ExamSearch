import codecs
import os
import re
import shutil
from PIL import Image
from pdf2image import convert_from_path
import pyocr.builders

tool = pyocr.get_available_tools()[0]
lang = tool.get_available_languages()[0]
final_text = []
dirname = os.path.dirname(__file__)
img = Image.open(dirname + "/img/img-01.jpg")
height = img.height
width = img.width


def pdfToText(filePath):
    # image_jpeg is the list of all pdf pages as images
    image_jpeg = convert_from_path(filePath, thread_count=4, dpi=300)
    length = len(image_jpeg)
    # creates img dir if not exists.
    print(os.path.join(dirname, "img"))
    if os.path.exists(os.path.join(dirname, "img")):
        shutil.rmtree(os.path.join(dirname, "img"))
    if not os.path.exists(os.path.join(dirname, "img")):
        os.makedirs(os.path.join(dirname, "img"))
    path = os.path.dirname(__file__) + "/img"

    count = 1
    builder = pyocr.builders.LineBoxBuilder()
    # all pdf pages transcribed into one large text file for data use later
    with open(path + "/text.txt", "a") as wrt:
        for i in range(1, length - 1):  # length
            img = image_jpeg[i]
            if count < 10:
                file = "{}/img-0{}.jpg".format(path, count)
            else:
                file = "{}/img-{}.jpg".format(path, count)
            print(file)
            img.save(file, 'jpeg')
            txt = tool.image_to_string(
                Image.open(file),
                lang=lang,
                builder=builder
            )
            for line in txt:
                wrt.write("{content} | ({x1},{y1}) ({x2},{y2})\n".format(content=line.content, x1=line.position[0][0],
                                                                         y1=line.position[0][1], x2=line.position[1][0],
                                                                         y2=line.position[1][1]))
            img = Image.open(file)
            if count < 10:
                pageCount = "0" + str(count)
            else:
                pageCount = count
            wrt.write("page end {} | (0,0) ({x2},{y2})\n".format(pageCount, x2=img.width, y2=img.height))
            print("Page {} transcribed".format(pageCount))
            count += 1
    print("Text transcription found at {}".format(dirname + "/img/text.txt"))


def snip(pos, img, count):
    img_to_crop = Image.open(img)
    if count < 10:
        thing = "0" + str(count)
    else:
        thing = str(count)
    img_to_crop.crop(pos).save("./img/question{}.jpg".format(thing))


def getFigures():
    with open("./img/text.txt", "r") as file:
        searchlines = file.readlines()
    str = ""
    figNum = ""
    figPos = []
    for i, line in enumerate(searchlines):
        # finds the two coordinates in the line
        pos = re.findall("\|(.*) (.*)", line)
        if len(pos) == 0:
            print(">>>>>>>>>" + line)
        else:
            pos = pos[0]
        if "Fig" in line and figNum != "":
            check = re.findall("Fig\.(.*[0-9]\.[0-9].*?)", line)
            # print(check)
            if len(check) == 0:
                continue
            elif figNum == check[0]:
                str += line
                print(str)
                str = ""
                figNum = ""
        elif figNum != "":
            str += line
        elif "Fig" in line and figNum == "":
            figNum = re.findall("Fig\.(.*[0-9]\.[0-9].*?)", line)[0]
            # print("asdf " + figNum)

            str += line
        # else:
        #     str += line + "\n"
        #     # print(line)


def getMultipleChoiceQuestions():
    with open("./img/text.txt", "r") as file:
        searchLines = file.readlines()
    lst = list()
    lineBeforeList = list()
    endOfPage = False
    questionStart = False
    oldLine = ""
    greatestXValue = 0
    coordHolder = ()
    for i in range(0, len(searchLines)):
        line = searchLines[i]
        if line.startswith("page"):
            pageNumber = re.findall(" ([0-9].*) \|", line)[0]
            lineBeforeList.append(eval(re.findall("\| (\(.*[0-9]\)) (.*[0-9]\))", line)[0][1]))
            lineBeforeList.append(pageNumber)
            lst.append("end")
            endOfPage = True
            continue
        if "UCLES" in line:
            continue
        # finds the two coordinates in the line
        pos = re.findall("\| (\(.*[0-9]\)) (.*[0-9]\))", line)[0]
        val = re.findall("^([0-9].*?)(?=\.| )", line)
        # these should always be correct/never fail... except when they do ugh
        coord1 = eval(pos[0])
        if 205 <= int(coord1[0]) <= 210 and len(val) > 0 and type(eval(val[0])) is int:
            if questionStart:
                lst.append(coordHolder)
                if oldLine != "":
                    pos = re.findall("\| (\(.*[0-9]\)) (.*[0-9]\))", oldLine)[0]
                    if endOfPage:
                        endOfPage = False
                    elif not endOfPage:
                        lineBeforeList.append((greatestXValue, eval(pos[1])[1]))
                greatestXValue = 0
            questionStart = True
            coordHolder = coord1
        if questionStart:
            potentialXValue = eval(pos[1])[0]
            # startCoord = eval(pos[0])
            # coordHolder =
            if potentialXValue > greatestXValue:
                greatestXValue = potentialXValue
            oldLine = line
    print(lst)
    print(lineBeforeList)
    count = 1
    counterNew = -1
    lastCounterIPromise = 1
    print(len(lst))
    print(len(lineBeforeList))
    print(len(lineBeforeList) == len(lst))
    for i in range(0, len(lst)):
        counterNew += 1
        coord1 = lst[i]
        endCoord = lineBeforeList[i]
        if coord1 == 'end':
            print("page end reached = {}".format(endCoord))
            count += 1
            # counterNew += 2
            continue
        # print(type(coord1), coord1, type(endCoord), endCoord)
        if type(endCoord) == str:
            print("AHHHHH " + endCoord)
        fullCoord = coord1 + endCoord
        print("fullcoord={}".format(fullCoord))
        if count < 10:
            newCount = "0" + str(count)
        elif count >= 10:
            newCount = str(count)
        imgName = dirname + "\img\img-{}.jpg".format(newCount)
        print(imgName)
        snip(fullCoord, imgName, lastCounterIPromise)
        lastCounterIPromise += 1


# pdfToText(dirname+r"\2018\May-June\9700_s18_qp_11.pdf")
# getFigures()
getMultipleChoiceQuestions()
# snip((207, 1236, width, 1701),r"D:\Nithish\cambridgepaperparser\img\img-01.jpg",69)

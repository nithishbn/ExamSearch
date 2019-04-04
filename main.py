import ast
import io
import os
import re
import shutil
import sqlite3

import flask
import requests
from PIL import Image
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
import pyocr.builders
from nltk.corpus import stopwords

# import nltk
# nltk.download("stopwords")
tool = pyocr.get_available_tools()[0]
# print(tool)
lang = tool.get_available_languages()[0]
dirname = os.path.dirname(__file__)
print(dirname)


def pdfToText(filePath, isMarkScheme):
    # comment
    # image_jpeg is the list of all pdf pages as images
    print(filePath)
    with convert_from_path(filePath, thread_count=4, dpi=300) as image_jpeg:

        length = len(image_jpeg)
        matches = re.findall("([0-9].+?)\/(.+[A-z])\/(.+).pdf", filePath)[0]
        # basic information about file
        year = matches[0]
        month = matches[1]
        paper = matches[2]
        if not isMarkScheme:
            # creates img dir if not exists.
            print(os.path.join(dirname, "img"))
            if os.path.exists(os.path.join(dirname, "img/{}/{}/{}".format(year, month, paper))):
                shutil.rmtree(os.path.join(dirname, "img/{}/{}/{}".format(year, month, paper)))
            if not os.path.exists(os.path.join(dirname, "img/{}/{}/{}".format(year, month, paper))):
                os.makedirs(os.path.join(dirname, "img/{}/{}/{}".format(year, month, paper)))
            path = os.path.dirname(__file__) + "/img/{}/{}/{}".format(year, month, paper)
            length -= 1
            print("dirs created")
        else:
            paperNew = ""
            for i, letter in enumerate(paper):
                if letter == "m" and paper[i + 1] == "s":
                    paperNew += "q"
                elif letter == "s" and paper[i - 1] == "m":
                    paperNew += "p"
                else:
                    paperNew += letter
            print(paperNew)
            path = os.path.dirname(__file__) + "/img/{}/{}/{}/ms".format(year, month, paperNew)
        count = 1
        builder = pyocr.builders.LineBoxBuilder()
        # writes basic info to be accessed later
        with open(path + "/text.txt", "w") as wrt:
            wrt.write(year)
            wrt.write("\n")
            wrt.write(month)
            wrt.write("\n")
            wrt.write(paper)
            wrt.write("\n")
        # all pdf pages transcribed into one large text file for data use later
        with open(path + "/text.txt", "a") as wrt:
            for i in range(1, length):  # length
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
                # where the magic happens for OCR
                for line in txt:
                    wrt.write(
                        "{content} | ({x1},{y1}) ({x2},{y2})\n".format(content=line.content, x1=line.position[0][0],
                                                                       y1=line.position[0][1], x2=line.position[1][0],
                                                                       y2=line.position[1][1]))
                    print(line.content)
                img = Image.open(file)
                if count < 10:
                    pageCount = "0" + str(count)
                else:
                    pageCount = count
                # end of page so it's easier to parse questions later
                wrt.write("page end {} | (0,0) ({x2},{y2})\n".format(pageCount, x2=img.width, y2=img.height))
                print("Page {} transcribed".format(pageCount))
                count += 1
        print("Text transcription found at {}".format(path + "/text.txt"))


# does the snippy snippy for the question images
def snip(pos, img, count, path):
    year = path[0]
    month = path[1]
    paper = path[2]
    with Image.open(img) as img_to_crop:
        if count < 10:
            thing = "0" + str(count)
        else:
            thing = str(count)
        print(pos)
        if pos[3] >= pos[1]:
            if len(pos) != 4:
                print(pos)
            else:
                img_to_crop.crop(pos).save("./img/{}/{}/{}/question{}.jpg".format(year, month, paper, thing))
                return 1


# gets multiple choice questions
def getMultipleChoiceQuestions(filePath):
    print(filePath)
    matches = re.findall("([0-9].+?)\\\(.+[A-z])\\\(.+).pdf", filePath)[0]
    # basic info again
    year = matches[0]
    month = matches[1]
    paper = matches[2]
    # reads text file
    with open("./img/{}/{}/{}/text.txt".format(year, month, paper), "r") as file:
        searchLines = file.readlines()
    # lst contains
    questionStartCoords = list()
    questionEndCoords = list()
    endOfPage = False
    questionStart = False
    oldLine = ""
    # decided to cave in and just use the maximum margin because calculating the greatest x value was such a pain
    greatestXValue = 2480
    coordHolder = (0, 0)
    # starts from 3rd line to skip over basic info
    for i in range(3, len(searchLines)):
        line = searchLines[i]
        # checks page end
        if line.startswith("page"):
            questionStart = False
            pageNumber = re.findall(" ([0-9].*) \|", line)[0]
            print(pageNumber)
            questionEndCoords.append(eval(re.findall("\| (\(.*[0-9]\)) (.*[0-9]\))", line)[0][1]))
            questionEndCoords.append(pageNumber)
            questionStartCoords.append(coordHolder)
            questionStartCoords.append("end")

            endOfPage = True
            continue
        # this was just being annoying
        if "UCLES" in line:
            continue
        # finds the two coordinates in the line
        pos = re.findall("\| (\([0-9].*\)) (.*[0-9]\))", line)[0]
        # questionNumber
        questionNumber = re.findall("^([0-9].*?)(?=\.| )", line)
        # these should always be correct/never fail... except when they do ugh
        coord1 = eval(pos[0])
        # checks if the line is the question start line
        if 205 <= int(coord1[0]) <= 210 and len(questionNumber) > 0 and type(eval(questionNumber[0])) is int:
            # is a question being parsed currently and have you stumbled upon the next question?
            # if so, put the last line in and assume this as the start of the next question
            if questionStart:
                questionStartCoords.append(coordHolder)
                if oldLine != "":
                    pos = re.findall("\| (\(.*[0-9]\)) (.*[0-9]\))", oldLine)[0]
                    if endOfPage:
                        endOfPage = False
                    questionEndCoords.append((greatestXValue, eval(pos[1])[1]))
            questionStart = True
            coordHolder = coord1
        # make the oldLine the line value for the endOfQuestionCoords list
        oldLine = line
    # lineBeforeList.pop(2)
    print(questionStartCoords)
    print(questionEndCoords)
    count = 1
    # great counter title
    lastCounterIPromise = 1
    path = dirname + "/img/{}/{}/{}".format(year, month, paper)
    # image snippy snippy
    for i in range(0, len(questionStartCoords)):
        # grab set of start and end coords
        coord1 = questionStartCoords[i]
        endCoord = questionEndCoords[i]
        # reached end of page
        if coord1 == 'end':
            print("page end reached = {}".format(endCoord))
            count += 1
            continue
        # this is how the snip tool takes the coordinates
        fullCoord = coord1 + endCoord
        print("fullcoord={}".format(fullCoord))
        if count < 10:
            newCount = "0" + str(count)
        elif count >= 10:
            newCount = str(count)
        imgName = path + "\img-{}.jpg".format(newCount)
        print(imgName)
        # snippy snippy
        snip(fullCoord, imgName, lastCounterIPromise, [year, month, paper])
        lastCounterIPromise += 1
    # getMultipleChoiceAnswers(year, month, paper)


def getFreeResponseQuestions(filePath):
    matches = re.findall("([0-9].+?)\/(.+[A-z])\/(.+).pdf", filePath)[0]
    year = matches[0]
    month = matches[1]
    paper = matches[2]
    path = dirname + "/img/{}/{}/{}".format(year, month, paper)
    questionStart = False
    questionStartCoords = []
    questionEndCoords = []
    oldLine = ""
    endOfPage = False
    greatestXValue = 2480
    with open(path + "/text.txt", "r") as file:
        lines = file.readlines()
        for i in range(3, len(lines)):
            line = lines[i]
            # finds the two coordinates in the line
            pos = re.findall("\| (\([0-9].*\)) (.*[0-9]\))", line)[0]
            # questionNumber
            questionNumber = re.findall("^([0-9].*?)(?=\.| )", line)
            # these should always be correct/never fail... except when they do ugh
            coord1 = eval(pos[0])
            if "page end" in line:
                print(line)
                endOfPage = True
                # continue
            if "[Total:" in line:
                print(line)
                questionStart = False
                questionStartCoords.append(coordHolder)
                questionEndCoords.append((greatestXValue, eval(pos[1])[1]))
                continue
            # checks if the line is the question start line
            if 205 <= int(coord1[0]) <= 210 and len(questionNumber) > 0 and type(eval(questionNumber[0])) is int:
                # is a question being parsed currently and have you stumbled upon the next question?
                # if so, put the last line in and assume this as the start of the next question
                print(line)
                if questionStart:
                    questionStartCoords.append(coordHolder)
                    if oldLine != "":
                        pos = re.findall("\| (\(.*[0-9]\)) (.*[0-9]\))", oldLine)[0]
                        if endOfPage:
                            endOfPage = False
                            print(line)
                            questionEndCoords.append((greatestXValue, eval(pos[1])[1]))
                questionStart = True
                coordHolder = coord1
            # make the oldLine the line value for the endOfQuestionCoords list
            oldLine = line
    print(questionStartCoords)
    print(questionEndCoords)
    print("hi")
    count = 1
    # great counter title
    lastCounterIPromise = 1
    path = dirname + "/img/{}/{}/{}".format(year, month, paper)
    # image snippy snippy
    for i in range(0, len(questionStartCoords)):
        # grab set of start and end coords
        coord1 = questionStartCoords[i]
        endCoord = questionEndCoords[i]
        # reached end of page
        if coord1 == 'end':
            print("page end reached = {}".format(endCoord))
            count += 1
            continue
        # this is how the snip tool takes the coordinates
        fullCoord = coord1 + endCoord
        print("fullcoord={}".format(fullCoord))
        if count < 10:
            newCount = "0" + str(count)
        elif count >= 10:
            newCount = str(count)
        imgName = path + "\img-{}.jpg".format(newCount)
        print(imgName)
        # snippy snippy
        res = snip(fullCoord, imgName, lastCounterIPromise, [year, month, paper])
        if res == 1:
            print("all good")
        else:
            print("skipping this one")
        lastCounterIPromise += 1


# takes image files and pairs them to their respective text tags to make the images searchable
def tagImage(filePath):
    matches = re.findall("([0-9].+?)\/(.+[A-z])\/(.+).pdf", filePath)[0]
    year = matches[0]
    month = matches[1]
    paper = matches[2]
    path = dirname + "/img/{}/{}/{}".format(year, month, paper)
    questionList = []
    question = []
    questionStart = False
    # very similar code to above for the coordinate parsing but this time it checks the contents of the line instead of the coordinates
    with open(path + "/text.txt", "r") as file:
        lines = file.readlines()
        for i in range(3, len(lines)):
            line = lines[i]
            pos = re.findall("\| (\([0-9].*\)) (.*[0-9]\))", line)[0]
            val = re.findall("^([0-9].*?)(?=\.| )", line)
            lineVal = re.findall("^(.*)\|", line)[0]
            # these should always be correct/never fail... except when they do ugh
            coord1 = eval(pos[0])
            # same stuff as earlier but now it's appending the cool contents
            if 205 <= int(coord1[0]) <= 210 and len(val) > 0 and type(eval(val[0])) is int:
                if questionStart:
                    questionList.append(question)
                    question = []
                questionStart = True
                # question.append(line)
            if questionStart:
                question.append(lineVal)
        # database connection
        conn = sqlite3.connect("questions.sqlite")
        cur = conn.cursor()
        # stop words
        stops = set(stopwords.words("english"))
        for q in questionList:
            # the following code standardizes each question string so that it doesnt have weird spaces and stuff
            thing = "".join(q)
            thing = thing.split()
            # removes top words
            newQ = [word.lower() for word in thing if word.lower() not in stops]
            # removes spaces and commas
            tags = [word.lower() for word in newQ if word.lower() not in [" ", ", "]]
            # gets the question number to be used for the filePath entry in the database
            questionNumber = tags.pop(0)
            if "." in questionNumber:
                questionNumber = questionNumber[:-1]
            if int(questionNumber) < 10:
                questionNumber = "0" + questionNumber

            # smart filePath
            insertFilePath = "/img/{}/{}/{}/question{}.jpg".format(year, month, paper, questionNumber)
            answer = "/img/{}/{}/{}/question{}-ms.jpg".format(year, month, paper, questionNumber)
            # row insertion
            for tag in tags:
                # insert new tags into the tags table
                cur.execute("insert into tags (tag) VALUES (?) ", (tag,))
                # insert filepath and tag id into main table
                cur.execute(
                    "INSERT OR REPLACE INTO main (tag,filepath, year, month, paper, answer) values ((select id from tags where tags.tag=?),?,?,?,?,?) ",
                    (tag, insertFilePath, year, month, paper, answer))
        cur.close()
        conn.commit()
        conn.close()


# search! :D
def search():
    server = "http://127.0.0.1:5000/"
    dirname = os.path.dirname(os.path.abspath(__file__))
    print(dirname)
    query = ""
    while True:
        query = input("Query: ")
        r = requests.post(server, {"query": query})
        # print(r.status_code)
        print(r.content)
        content = ast.literal_eval(bytes.decode(r.content))
        print(list(content))
        for val in content:
            print(val)
            img = requests.post(server + "getImage", {"imgPath": val})
            print(img.status_code)
            if img.status_code==200:
                print(type(img.content))
                imgToShow = Image.open(io.BytesIO(img.content))
                imgToShow.show()
            input("wait: ")
        if query == "quit":
            break


# takes url and downloads the pdf from PapaCambridge. year, month, and paper used to create directories/name files
def scrap(url, year, month, paper):
    data = requests.get(url, stream=True)
    if data.status_code != 200:
        print("error :(")
    else:
        if not os.path.exists(year):
            os.makedirs(year)
        if not os.path.exists(os.path.join(dirname, "{}/{}".format(year, month))):
            os.makedirs("{}/{}".format(year, month))
        path = os.path.join(dirname, "{year}/{month}/{paper}.pdf".format(year=year, month=month, paper=paper))
        with open(path, "wb") as file:
            # if not os.path.exists(path):
            file.write(data.content)


def initializeDirectories():
    baseUrl = "https://pastpapers.papacambridge.com/?dir=Cambridge%20International%20Examinations%20%28CIE%29%2FAS%20and%20A%20Level%2FBiology%20%289700%29"
    domain = "https://pastpapers.papacambridge.com"
    directory = requests.get(baseUrl)
    soup = BeautifulSoup(directory.content, "html.parser")
    aTags = list(soup.find_all('a', class_="clearfix", href=True))
    newList = list()
    for i in range(0, len(aTags) - 2):  # len(aTags) - 2
        dirThing = aTags[i]['href']
        monthDir = requests.get(domain + "/" + dirThing)
        soup = BeautifulSoup(monthDir.content, "html.parser")
        fileTags = list(soup.find_all('a', class_="clearfix", href=True))
        for j in range(1, len(fileTags)):
            tag = fileTags[j]
            file = tag['href']
            thing = "{file}".format(file=file)[12::]
            print(thing)
            # this regex finds the year, the month, and the paper name
            matches = re.findall("(?:Biology%20%289700%29/)([0-9].+?)%20(.+[A-z])/(.+).pdf", thing)
            if len(matches) == 0:
                # this regex does the same but looks for a dash instead of a space because papacambridge sucks
                matches = re.findall("(?:Biology%20%289700%29/)([0-9].+?)-(.+[A-z])/(.+).pdf", thing)
            if matches is not None and len(matches) != 0:
                print(matches)
                matches = matches[0]
                year = matches[0]
                month = matches[1]
                paper = matches[2]
                print(domain + thing)
                # takes year, month, and paper name and appends it to the base domain to get it from PapaCambridge
                scrap("{domain}/{file}".format(domain=domain, file=thing), year, month, paper)


#
# fileName = dirname + r"/2017/Nov/9700_w17_qp_21.pdf"
# search()


#
search()
# run()

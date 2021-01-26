import ast
import io
import os
import re
import shutil
import sqlite3

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
    image_jpeg = convert_from_path(filePath, thread_count=4, dpi=300)

    length = len(image_jpeg)
    val = "\/"
    print(val)
    if "\\" in filePath:
        val = '\\\\'
    fileInfo = re.findall("([0-9].+?){val}(.+[A-z]){val}(.+).pdf".format(val=val), filePath)[0]
    # basic information about file
    year = fileInfo[0]
    month = fileInfo[1]
    paper = fileInfo[2]
    if not isMarkScheme:
        # creates img dir if not exists.
        print(os.path.join(dirname, "app/static/img"))
        if os.path.exists(os.path.join(dirname, "app/static/img/{}/{}/{}".format(year, month, paper))):
            shutil.rmtree(os.path.join(dirname, "app/static/img/{}/{}/{}".format(year, month, paper)))
        if not os.path.exists(os.path.join(dirname, "app/static/img/{}/{}/{}".format(year, month, paper))):
            os.makedirs(os.path.join(dirname, "app/static/img/{}/{}/{}".format(year, month, paper)))
        path = os.path.dirname(__file__) + "/app/static/img/{}/{}/{}".format(year, month, paper)
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
        path = os.path.dirname(__file__) + "/app/static/img/{}/{}/{}/ms".format(year, month, paperNew)
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
    print(year, month, paper)
    getMultipleChoiceQuestions([year, month, paper])


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
                img_to_crop.crop(pos).save("./app/static/img/{}/{}/{}/question{}.jpg".format(year, month, paper, thing))
                return 1


# gets multiple choice questions
def getMultipleChoiceQuestions(fileInfo):
    print(fileInfo)
    # basic info again
    year = fileInfo[0]
    month = fileInfo[1]
    paper = fileInfo[2]
    # reads text file
    with open("./app/static/img/{}/{}/{}/text.txt".format(year, month, paper), "r") as file:
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
        if 205 <= int(coord1[0]) <= 210 and len(questionNumber) > 0 and type(
                eval(questionNumber[0])) is int or endOfPage:
            if not (205 <= int(coord1[0]) <= 210 and len(questionNumber) > 0 and type(eval(questionNumber[0])) is int):
                coord1 = (0, 0)
                endOfPage = False
                # questionStart=True
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
    pageNumber = '01'
    # great counter title
    questionNumber = 1
    path = dirname + "/app/static/img/{}/{}/{}".format(year, month, paper)
    testList = []
    # image snippy snippy
    print(len(questionEndCoords) == len(questionStartCoords))
    for i in range(0, len(questionStartCoords)):
        # grab set of start and end coords
        coord1 = questionStartCoords[i]
        endCoord = questionEndCoords[i]
        # reached end of page
        if coord1 == 'end':
            print("page end reached = {}\n".format(endCoord))
            print(questionStartCoords)
            print(questionEndCoords)
            if int(endCoord) < 9:
                pageNumber = "0" + (str(int(endCoord) + 1))
            else:
                pageNumber = (str(int(endCoord) + 1))
            # questionNumber += 2
            continue
        # this is how the snip tool takes the coordinates
        fullCoord = coord1 + endCoord
        print("fullcoord={}".format(fullCoord))
        print("question number = {}".format(questionNumber))
        imgName = path + "/img-{}.jpg".format(pageNumber)
        print(imgName)
        # snippy snippy
        testList.append(questionNumber)
        snip(fullCoord, imgName, questionNumber, [year, month, paper])
        questionNumber += 1

    # getMultipleChoiceAnswers(year, month, paper)
    # tagImage(fileInfo)
    print(testList)


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
def tagImage(fileInfo):
    year = fileInfo[0]
    month = fileInfo[1]
    paper = fileInfo[2]
    path = dirname + "app/static/img/{}/{}/{}".format(year, month, paper)
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
            insertFilePath = "app/static/img/{}/{}/{}/question{}.jpg".format(year, month, paper, questionNumber)
            answer = "/app/static/img/{}/{}/{}/question{}-ms.jpg".format(year, month, paper, questionNumber)
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


def search(query):
    # multiple tags :)
    query = query.split()
    # database connection
    conn = sqlite3.connect("questions.sqlite")
    cur = conn.cursor()
    results = []
    # goes through each word in the query and finds which filePath entry has that tag using cool sql
    for word in query:
        cur.execute(
            "select distinct filepath,year,month,paper from main join tags on main.tag = tags.id where tags.tag=?",
            (word,))
        res = cur.fetchall()
        print(res)
        for val in res:
            results.append(val)
    # ooh what's this you ask?
    # this intersection thing basically removes duplicate file paths in case multiple tags exist in the same question
    # so if the question had the entries xylem AND transpiration, which is highly likely, then it won't open the same question twice
    # which is nice
    # print(results)

    # results = results[0]
    # print(results)
    # results = results[0]
    thing = []
    if len(query) > 1:
        for val in results:
            # print(results.count(val) > 1)
            if val not in thing and results.count(val) >= 1:
                thing.append(val)
        # print(thing)
        results = thing
        # for i in range(0, len(results) - 1, 2):
        #     print(results[i])
        #     results = list(set(results[i]).intersection(results[i + 1]))
        # print(results)
    # only one query? just remove the duplicates and dont do weird intersections
    else:
        results = set(results)
        # print(results)
    # you suck at searching/you haven't indexed enough of the MC papers to get a good result
    if len(results) == 0:
        return []
    # yay go you! you searched well, my young padawan
    else:
        results = list(results)
        # values = ["./static{}".format(path) for path in results]
        # print(values)
        # return values
        return results
        # for imgPath in results:
        #         #     # imgPath = val
        #         #     print(r"{}".format(imgPath))
        #         #     # PULL THE LEVER, KRONK
        #         #     cur.execute("select year, month, paper from main where main.main.filepath=?", (imgPath,))
        #         #     stuff = cur.fetchall()
        #         #     # print(stuff)
        #     paperInfo = list(set(stuff))[0]
        #     # print(paperInfo)
        #     year = paperInfo[0]
        #     month = paperInfo[1]
        #     paper = paperInfo[2]
        #     if ("qp_2" or "qp_4") in imgPath:
        #         print("{}/{}/{}/{}.pdf".format(dirname, year, month, paper))
        #     markScheme = paper.replace("qp", "ms")
        #     print("{}/{}/{}/{}.pdf".format(dirname, year, month, markScheme))
        #     # WRONG LEVAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        #     # jk it's the right lever get hekt
        #     inp = input("next: ")
        #     if inp == "quit":
        #         break


#
filePath = dirname + r"/data/2014/Jun/9700_s14_qp_13.pdf"
# search()
# dirname = os.path.dirname(__file__)
# # pdfToText(filePath, False)
# val = "\/"
# print(val)
# if "\\" in filePath:
#     val = '\\\\'
# fileInfo = re.findall("([0-9].+?){val}(.+[A-z]){val}(.+).pdf".format(val=val), filePath)[0]
# getMultipleChoiceQuestions(fileInfo)
# snip((210, 1455, 2480, 1966), "D:/Nithish/cambridgepaperparser/app/static/img/2014/Jun/9700_s14_qp_13/img-07.jpg", 15,
#      [2014, "Jun", "9700_s14_qp_13"])
# # tagImage(filePath)
# for root, dirs, files in os.walk(os.path.abspath(".")):
#     for file in files:
#         if "qp_1" in file and ".pdf" in file:
#             filePath = os.path.join(root,file)
#             print(filePath)
#             pdfToText(filePath, False)
#
# search()
# run()

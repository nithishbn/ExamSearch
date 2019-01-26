import os
import re
import shutil
import sqlite3

from PIL import Image
from pdf2image import convert_from_path
import pyocr.builders
from nltk.corpus import stopwords

tool = pyocr.get_available_tools()[0]
# print(tool)
lang = tool.get_available_languages()[0]
dirname = os.path.dirname(__file__)
print(dirname)

def pdfToText(filePath,isMarkScheme):
    # comment
    # image_jpeg is the list of all pdf pages as images
    print(filePath)
    # if isMarkScheme:
    #     filePath
    image_jpeg = convert_from_path(filePath, thread_count=4, dpi=300)
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
                wrt.write("{content} | ({x1},{y1}) ({x2},{y2})\n".format(content=line.content, x1=line.position[0][0],
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
    print("Text transcription found at {}".format(path+"/text.txt"))


# does the snippy snippy for the question images
def snip(pos, img, count, path):
    year = path[0]
    month = path[1]
    paper = path[2]
    img_to_crop = Image.open(img)
    if count < 10:
        thing = "0" + str(count)
    else:
        thing = str(count)
    # if you're bad at life
    if len(pos) != 4:
        print(pos)
    else:
        img_to_crop.crop(pos).save("./img/{}/{}/{}/question{}.jpg".format(year, month, paper, thing))


# gets multiple choice questions
def getMultipleChoiceQuestions(filePath):
    matches = re.findall("([0-9].+?)\/(.+[A-z])\/(.+).pdf", filePath)[0]
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
    coordHolder = ()
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
            coordHolder = ()
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
    getMultipleChoiceAnswers(year,month,paper)

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
                    (tag, insertFilePath, year, month, paper,answer))
        cur.close()
        conn.commit()
        conn.close()


# search! :D
def search():
    query = ""
    while True:
        query = input("Query: ")
        if query == "quit":
            break
        # multiple tags :)
        query = query.split()
        # database connection
        conn = sqlite3.connect("questions.sqlite")
        cur = conn.cursor()
        results = []
        # goes through each word in the query and finds which filePath entry has that tag using cool sql
        for word in query:
            cur.execute("select filepath from main join tags on main.tag = tags.id where tags.tag=?", (word,))
            res = cur.fetchall()
            results.append(res)
        # ooh what's this you ask?
        # this intersection thing basically removes duplicate file paths in case multiple tags exist in the same question
        # so if the question had the entries xylem AND transpiration, which is highly likely, then it won't open the same question twice
        # which is nice
        if len(query) > 1:
            for i in range(0, len(results) - 1, 2):
                results = list(set(results[i]).intersection(results[i + 1]))
        # only one query? just remove the duplicates and dont do weird intersections
        else:
            results = set(results[0])
        # you suck at searching/you haven't indexed enough of the MC papers to get a good result
        if len(results) == 0:
            print("No results found!")
        # yay go you! you searched well, my young padawan
        else:
            for val in results:
                imgPath = val[0]
                print(r"{}".format(imgPath))
                # PULL THE LEVER, KRONK
                img = Image.open(dirname + imgPath)
                img.show()
                # print(val)
                cur.execute("select year, month, paper from main where main.main.filepath=?", (imgPath,))
                stuff = cur.fetchall()
                print(stuff)
                paperInfo = list(set(stuff))[0]
                print(paperInfo)
                year = paperInfo[0]
                month = paperInfo[1]
                paper = paperInfo[2]

                # WRONG LEVAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                # jk it's the right lever get hekt
                inp = input("next: ")
                if inp == "quit":
                    break


def getMultipleChoiceAnswers(year, month, paper):
    dirname = os.path.dirname(__file__)
    paperDir = paper.format("qp")
    path = "/img/{}/{}/{}".format(year, month, paperDir)
    paper = paper.format("ms")
    markSchemePath = path+"/ms"
    # print(markSchemePath)
    fullPath = dirname+markSchemePath
    print(fullPath)

    if os.path.exists(fullPath):
        shutil.rmtree(fullPath)
    os.makedirs(fullPath)
    print("this will take a while because the mark scheme has not been parsed and indexed yet")
    markScheme = ""
    for i, letter in enumerate(paper):
        if letter == "q" and paper[i + 1] == "p":
            markScheme += "m"
        elif letter == "p" and paper[i - 1] == "q":
            markScheme += "s"
        else:
            markScheme += letter
    pdfToText(dirname + "/{}/{}/{}.pdf".format(year, month, markScheme),True)
    print("Mark Scheme indexed!")


fileName = dirname + r"/2018/Oct-Nov/9700_w18_qp_13.pdf"
# conn = sqlite3.connect("questions.sqlite")
# cur = conn.cursor()
# cur.close()
# conn.commit()
# conn.close()
# pdfToText(fileName,False)
# getMultipleChoiceQuestions(fileName)
# tagImage(fileName)
# getMultipleChoiceAnswers("2018","Oct-Nov","9700_w18_qp_13")
# search()

# for i in range(1,4):
#     num = str(i)
#     fileName = dirname + r"/2016/Jun/9700_s16_qp_1{num}.pdf".format(num=num)
#
#     print(fileName)
#     pdfToText(fileName)
#     getMultipleChoiceQuestions(fileName)
#     tagImage(fileName)
# #
#
# pos = (319,871, 319+300,871+100)
# img_to_crop = Image.open(r"C:\Users\narasimmanr\Documents\Nithish\examsearch\img\2018\Oct-Nov\9700_w18_qp_13\ms\img-01.jpg")
# img_to_crop.crop(pos).save("./heh.jpg")
# newImg = Image.open("./heh.jpg")
# newImg.show()
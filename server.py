import os
import re
import sqlite3

from PIL import Image
from flask import Flask, request, jsonify, send_file, send_from_directory

dirname = os.path.dirname(__file__)

app = Flask(__name__, static_url_path='')


@app.route('/', methods=['GET', 'POST'])
def run():
    query = request.form["query"]
    val = list(webServer(query))
    return jsonify(val)


@app.route('/getImage', methods=['GET', 'POST'])
def getImage():
    imgPath = request.form["imgPath"]
    file = re.findall("\/(question.*)",imgPath)[0]
    dirPath = re.findall("(.*)\/question.*",imgPath)[0]
    print(dirPath)
    print(file)
    return send_from_directory("."+dirPath, file)


def webServer(query):
    print("Initializing web server")
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

        for val in res:
            results.append(val[0])
    # ooh what's this you ask?
    # this intersection thing basically removes duplicate file paths in case multiple tags exist in the same question
    # so if the question had the entries xylem AND transpiration, which is highly likely, then it won't open the same question twice
    # which is nice
    # print(results)
    # results = results[0]
    print(results)
    # results = results[0]
    thing = []
    if len(query) > 1:
        for val in results:
            print(results.count(val) > 1)
            if val not in thing and results.count(val) >= 1:
                thing.append(val)
        print(thing)
        results = thing
        # for i in range(0, len(results) - 1, 2):
        #     print(results[i])
        #     results = list(set(results[i]).intersection(results[i + 1]))
        # print(results)
    # only one query? just remove the duplicates and dont do weird intersections
    else:
        results = set(results)
        print(results)
    # you suck at searching/you haven't indexed enough of the MC papers to get a good result
    if len(results) == 0:
        return "No results found!"
    # yay go you! you searched well, my young padawan
    else:
        return list(results)
        # for imgPath in results:
        #     # imgPath = val
        #     print(r"{}".format(imgPath))
        #     # PULL THE LEVER, KRONK
        #     cur.execute("select year, month, paper from main where main.main.filepath=?", (imgPath,))
        #     stuff = cur.fetchall()
        #     # print(stuff)
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

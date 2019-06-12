import os
import sqlite3
from flask import render_template, redirect, session, request

from app import app
from app.forms import SearchForm

dirname = os.path.dirname(__file__)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        res = search(form.search.data.lower())
        print(res)
        # print(os.path.join("./app/static",res[0]))
        for val in res:
            print(val[0])
        print()
        # print(newRes)
        session['results'] = res
        session['searchTerm'] = form.search.data.lower()
        return redirect("/results")
    return render_template('index.html', title='Home', form=form)


@app.route('/results',methods=['GET','POST'])
def getResults():
    query = session['results']
    # info = [ for val in query]
    query = [("./static" + val[0],val[1], val[2], val[3]) for val in query if os.path.isfile("./app/static" + val[0])]
    print()

    searchTerm = session['searchTerm']
    newForm = SearchForm(request.form)
    if newForm.validate_on_submit():
        res = search(newForm.search.data.lower())
        # print(os.path.join("./app/static",res[0]))
        for val in res:
            print(val)
        print()
        newRes = ["./static" + val[0] for val in res if os.path.isfile("./app/static" + val)]
        print(newRes)
        session['results'] = newRes
        session['searchTerm'] = newForm.search.data.lower()
        return redirect("/results")
    return render_template('results.html', query=query,searchTerm=searchTerm,form=newForm)


def search(query):
    # multiple tags :)
    query = query.split()
    # database connection
    conn = sqlite3.connect("questions.sqlite")
    cur = conn.cursor()
    results = []
    # goes through each word in the query and finds which filePath entry has that tag using cool sql
    for word in query:
        cur.execute("select distinct filepath,year,month,paper from main join tags on main.tag = tags.id where tags.tag=?", (word,))
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


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

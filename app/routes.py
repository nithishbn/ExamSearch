import os
from flask import render_template, redirect, session, request

from app import app
from app.examsearch.main import search
from app.forms import SearchForm

dirname = os.path.dirname(__file__)


@app.route('/', methods=['GET', 'POST'])
# @app.route('/index', methods=['GET', 'POST'])
def index():
    return redirect("/examsearchapp")
    # return render_template('examSearch.html')


@app.route("/portfolio")
def portfolio():
    return render_template("/templates/portfolio/portfolio.html")


@app.route('/examsearchapp', methods=['GET', 'POST'])
def examSearch():
    form = SearchForm()
    if form.validate_on_submit():
        res = search(form.search.data.lower())
        # print(os.path.join("./app/static",res[0]))
        for val in res:
            print(val)
        print()
        newRes = [("/static/examsearch" + val[0],val[1],val[2],val[3]) for val in res if os.path.isfile("/static/examsearch" + val[0])]
        print("newRes: " + str(newRes))
        session['results'] = newRes
        session['searchTerm'] = form.search.data.lower()
        return redirect("/results")

    return render_template('/examsearch/examSearch.html', title='Home', form=form)


@app.route('/examsearchapp/results', methods=['GET', 'POST'])
def getResults():
    query = session['results']
    # info = [ for val in query]
    for val in query:
        print("test:" + val[0])
    query = [val[0] for val in query]
    print("query: " + str(query))

    searchTerm = session['searchTerm']
    newForm = SearchForm(request.form)
    if newForm.validate_on_submit():
        res = search(newForm.search.data.lower())
        # print(os.path.join("./app/static",res[0]))
        for val in res:
            print(val)
        print()
        newRes = ["/static/examsearch" + val for val in res if os.path.isfile("/static/examsearch" + val)]
        print(newRes)
        session['results'] = newRes
        session['searchTerm'] = newForm.search.data.lower()
        return redirect("/results")
    return render_template('/examsearch/results.html', query=query, searchTerm=searchTerm, form=newForm)


#if __name__ == '__main__':
 #   app.run(host="0.0.0.0", debug=True)

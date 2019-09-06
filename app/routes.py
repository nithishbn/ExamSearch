import os
from flask import render_template, redirect, session, request

from app import app
from app.forms import SearchForm
from examsearch.main import search

dirname = os.path.dirname(__file__)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return redirect("/portfolio")
    # return render_template('examSearch.html')

@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")
@app.route('/examsearch', methods=['GET', 'POST'])
def examSearch():
    form = SearchForm()
    if form.validate_on_submit():
        res = search(form.search.data.lower())
        # print(os.path.join("./app/static",res[0]))
        for val in res:
            print(val)
        print()
        newRes = ["./static"+val for val in res if os.path.isfile("./app/static" + val)]
        print(newRes)
        session['results'] = newRes
        session['searchTerm'] = form.search.data.lower()
        return redirect("/results")
    return render_template('examSearch.html', title='Home', form=form)


@app.route('/results', methods=['GET', 'POST'])
def getResults():
    query = session['results']
    # info = [ for val in query]
    query = [("./static" + val[0], val[1], val[2], val[3]) for val in query if os.path.isfile("./app/static" + val[0])]
    print()

    searchTerm = session['searchTerm']
    newForm = SearchForm(request.form)
    if newForm.validate_on_submit():
        res = search(newForm.search.data.lower())
        # print(os.path.join("./app/static",res[0]))
        for val in res:
            print(val)
        print()
        newRes = ["./static" + val for val in res if os.path.isfile("./app/static" + val)]
        print(newRes)
        session['results'] = newRes
        session['searchTerm'] = newForm.search.data.lower()
        return redirect("/results")
    return render_template('results.html', query=query, searchTerm=searchTerm, form=newForm)





if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

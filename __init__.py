from flask import Flask, request, render_template, g
from nlpalgorithm import get_relevant_sections
import sqlite3, path

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/result", methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        inputString = request.form['user-input']
        matches = get_relevant_sections(inputString, db = get_db())
        composer = nlpalgorithm.get_composer(inputString)
        return render_template('result.html', inputString=inputString, matches=matches, composer=composer)
    else:
        return render_template('index.html')

DATABASE = path.PATH + 'sqlite/history.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(threaded=True)

import sqlite3
from flask import Flask, request, render_template, g

from scalian import get_relevant_sentences, get_composer, get_original_article
import path

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/result", methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        db = get_db()
        user_query = request.form['user-input']
        composer = get_composer(user_query, db)

        if composer == None:
            return render_template(
                'result.html', 
                inputString=user_query,
                matches=None,
                composer=None, 
                originalContent=None
            )
        else:
            original = get_original_article(composer, db)
            composer = composer.split('-')
            composer = ' '.join(composer).title()

            return render_template(
                'result.html', 
                inputString=user_query, 
                matches=get_relevant_sentences(user_query, db), 
                composer=composer, 
                originalContent=original
            )
    else:
        return render_template('index.html')

def get_db():
    db_path = path.PATH + 'sqlite/history.db'
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(db_path)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run()
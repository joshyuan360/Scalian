from flask import Flask, request, render_template
from nlpalgorithm import get_relevant_sections

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/result", methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        inputString = request.form['user-input']
        matches = get_relevant_sections(inputString)
        return render_template('result.html', inputString = inputString, matches = matches)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run()

from flask import Flask, request, render_template
from nlpalgorithm import get_relevant_sections

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

DEPLOY = '/var/www/ScaliaBot/ScaliaBot/'
#DEPLOY = ''

@app.route("/result", methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        inputString = request.form['user-input']
        matches = get_relevant_sections(inputString)
        return render_template('result.html', inputString = inputString, matches = matches)
    elif request.method == 'POSTkkk':
        inputString = request.form['user-input']

        #local server
        f = open(DEPLOY + 'text.sb')
        #deployment server: law.joshuayuan.com
        #f = open('/var/www/ScaliaBot/ScaliaBot/text.sb')
        
        matches = []
        proximity = 0

        line = f.readline()
        while line:
            proximity = 0
            for word in inputString.split():
                if len(word) > 3 and (word.lower() in line.lower()):
                    proximity += 1
                    if proximity == 2:
                        line = "..." + line + "..."
                        matches.append(line)
                        break

            line = f.readline()
        
        return render_template('result.html', inputString=inputString, matches=matches)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run()

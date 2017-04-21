from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/result", methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        inputString = request.form['user-input']
        f = open('text.sb')
        line = f.readline()
        
        while line:
            if inputString in line:
                textMatch = "..." + line + "..."
                return render_template('result.html', inputString=inputString, textMatch=textMatch)
            line = f.readline()
        

        return render_template('result.html', inputString=inputString, textMatch="none")
    
    return render_template('index.html')

if __name__ == '__main__'
    app.run()

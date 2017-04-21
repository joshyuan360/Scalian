from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/result", methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        inputString = request.form['user-input']
        if "abortion" in inputString:
        	constitution = "no"
        else:
        	constitution = "yes"

        return render_template('result.html', verdict=constitution)
    
    return "LOL"

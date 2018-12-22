from flask import Flask, render_template, url_for

from models.lawyer import Lawyer

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('index.html',title='Login')

@app.route('/register')
def register():
    return render_template('register.html',title='Registration')

if __name__ == '__main__':
    app.run(debug=True)
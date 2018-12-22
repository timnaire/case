from flask import Flask, render_template, url_for, request, session, redirect
from config import SECRET_KEY

from models.lawyer import Lawyer


app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.route('/')
def login():
    return render_template('login.html',title='Login')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        specialize = request.form.get('specialize')
        bar_number = request.form.get('bar_number')

        lawyer = Lawyer.save(first_name=first_name,last_name=last_name,email=email,phone=phone,specialize=specialize,bar_number=bar_number,password='')
        if lawyer:
            return redirect(url_for('verify'))
        else:
            return redirect(
                url_for('register',
                    err=1, m="Something went wrong please try again."))

    return render_template('register.html',title='Registration')

@app.route('/verify')
def verify():
    return render_template('verify.html', title='Verifying details')

if __name__ == '__main__':
    app.run(debug=True)
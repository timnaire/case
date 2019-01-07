import logging
from flask import Flask, render_template, url_for, request, session, redirect
from config import SECRET_KEY

from models.lawyer import Lawyer
from decorators import login_required
from functions import json_response

app = Flask(__name__)
app.secret_key = SECRET_KEY

#home page for client
@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        main_category = request.form.get('main_category')
        location = request.form.get('location')
    
        return redirect(url_for('sub_category',main_category=main_category,location=location))

    return render_template('home.html',title='Home')

#home page for lawyers
@app.route('/mypage/dashboard')
@login_required
def dashboard():
    return render_template('mypage/dashboard.html',title="Welcome to Dashboard",lawyer=session['lawyer'])

#sign in route
@app.route('/signin/lawyer',methods=['GET','POST'])
def lawyer_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        lawyer = Lawyer.login(email=email,password=password)
        if lawyer:
            session['lawyer'] = lawyer.key.id()
            return redirect(url_for('dashboard'))
        else:
            return redirect(
                url_for('lawyer_login',
                    err=1, m="These credentials do not match our records."))

    return render_template('lawyer_login.html',title='Lawyer Login')

#sign up attorney route
@app.route('/signup/lawyer', methods=['GET','POST'])
def lawyer_registration():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        office = request.form.get('office')
        law_practice = request.form.get('law_practice')
        bar_number = request.form.get('bar_number')
        
        lawyer = Lawyer.save(first_name=first_name,last_name=last_name,email=email,phone=phone,office=office,law_practice=law_practice,bar_number=bar_number,password='')
        if lawyer:
            return json_response({
                'code': 200,
                'message': 'Thank you, We will contact you soon.'})
        else:
            return json_response({
                'code': 400,
                'message': 'Something went wrong, Please try again.'})

    return render_template('lawyer_registration.html',title='Lawyer Registration')

#reset password for the first time
@app.route('/password/reset',methods=['GET','POST'])
def reset_password():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password == confirm_password:
            lawyer = Lawyer.f_reset_password(email=email,password=password)
            if lawyer:
                return redirect(url_for('reset_password',succ=1,m='Password has been reset'))
            else:
                return redirect(
                url_for('reset_password',
                    err=1, m="These credentials do not match our records."))
        else:
            return redirect(
                url_for('reset_password',
                    err=1, m="Confirm password does not match."))
    return render_template('lawyer_frespass.html',title='Reset Password')

@app.route('/mypage/logout')
def logout():
    del session['lawyer']
    return redirect(url_for('lawyer_login'))

@app.errorhandler(500)
def error_500(e):
    logging.exception(e)
    return 'Something went wrong'

@app.errorhandler(404)
def error_404(e):
    logging.exception(e)
    return 'Page not found'

if __name__ == '__main__':
    app.run(debug=True)
import logging
from flask import Flask, render_template, url_for, request, session, redirect
from config import SECRET_KEY

from models.lawyer import Lawyer
from decorators import login_required_lawyer, login_required_client
from functions import json_response, is_email

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
@login_required_lawyer
def dashboard():
    return render_template('mypage/dashboard.html',title="Welcome to Dashboard",lawyer=session['lawyer'])

#sign in for client
@app.route('/signin/client',methods=['GET','POST'])
def client_login():
    return render_template('clientpages/client_login.html',title='Client Login')

@app.route('/signup/client',methods=['GET','POST'])
def client_registration():
    return render_template('clientpages/client_registration.html',title='Client Login')

#updating the lawyer
@app.route('/update/lawyer',methods=['GET','POST'])
def lawyer_update():
    if request.method == 'POST':
        req_data = request.get_json(force=True)

        if session['lawyer']:

            if 'first_name' in req_data:
                first_name = req_data['first_name']
            if 'last_name' in req_data:
                last_name = req_data['last_name']
            if 'email' in req_data:
                email = req_data['email']
            if 'phone' in req_data:
                phone = req_data['phone']
            if 'province' in req_data:
                province = req_data['province']    
            if 'office' in req_data:
                office = req_data['office']
            if 'law_practice' in req_data:
                law_practice = req_data['law_practice']

        #all fields required
        if first_name and last_name and email and phone and office and law_practice:
            #valid email address
            if is_email(email):
                lawyer = Lawyer.check_email(email)
                if not lawyer:
                    lawyer = Lawyer.update(first_name=first_name,last_name=last_name,email=email,phone=phone,province=province,office=office,law_practice=law_practice)
                    if lawyer:
                        return json_response({
                            'code': 200,
                            'message': 'Your account has been updated.'})
                    else:
                        return json_response({
                            'code': 400,
                            'message': 'Unable to process your request.'})
                else:
                    return json_response({
                            'code': 400,
                            'message': 'Email already taken, Please try again.'})
            else:
                return json_response({
                        'code': 400,
                        'message': 'You have entered an invalid email address, Please try again.'})
        else:

            return json_response({
                        'code': 400,
                        'message': 'Please provide all the information below.'})

    return render_template('lawyer_update.html',title='Lawyer Profile')
            

#sign in route
@app.route('/signin/lawyer',methods=['GET','POST'])
def lawyer_login():
    if request.method == 'POST':
        req_data = request.get_json(force=True)

        if 'email' in req_data:
            email = req_data['email']
        if 'password' in req_data:
            password = req_data['password']

        lawyer = Lawyer.login(email=email,password=password)
        if lawyer:
            session['lawyer'] = lawyer.key.id()
            return json_response({
                'code': 200,
                'message': 'Successfully Logged in.'})
        else:
            return json_response({
                'code': 400,
                'message': 'Credintials do not much, Please try again.'})

    return render_template('lawyer_login.html',title='Lawyer Login')

#sign up attorney route
@app.route('/signup/lawyer', methods=['GET','POST'])
def lawyer_registration():
    if request.method == 'POST':
        req_data = request.get_json(force=True)

        if 'first_name' in req_data:
            first_name = req_data['first_name']
        if 'last_name' in req_data:
            last_name = req_data['last_name']
        if 'email' in req_data:
            email = req_data['email']
        if 'phone' in req_data:
            phone = req_data['phone']
        if 'province' in req_data:
            province = req_data['province']    
        if 'office' in req_data:
            office = req_data['office']
        if 'law_practice' in req_data:
            law_practice = req_data['law_practice']
        if 'bar_number' in req_data:
            bar_number = req_data['bar_number']

        #all fields required
        if first_name and last_name and email and phone and office and law_practice and bar_number:
            #valid email address
            if is_email(email):
                lawyer = Lawyer.check_email(email)
                if not lawyer:
                    lawyer = Lawyer.save(first_name=first_name,last_name=last_name,email=email,phone=phone,province=province,office=office,law_practice=law_practice,bar_number=bar_number,password='admin')
                    if lawyer:
                        return json_response({
                            'code': 200,
                            'message': 'Thank you for registering, We will contact you soon.'})
                    else:
                        return json_response({
                            'code': 400,
                            'message': 'Unable to process your request.'})
                else:
                    return json_response({
                            'code': 400,
                            'message': 'Email already taken, Please try again.'})
            else:
                return json_response({
                        'code': 400,
                        'message': 'You have entered an invalid email address, Please try again.'})
        else:

            return json_response({
                        'code': 400,
                        'message': 'Please provide all the information below.'})

    return render_template('lawyer_registration.html',title='Lawyer Registration')

@app.route('/mypage/myaccount')
def myaccount():
    return render_template('mypage/myaccount.html',title="My Account")

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
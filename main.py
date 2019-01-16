import logging
import base64
from flask import Flask, render_template, url_for, request, session, redirect, abort, json
from config import SECRET_KEY

from models.lawyer import Lawyer
from decorators import login_required_lawyer, login_required_client
from functions import json_response, is_email, save_to_gcs

app = Flask(__name__)
app.secret_key = SECRET_KEY

#home page for client
@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():

    return render_template('home.html',title='Home')

#dashboard for lawyers
@app.route('/mypage/dashboard')
@login_required_lawyer
def dashboard():
    return render_template('mypage/dashboard.html',title="Welcome to Dashboard",lawyer=session['lawyer'])

#myaccount for lawyers / editing profile
@app.route('/mypage/myaccount/<int:lawyer_id>',methods=['GET','POST'])
@login_required_lawyer
def myaccount(lawyer_id=None):
    response = {}
    if request.method == "POST":
        # req_data = request.get_json(force=True)
        # if 'profile_pic' in req_data:
        #     profile_pic = req_data['profile_pic']
        f = request.files.get('image')
        if f and f.filename != '':
            response["serving_url"] = save_to_gcs(f).get("serving_url")
        return json_response(response)

    law_practice = {'family':"Family", 'employment': 'Employment', 'criminal_defense': 'Criminal Defense',
        'real_estate': 'Real Estate', 'business' : 'Business', 'personal_injury': 'Personal Injury',
        'wills_trusts_estates':'Wills & Estates', 'bankruptcy_finance':'Bankruptcy','intellectual_property':'Intellectual Property',
        'others':'Others'}
    if lawyer_id:
        lawyer_dict = Lawyer.get_by_id(int(lawyer_id))
        if lawyer_dict:
            lawyer_dict = lawyer_dict.to_dict()
        else:
            abort(404)

    return render_template("mypage/myaccount.html",title="My Profile",lawyer=session.get('lawyer'),lawyer_dict=lawyer_dict,law_practice=law_practice)

#sign in route
@app.route('/signin/lawyer',methods=['GET','POST'])
def lawyer_login():
    if request.method == 'POST':
        req_data = request.get_json(force=True)
        
        if 'email' in req_data:
            email = req_data['email']
        if 'password' in req_data:
            password = req_data['password']

        if is_email(email):
            lawyer = Lawyer.login(email=email,password=password)
            if lawyer:
                session['lawyer'] = lawyer.key.id()
                return json_response({
                    'code' : 200,
                    'message' : 'Successfully Logged in.',
                    'first_name' : lawyer.first_name,
                    'last_name': lawyer.last_name,
                    'email': lawyer.email,
                    'phone': lawyer.phone,
                    'city': lawyer.city,
                    'office': lawyer.office,
                    'law_practice': lawyer.law_practice,
                    'profile_pic': lawyer.profile_pic
                    })
            else:
                return json_response({
                    'code': 401,
                    'message': 'Credintials do not much, Please try again.',
                    'email' : email
                    })
        else:
            return json_response({
                    'code': 406,
                    'message': 'Please check your email and password to login.',
                    'email' : email
                    })

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
        if 'city' in req_data:
            city = req_data['city']    
        if 'office' in req_data:
            office = req_data['office']
        if 'law_practice' in req_data:
            law_practice = req_data['law_practice']

        #all fields required
        if first_name and last_name and email and phone and city and office and law_practice:
            #valid email address
            if is_email(email):
                lawyer = Lawyer.check_email(email)
                if not lawyer:
                    lawyer = Lawyer.save(first_name=first_name,last_name=last_name,email=email,phone=phone,city=city,office=office,law_practice=law_practice,password='')
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

# @app.errorhandler(500)
# def error_500(e):
#     logging.exception(e)
#     return 'Something went wrong'

# @app.errorhandler(404)
# def error_404(e):
#     logging.exception(e)
#     return 'Page not found'

if __name__ == '__main__':
    app.run(debug=True)
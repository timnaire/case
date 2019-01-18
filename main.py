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
@app.route('/lawyer/dashboard')
@login_required_lawyer
def dashboard():
    return render_template('lawyer/lawyer-dashboard.html',title="Welcome to Dashboard",lawyer=session['lawyer'])

# profile picture route
@app.route('/lawyer/account-setting/<int:lawyer_id>/profile-picture', methods=['POST'])
@login_required_lawyer
def lawyer_update_picture(lawyer_id=None):
    if request.method == "POST":
        f = request.files.get('image')
        if f and f.filename != '':
            profile_pic = save_to_gcs(f).get("serving_url")
            lawyer = Lawyer.save(id=lawyer_id, profile_pic=profile_pic)
            if lawyer:
                return json_response({
                    'error' : False,
                    'message' : "Profile picture has been saved!"
                })
            else:
                return json_response({
                    'error' : True,
                    'message' : "Profile picture was not saved!"
                })

# profile information route
@app.route('/lawyer/account-setting/<int:lawyer_id>/profile-information',methods=['POST'])
@login_required_lawyer
def lawyer_update_information(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'first_name' in req_data:
            first_name = req_data['first_name']
        if 'last_name' in req_data:
            last_name = req_data['last_name']
        if 'phone' in req_data:
            phone = req_data['phone']
        if 'province' in req_data:
            province = req_data['province']
        if 'office' in req_data:
            office = req_data['office']
        if 'law_practice' in req_data:
            law_practice = req_data['law_practice']

        lawyer = Lawyer.save(id=lawyer_id,first_name=first_name,last_name=last_name,phone=phone,province=province,office=office,law_practice=law_practice)
        if lawyer:
            return json_response({
                'error' : False,
                'message' : "Profile information has been saved!"
            })
        else:
            return json_response({
                'error' : True,
                'message' : "Profile information was not saved!"
            })

@app.route('/lawyer/account-setting/<int:lawyer_id>/change-email',methods=['POST'])
@login_required_lawyer
def lawyer_update_email(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'current' in req_data:
            current = req_data['current']
        if 'new_email' in req_data:
            newemail = req_data['new_email'] 
        if 'password' in req_data:
            password = req_data['password'] 
        # lawyer = Lawyer.change_email(id=lawyer_id,current=current,newemail=newemail,password=password)  
        # if lawyer:
        #     return json_response({
        #         'error' : False,
        #         'message' : "Email has been changed!"
        #     })
        # else:
        #     return json_response({
        #         'error' : True,
        #         'message' : "Email was not changed!"
        #     })

#main render template for account setting for lawyers / editing profile
@app.route('/lawyer/account-setting/<int:lawyer_id>',methods=['GET','POST'])
@login_required_lawyer
def lawyer_account_setting(lawyer_id=None):
    law_practice = {'Family':"Family", 'Employment': 'Employment', 'Criminal Defense': 'Criminal Defense',
        'Real Estate': 'Real Estate', 'Business' : 'Business', 'Immigration': 'Immigration' , 'Personal Injury': 'Personal Injury',
        'Wills & Estates':'Wills & Estates', 'Bankruptcy':'Bankruptcy','Intellectual Property':'Intellectual Property',
        'Others':'Others'}

    if lawyer_id:
        lawyer_dict = Lawyer.get_by_id(int(lawyer_id))
        if lawyer_dict:
            lawyer_dict = lawyer_dict.to_dict()
        else:
            abort(404)

    return render_template("lawyer/lawyer-account-setting.html",title="Account Setting",lawyer=session.get('lawyer'),lawyer_dict=lawyer_dict,law_practice=law_practice)

#sign in route
@app.route('/lawyer/signin',methods=['GET','POST'])
def lawyer_signin():
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
                    'error' : False,
                    'message' : 'Successfully Logged in.',
                    'first_name' : lawyer.first_name,
                    'last_name': lawyer.last_name,
                    'email': lawyer.email,
                    'phone': lawyer.phone,
                    'province': lawyer.province,
                    'office': lawyer.office,
                    'law_practice': lawyer.law_practice,
                    'profile_pic': lawyer.profile_pic
                    })
            else:
                return json_response({
                    'error': True,
                    'message': 'Credintials do not much, Please try again.',
                    'email' : email
                    })
        else:
            return json_response({
                    'error': True,
                    'message': 'Please check your email and password to login.',
                    'email' : email
                    })

    return render_template('lawyer/lawyer-signin.html',title='Sign In Lawyer')

#sign up attorney route
@app.route('/lawyer/signup', methods=['GET','POST'])
def lawyer_signup():
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

        #all fields required
        if first_name and last_name and email and phone and province and office and law_practice:
            #valid email address
            if is_email(email):
                lawyer = Lawyer.check_email(email)
                if not lawyer:
                    lawyer = Lawyer.save(first_name=first_name,last_name=last_name,email=email,phone=phone,province=province,office=office,law_practice=law_practice,password='')
                    if lawyer:
                        return json_response({
                            'error': False,
                            'message': 'Thank you for registering, We will contact you soon.'})
                    else:
                        return json_response({
                            'error': True,
                            'message': 'Unable to process your request.'})
                else:
                    return json_response({
                            'error': True,
                            'message': 'Email already taken, Please try again.'})
            else:
                return json_response({
                        'error': True,
                        'message': 'You have entered an invalid email address, Please try again.'})
        else:
            return json_response({
                        'error': True,
                        'message': 'Please provide all the information below.'})

    return render_template('lawyer/lawyer-signup.html',title='Try it for Free')

#reset password for the first time
@app.route('/lawyer/reset-password',methods=['GET','POST'])
def lawyer_reset_pass():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password == confirm_password:
            lawyer = Lawyer.f_reset_password(email=email,password=password)
            if lawyer:
                return redirect(url_for('lawyer_reset_pass',succ=1,m='Password has been reset'))
            else:
                return redirect(
                url_for('lawyer_reset_pass',
                    err=1, m="These credentials do not match our records.", email=email))
        else:
            return redirect(
                url_for('lawyer_reset_pass',
                    err=1, m="Confirm password does not match.",email=email))
    return render_template('lawyer/lawyer-reset-pass.html',title='Reset Password')

#######################################################

@app.route('/lawyer/signout')
def signout():
    del session['lawyer']
    return redirect(url_for('lawyer_signin'))

@app.errorhandler(500)
def error_500(e):
    logging.exception(e)
    return 'Something went wrong'

@app.errorhandler(404)
def error_404(e):
    logging.exception(e)
    return 'Page not found'
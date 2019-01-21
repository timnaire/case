import logging
from flask import Flask, render_template, url_for, request, session, redirect, abort
from config import SECRET_KEY

from models.lawyer import Lawyer
from models.practice import Practice
from decorators import login_required_lawyer, login_required_client
from functions import json_response, is_email, save_to_gcs

app = Flask(__name__)
app.secret_key = SECRET_KEY

law_practice = {'Family':"Family", 'Employment': 'Employment', 'Criminal Defense': 'Criminal Defense',
        'Business': 'Business', 'Personal Injury' : 'Personal Injury', 'Immigration': 'Immigration' ,
         'Bankruptcy': 'Bankruptcy','Wills, Trust, and Estates':'Wills, Trust, and Estates', 'Real Estate':'Real Estate',
         'Commercial Law':'Commercial Law' }

#home page for client
@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    global law_practice
    return render_template('home.html',title='Home',law_practice=law_practice)

#####################################################################################################################################
# for lawyers and below


# find a lawyer
@app.route('/lawyer/find',methods=['post'])
def find_lawyer():
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'law_practice' in req_data:
            law_practice = req_data['law_practice']
        if 'cityOrMunicipality' in req_data:
            cityOrMunicipality = req_data['cityOrMunicipality']

        respo = {}
        # lawyers = Lawyer.query(Lawyer.cityOrMunicipality == cityOrMunicipality, Lawyer.password != None).fetch()
        counter = 0
        # for lawyer in lawyers:
        #     practice = Practice.query(Lawyer.)
        #     respo[counter] = lawyer.to_dict()
        #     counter = counter + 1
        if law_practice and cityOrMunicipality:
            found_lawyers = Practice.find_practice(law_practice=law_practice, cityOrMunicipality=cityOrMunicipality)
            if found_lawyers:
                return json_response({
                    'error': False,
                    'lawyers' : found_lawyers})
            else:
                return json_response({
                    'error' : True,
                    'message': "No lawyer(s) found in "+cityOrMunicipality+" with practice of "+law_practice})

        else:
            return json_response({
                'error' : True,
                'message' : "Please select your legal issue and city to find lawyer."})

        return json_response(respo)

#dashboard for lawyers
@app.route('/lawyer/dashboard')
@login_required_lawyer
def dashboard():
    return render_template('lawyer/lawyer-dashboard.html',title="Welcome to Dashboard",lawyer=session['lawyer'])

# profile picture route
@app.route('/lawyer/<int:lawyer_id>/account-setting/profile-picture', methods=['POST'])
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
                    'message' : "Profile picture has been saved!",
                    'profile_pic' : save_to_gcs(f).get("serving_url")})
            else:
                return json_response({
                    'error' : True,
                    'message' : "Profile picture was not saved!"})

# profile information route
@app.route('/lawyer/<int:lawyer_id>/account-setting/profile-information',methods=['POST'])
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
        if 'cityOrMunicipality' in req_data:
            cityOrMunicipality = req_data['cityOrMunicipality']
        if 'office' in req_data:
            office = req_data['office']
        if 'aboutme' in req_data:
            aboutme = req_data['aboutme']
        if 'law_practice' in req_data:
            law_practice = req_data['law_practice']

        if first_name and last_name and phone and cityOrMunicipality and office and law_practice:
            lawyer = Lawyer.save(id=lawyer_id,first_name=first_name,last_name=last_name,phone=phone,cityOrMunicipality=cityOrMunicipality,office=office,aboutme=aboutme)
            if lawyer:
                lawyer = Lawyer.get_by_id(int(lawyer_id))
                practices = Practice.query(Practice.lawyer == lawyer.key).fetch()
                for practice in practices:
                    practice.key.delete()
                # saving new pick practice
                for pract in law_practice:
                    Practice.save(lawyer=lawyer_id,pract=pract)
                return json_response({
                    'error' : False,
                    'message' : "Profile information has been saved!"})
            else:
                return json_response({
                    'error' : True,
                    'message' : "Profile information was not saved!"})
        else:
            return json_response({
                'error' : True,
                'message' : "Please dont leave the fields empty."})

# changing email
@app.route('/lawyer/<int:lawyer_id>/account-setting/change-email',methods=['POST'])
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
        
        if current and newemail and password:
            # check if the current email is email
            if is_email(current):
                # check if the new email is email
                if is_email(newemail):
                    # check if the new email already exist or not
                    lawyer = Lawyer.email_exist(newemail=newemail)
                    if not lawyer:
                        # check if the password is correct
                        lawyer = Lawyer.check_pass(id=lawyer_id,password=password)
                        if lawyer:
                            # changing email
                            lawyer = Lawyer.change_email(id=lawyer_id,current=current,newemail=newemail,password=password)
                            if lawyer:
                                return json_response({"error" : False,
                                "message" : "Email has been changed!"})
                            else:
                                return json_response({"error" : True,
                                "message" : "Email was not changed, please try again."})
                        else:
                            return json_response({"error" : True,
                            "message" : "Incorrect password, please try again."})
                    else:
                        return json_response({"error" : True,
                        "message" : "Email already taken, please another email"})
                else:
                    return json_response({
                        "error" : True,
                        "message" : "Please enter a valid new email."})
            else:
                return json_response({
                    "error" : True,
                    "message" : "Please enter your correct email"}) 
        else:
            return json_response({
                "error" : True,
                "message" : "Please dont leave the fileds empty."})

# change password
@app.route('/lawyer/<int:lawyer_id>/account-setting/change-password',methods=['POST'])
@login_required_lawyer
def lawyer_update_password(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'current' in req_data:
            password = req_data['current']
        if 'newpass' in req_data:
            newpass = req_data['newpass']
        if 'confirm' in req_data:
            confirm = req_data['confirm']
        
        if password and newpass and confirm:
            lawyer = Lawyer.check_pass(id=lawyer_id, password=password)
            if lawyer:
                if newpass == confirm:
                    if newpass != password:
                        lawyer = Lawyer.change_pass(id=lawyer_id, password=password,newpass=newpass)
                        if lawyer:
                            return json_response({"error" : False,
                            "message" : "Password has been changed!"})
                        else:
                            return json_response({"error" : True,
                            "message" : "Password was not changed, please try again."})
                    else:
                        return json_response({'error' : True,
                        "message" : "New password must not be the same to your current password."})
                else:
                    return json_response({"error" : True,
                    "message" : "Confirm password does not match, please try again. "})
            else:
                return json_response({
                    "error" : True,
                    "message" : "Please enter your current password."})
        else:
            return json_response({
                "error" : True,
                "message" : "Please dont leave the fields empty"})

#main render template for account setting for lawyers / editing profile
@app.route('/lawyer/<int:lawyer_id>/account-setting',methods=['GET','POST'])
@login_required_lawyer
def lawyer_account_setting(lawyer_id=None):
    # get the lawyer details in a dictionary format
    global law_practice
    if lawyer_id:
        lawyer_dict = Lawyer.get_by_id(int(lawyer_id))
        if lawyer_dict:
            lawyer_dict = lawyer_dict.to_dict()
        else:
            abort(404)
    lawyer = Lawyer.get_by_id(int(lawyer_id))
    practices = Practice.query(Practice.lawyer == lawyer.key).fetch()
    practice_dict = []
    for practice in practices:
        practice_dict.append(practice.to_dict())

    return render_template("lawyer/lawyer-account-setting.html",title="Account Setting",lawyer=session.get('lawyer'),lawyer_dict=lawyer_dict,law_practice=law_practice,practices=practice_dict)

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
                    'cityOrMunicipality': lawyer.cityOrMunicipality,
                    'office': lawyer.office,
                    'profile_pic': lawyer.profile_pic})
            else:
                return json_response({
                    'error': True,
                    'message': 'Credintials do not much, Please try again.',
                    'email' : email})
        else:
            return json_response({
                    'error': True,
                    'message': 'Please check your email and password to login.',
                    'email' : email})

    if session.get('lawyer') is not None:
        return redirect(url_for('dashboard'))

    return render_template('lawyer/lawyer-signin.html',title='Sign In Lawyer')

#sign up attorney route
@app.route('/lawyer/signup', methods=['GET','POST'])
def lawyer_signup():
    global law_practice
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
        if 'cityOrMunicipality' in req_data:
            cityOrMunicipality = req_data['cityOrMunicipality']    
        if 'office' in req_data:
            office = req_data['office']
        if 'law_practice' in req_data:
            law_practice = req_data['law_practice']

        #all fields required
        if first_name and last_name and email and phone and cityOrMunicipality and office and law_practice:
            #valid email address
            if is_email(email):
                lawyer = Lawyer.check_email(email=email)
                if not lawyer:
                    lawyer = Lawyer.save(first_name=first_name,last_name=last_name,email=email,phone=phone,cityOrMunicipality=cityOrMunicipality,office=office,password='')
                    if lawyer:
                        # pract as in practice
                        for pract in law_practice:
                            Practice.save(lawyer=lawyer.key.id(),pract=pract)

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
                            'message': 'Email already taken, please try another email.'})
            else:
                return json_response({
                        'error': True,
                        'message': 'You have entered an invalid email address, Please try again.'})
        else:
            return json_response({
                        'error': True,
                        'message': 'Please provide all the information below.'})

    if session.get('lawyer') is not None:
        return redirect(url_for('dashboard'))
    
    return render_template('lawyer/lawyer-signup.html',title='Try it for Free',law_practice=law_practice)

#reset password for the first time
@app.route('/lawyer/reset-password',methods=['GET','POST'])
def lawyer_reset_pass():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if is_email(email):
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
                        err=1, m="Confirm password does not match, please try again.",email=email))
        else:
            return redirect(
                url_for('lawyer_reset_pass',
                err=1, m="You have entered an invalid email address, Please try again.",email=email))
    return render_template('lawyer/lawyer-reset-pass.html',title='Reset Password')

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
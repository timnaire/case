import logging
from flask import Flask, render_template, url_for, request, session, redirect, abort
from flask_mail import Mail, Message
from config import SECRET_KEY
import googlemaps
from models.lawyer import Lawyer
from models.client import Client
from models.practice import Practice
from models.case import Case
from decorators import login_required_lawyer
from functions import json_response, is_email, save_to_gcs

app = Flask(__name__)
app.secret_key = SECRET_KEY
gmaps = googlemaps.Client(key='AIzaSyCNHYz-iF2kippAtUQiv4hCPesfP_3G0ZE')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_USERNAME'] = 'casesteamaid@gmail.com'
app.config['MAIL_PASSWORD'] = 'Caseadmin123'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)
# Geocoding an address
# geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# client sign in
@app.route('/client/signin',methods=['GET','POST'])
def client_signin():
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'email' in req_data:
            email = req_data['email']
        if 'password' in req_data:
            password = req_data['password']

        if email and password:
            client = Client.sign_in(email=email,password=password)
            if client:
                session['client'] = client.key.id()
                return json_response({
                    "error" : False,
                    "message" : "Successfully signed in"})
            else:
                return json_response({
                    "error" : True,
                    "message" : "Unsuccessful sign in, please try again."})
        else:
            return json_response({
                "error" : True,
                "message" : "Please enter your email and password to sign in."})

@app.route('/client/signup',methods=['GET','POST'])
def client_signup():
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'first_name' in req_data:
            first_name = req_data['first_name']
        if 'last_name' in req_data:
            last_name = req_data['last_name']
        if 'email' in req_data:
            email = req_data['email']
        if 'phone' in req_data:
            phone = req_data['phone']
        if 'address' in req_data:
            address = req_data['address']
        if 'password' in req_data:
            password = req_data['password']
        if 'confirm' in req_data:
            confirm = req_data['confirm']
        
        if first_name and last_name and email and phone and address and password:
            if is_email(email=email):
                client = Client.check_email(email)
                if not client:
                    if password == confirm:
                        client = Client.save(first_name=first_name,last_name=last_name,email=email,phone=phone,address=address,password=password)
                        if client:
                            return json_response({
                                "error" : False,
                                "message" : "Successfully signed up"})
                    else:
                        return json_response({
                            "error" : True,
                            "message" : "Confirmation password does not match, please try again."})
                else:
                    return json_response({
                        "error" : True,
                        "message" : "Email already taken, please try again."})
            else:
                return json_response({
                    "error" : True,
                    "message" : "Invalid email address, Please try again."})
        else:
            return json_response({
                "error" : True,
                "message" : "Please provide your details to sign up."})
        

        
    return render_template('client/client-signup.html',title="Client Sign up")

# home page for client
@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    global available_practice
    return render_template('home.html',title='Home',law_practice=available_practice)

#####################################################################################################################################
# for lawyers and below

available_practice = {'Family':"Family", 'Employment': 'Employment', 'Criminal Defense': 'Criminal Defense',
        'Business': 'Business', 'Personal Injury' : 'Personal Injury', 'Immigration': 'Immigration' ,
         'Bankruptcy': 'Bankruptcy','Wills, Trust, and Estates':'Wills, Trust, and Estates', 'Real Estate':'Real Estate',
         'Commercial Law':'Commercial Law' }

# find a lawyer route
@app.route('/lawyer/find',methods=['GET','POST'])
def find_lawyer():
    if request.method == "POST":        
        
        law_practice=request.get('lawpractice')
        cityOrMunicipality = request.get('city')
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

    return render_template('lawyer-found.html',title='Find',law_practice=available_practice,response=json_response)

#dashboard route for lawyers
@app.route('/lawyer/')
@app.route('/lawyer/dashboard')
@login_required_lawyer
def dashboard():
    return render_template('lawyer/lawyer-dashboard.html',title="Welcome to Dashboard",lawyer=session['lawyer'])

# mycase route for lawyers 
@app.route('/lawyer/<int:lawyer_id>/mycase', methods=['GET','POST'])
# @login_required_lawyer
def mycase(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'case_title' in req_data:
            case_title = req_data['case_title']
        if 'client_id' in req_data:
            client_id = req_data['client_id']
        if 'case_description' in req_data:
            case_description = req_data['case_description']
        
        if case_title and client_id and case_description:
            case = Case.save(lawyer=lawyer_id,case_title=case_title,client_id=client_id,case_description=case_description)
            if case:
                return json_response({
                    "error" : False,
                    "message" : "New case added."})
            else:
                return json_response({
                    "error" : True,
                    "message" : "Couldn't add a case, please try again."})
        else:
            return json_response({
                'error' : True,
                'message' : 'Please input the case name and try again.'})

    lawyer = Lawyer.get_by_id(int(lawyer_id))
    cases = Case.query(Case.lawyer == lawyer.key).fetch()
    case_dict = []
    for case in cases:
        case_dict.append(case.to_dict())
    return render_template('lawyer/lawyer-mycase.html',title="My Case",lawyer=session['lawyer'],cases=case_dict)

@app.route('/lawyer/<int:lawyer_id>/getAllCase',methods=['GET','POST'])
def getAllCase(lawyer_id=None):
    lawyer = Lawyer.get_by_id(int(lawyer_id))
    cases = Case.query(Case.lawyer == lawyer.key).fetch()
    case_dict = []
    for case in cases:
        case_dict.append(case.to_dict())
        
    return json_response({"cases" : case_dict})


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
                    'message' : "Profile picture has been saved!"})
            else:
                return json_response({
                    'error' : True,
                    'message' : "Profile picture was not saved!"})

# for mobile upload with no login required
@app.route('/lawyer/<int:lawyer_id>/profile-picture', methods=['POST'])
def update_lawyer_picture(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'profile_pic' in req_data:
            profile_pic = req_data['profile_pic']
            
        lawyer = Lawyer.save(id=lawyer_id, profile_pic=profile_pic)
        if lawyer:
            return json_response({
                'error' : False,
                'message' : "Profile picture has been saved!"})
        else:
            return json_response({
                'error' : True,
                'message' : "Profile picture was not saved!"})

# profile information route
@app.route('/lawyer/<int:lawyer_id>/account-setting/profile-information',methods=['POST'])
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

#main render template for account setting for lawyers / editing profile route
@app.route('/lawyer/<int:lawyer_id>/account-setting',methods=['GET','POST'])
@login_required_lawyer
def lawyer_account_setting(lawyer_id=None):
    # get the lawyer details in a dictionary format
    global available_practice
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

    return render_template("lawyer/lawyer-account-setting.html",title="Account Setting",lawyer=session.get('lawyer'),lawyer_dict=lawyer_dict,law_practice=available_practice,practices=practice_dict)

# @app.route('/lawyer/<int:lawyer_id>/get-lawyer',methods=['GET'])
# def getLawyer(lawyer_id=None):
#     if lawyer_id:
#         lawyer_dict = Lawyer.get_by_id(int(lawyer_id))
#         if lawyer_dict:
#             lawyer_dict = lawyer_dict.to_dict()
#             return json_response(lawyer_dict)
#         else:
#             abort(404)
    
@app.route('/lawyer/<int:lawyer_id>/get-lawyer-practice',methods=['GET'])
def getPractice(lawyer_id=None):
    lawyer = Lawyer.get_by_id(int(lawyer_id))
    practices = Practice.query(Practice.lawyer == lawyer.key).fetch()
    practice_dict = []
    for practice in practices:
        practice_dict.append(practice.practice())
    return json_response({ "practice" : practice_dict})

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
            lawyer = Lawyer.sign_in(email=email,password=password)
            if lawyer:
                session['lawyer'] = lawyer.key.id()
                return json_response({
                    'error' : False,
                    'message' : 'Successfully Logged in.',
                    'lawyer' : lawyer.key.id(),
                    'first_name' : lawyer.first_name,
                    'last_name': lawyer.last_name,
                    'email': lawyer.email,
                    'phone': lawyer.phone,
                    'cityOrMunicipality': lawyer.cityOrMunicipality,
                    'office': lawyer.office,
                    'profile_pic': lawyer.profile_pic,
                    'aboutme' : lawyer.aboutme })
            else:
                return json_response({
                    'error': True,
                    'message': 'Credintials do not much, Please try again.',
                    'email' : email})
        else:
            return json_response({
                    'error': True,
                    'message': 'Please check your email and password and try again.',
                    'email' : email})

    if session.get('lawyer') is not None:
        return redirect(url_for('dashboard'))

    return render_template('lawyer/login.html',title='Sign In Lawyer')

#sign up lawyer route
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
        if 'cityOrMunicipality' in req_data:
            cityOrMunicipality = req_data['cityOrMunicipality']    
        if 'office' in req_data:
            office = req_data['office']
        if 'law_practice' in req_data:
            law_practice = req_data['law_practice']
        if 'password' in req_data:
            password = req_data['password']
        if 'confirm_password' in req_data:
            confirm_password = req_data['confirm_password']

        #all fields required
        if first_name and last_name and email and phone and cityOrMunicipality and office and law_practice and password:
            #valid email address
            if is_email(email):
                lawyer = Lawyer.check_email(email=email)
                if not lawyer:
                    if password == confirm_password:

                        lawyer = Lawyer.save(first_name=first_name,last_name=last_name,email=email,phone=phone,cityOrMunicipality=cityOrMunicipality,office=office,password=password,status="deactivate")
                        if lawyer:
                            # pract as in practice
                            for pract in law_practice:
                                Practice.save(lawyer=lawyer.key.id(),pract=pract)

                            return json_response({
                                'error': False,
                                'message': 'Thank you for signing up, We will contact you soon.'})
                        else:
                            return json_response({
                                'error': True,
                                'message': 'Unable to process your request.'})
                    else:
                        return json_response({
                            'error': True,
                            'message' : "Confirm password does not match, please try again."})
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
    global available_practice
    
    return render_template('lawyer/lawyer-signup.html',title='Try it for Free',law_practice=available_practice)

#reset password for the first time route
@app.route('/lawyer/add-password',methods=['GET','POST'])
def lawyer_add_password():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if is_email(email):
            if password == confirm_password:
                lawyer = Lawyer.add_password(email=email,password=password)
                if lawyer:
                    return redirect(url_for('lawyer_add_password',succ=1,m='Password has been reset'))
                else:
                    return redirect(
                    url_for('lawyer_add_password',
                        err=1, m="These credentials do not match our records.", email=email))
            else:
                return redirect(
                    url_for('lawyer_add_password',
                        err=1, m="Confirmation password does not match, please try again.",email=email))
        else:
            return redirect(
                url_for('lawyer_add_password',
                err=1, m="You have entered an invalid email address, Please try again.",email=email))
    return render_template('lawyer/lawyer-add-pass.html',title='Reset Password')

# send email with token 
def send_reset_email(lawyer):
    token = lawyer.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@case.com', recipients=[lawyer.email])
    msg.body  = "To reset your password, visit the following link: \n" + url_for('lawyer_reset_token',token=token, _external=True) +"\n if you did not make this request then simply ignore this email and no changes will be made."
    mail.send(msg)

# ask for email to reset password
@app.route('/lawyer/reset-password',methods=['GET','POST'])
def lawyer_reset_request():
    if session.get('lawyer') is not None:
        return redirect(url_for('dashboard'))

    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'email' in req_data:
            email = req_data['email']
        if email:
            if is_email(email):
                lawyer = Lawyer.check_email(email)
                if lawyer:
                    send_reset_email(lawyer)
                else:
                    return json_response({
                        "error": True,
                        "message" : "Sorry, your email does not match our records."})
            else:
                return json_response({
                    "error" : True,
                    "message" : "Invalid email address, please try again."})
        else:
            return json_response({
                "error" : True,
                "message" : "Please enter your email."})
    return render_template('lawyer/lawyer-reset-pass.html',title="Reset")

# resetting password with new password
@app.route('/lawyer/reset-password/<token>',methods=['GET','POST'])
def lawyer_reset_token(token):
    if session.get('lawyer') is not None:
        return redirect(url_for('dashboard'))
    lawyer = Lawyer.verify_reset_token(token)
    if lawyer is None:
        return json_response({
            "error" : True,
            "message" : "That is an invalid or expired token"})
    else:
        if request.method == "POST":
            req_data = request.get_json(force=True)
            if 'password' in req_data:
                password = req_data['password']
            if 'confirm' in req_data:
                confirm = req_data['confirm']
            
            if password and confirm:
                if password == confirm:
                    lawyer = lawyer.save(id=lawyer.key.id(),password=password,status="activated")
                    if lawyer:
                        return json_response({
                            "error" : False,
                            "message" : "Your password has been updated! You are now able to sign in."})
                else:
                    return json_response({
                        "error" : True,
                        "message" : "Confirmation password does not match, please try again."})
            else:
                return json_response({
                    "error" : True,
                    "message" : "Please fill up the fields to reset password."})
        
    return render_template('lawyer/lawyer-reset-token.html',title="Reset Password",token=token)


# sign out route
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

if __name__ == "__main__":
    app.run()
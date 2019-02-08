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

# method to check if the lawyer exist in cebu lawyer list.
def get_rollno(rollno):
    lawyer = None
    with open("cebulawyers.txt") as line:
        for l in line:
            if rollno in l:
                lawyer = True
    return lawyer

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
                    "message" : "Successfully signed in",
                    "client" : client.key.id(),
                    "first_name" : client.first_name,
                    "last_name" : client.last_name,
                    "email" : client.email,
                    "phone" : client.phone,
                    "address" : client.address})
            else:
                return json_response({
                    "error" : True,
                    "message" : "Credentials do not match, please try again."})
        else:
            return json_response({
                "error" : True,
                "message" : "Please check your email and password and try again."})

    if session.get('client') is not None:
        return redirect(url_for('dashboard'))

    return render_template('lawyer/login.html',title='Sign In')

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
                                "message" : "Unable to process your request."})
                    else:
                        return json_response({
                            "error" : True,
                            "message" : "Confirmation password does not match, please try again."})
                else:
                    return json_response({
                        "error" : True,
                        "message" : "Email already taken, please try another email."})
            else:
                return json_response({
                    "error" : True,
                    "message" : "You have entered an invalid email address, please try again."})
        else:
            return json_response({
                "error" : True,
                "message" : "Please dont leave the fields empty and try again."})
        
    return render_template('client/client-signup.html',title="Client Sign up")

# for mobile upload with no login required
@app.route('/client/<int:client_id>/profile-picture', methods=['POST'])
def update_client_picture(client_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'profile_pic' in req_data:
            profile_pic = req_data['profile_pic']
            
        client = Client.save(id=client_id, profile_pic=profile_pic)
        if client:
            return json_response({
                'error' : False,
                'message' : "Profile picture has been saved!"})
        else:
            return json_response({
                'error' : True,
                'message' : "Profile picture was not saved!"})

# profile information route
@app.route('/client/<int:client_id>/account-setting/profile-information',methods=['POST'])
def client_update_information(client_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'first_name' in req_data:
            first_name = req_data['first_name']
        if 'last_name' in req_data:
            last_name = req_data['last_name']
        if 'phone' in req_data:
            phone = req_data['phone']
        if 'address' in req_data:
            address = req_data['address']

        if first_name and last_name and phone and address:
            client = Client.save(id=client_id,first_name=first_name,last_name=last_name,phone=phone,address=address)
            if client:
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
@app.route('/client/<int:client_id>/account-setting/change-email',methods=['POST'])
def client_update_email(client_id=None):
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
                    client = Client.email_exist(newemail=newemail)
                    if not client:
                        # check if the password is correct
                        client = Client.check_pass(id=client_id,password=password)
                        if client:
                            # changing email
                            client = Client.change_email(id=client_id,current=current,newemail=newemail,password=password)
                            if client:
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
                        "message" : "Email already taken, please try another email"})
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
@app.route('/client/<int:client_id>/account-setting/change-password',methods=['POST'])
def client_update_password(client_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'current' in req_data:
            password = req_data['current']
        if 'newpass' in req_data:
            newpass = req_data['newpass']
        if 'confirm' in req_data:
            confirm = req_data['confirm']
        
        if password and newpass and confirm:
            client = Client.check_pass(id=client_id, password=password)
            if client:
                if newpass == confirm:
                    if newpass != password:
                        client = Client.change_pass(id=client_id, password=password,newpass=newpass)
                        if client:
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
                    "message" : "Confirmation password does not match, please try again. "})
            else:
                return json_response({
                    "error" : True,
                    "message" : "Please enter your current password."})
        else:
            return json_response({
                "error" : True,
                "message" : "Please dont leave the fields empty"})


available_practice = {'Constitutional Law':"Constitutional Law", 'Criminal Law': 'Criminal Law', 'Business Law': 'Business Law',
        'Labor Law': 'Labor Law', 'Civil Law' : 'Civil Law', 'Taxation Law': 'Taxation Law' ,'Family Law': 'Family Law'}

# home page for client
@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    global available_practice
    if request.method == "POST":
        law_practice = request.form.get('lawpractice')
        cityOrMunicipality = request.form.get('cityOrMunicipality')
        return redirect(url_for('find_lawyer',practice=law_practice,cityOrMunicipality=cityOrMunicipality))

    if session.get('lawyer') is not None:
        return render_template('home.html',title='Home',lawyer=session['lawyer'],law_practice=available_practice)
    else:
        return render_template('home.html',title='Home',law_practice=available_practice)

#####################################################################################################################################
# for lawyers and below

# appoint lawyer 
@app.route('/lawyer/<int:client_id>/pre-appoint',methods=['POST'])
def lawyer_clicked(client_id=None):
    if request.methods == "POST":
        lawyer_id = request.form.get('id')
        lawyer = Lawyer.get_by_id(int(lawyer_id))
        event = Event.save(lawyer=lawyer_id,client=client_id,event_type="pre-appointment")
        if event:
            return json_response({
                "error" : False,
                "message" : "You have now set a pre appointment with "+lawyer.first_name+" "+lawyer.last_name})
        else:
            return json_response({
                "error" : True,
                "message" : "Pre-appointment was not made, please try again."})
        
# find a lawyer route
@app.route('/lawyer/found',methods=['GET','POST'])
def find_lawyer():
    lawyers = None
    found_lawyers = []
    if request.method == "POST":        
        law_practice = request.form.get('lawpractice')
        cityOrMunicipality = request.form.get('city')
        if law_practice and cityOrMunicipality:
            found_lawyers = Practice.find_practice(law_practice=law_practice, cityOrMunicipality=cityOrMunicipality)
            if found_lawyers:

                lawyers = found_lawyers
                return render_template('lawyer-found.html',title='Find',law_practice=available_practice,results=lawyers)
                #return json_response({"found" : found_lawyers})
            else:
                return redirect(json_response({
                    'error' : True,
                    'message': "No lawyer(s) found in "+cityOrMunicipality+" with practice of "+law_practice}))
        else:
            return redirect(json_response({
                'error' : True,
                'message' : "Please select your legal issue and city to find lawyer."}))
    
    law_practice = request.args.get('practice')
    cityOrMunicipality = request.args.get('cityOrMunicipality')

    # if law_practice and cityOrMunicipality:
    #     found_lawyers = Practice.find_practice(law_practice=law_practice, cityOrMunicipality=cityOrMunicipality)
    #     if found_lawyers:
    #         lawyers = found_lawyers
    #     else:
    #         lawyers = None
    

    return render_template('lawyer-found.html',title='Find',law_practice=available_practice,results=lawyers)

#dashboard route for lawyers
@app.route('/lawyer/')
@app.route('/lawyer/dashboard')
@login_required_lawyer
def dashboard():
    return render_template('lawyer/lawyer-dashboard.html',title="Welcome to Dashboard",lawyer=session['lawyer'])

@app.route('/lawyer/<int:lawyer_id>/add-event',methods=['GET','POST'])
def add_event(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'client_id' in req_data:
            client_id = req_data['client_id']
        if 'event_content' in req_data:
            event_content = req_data['event_data']
        if 'event_type' in req_data:
            event_type = req_data['event_type']
        if 'date' in req_data:
            date = req_data['date']

        if client_id and event_content and event_type and date:
            event = Event.save(lawyer=lawyer_id, client=client_id,event_content=event_content,event_type=event_type,date=date)
            if event:
                return json_response({
                    "error" : False,
                    "message" : "Event created !"})
            else:
                return json_response({
                    "error" : True,
                    "message" : "Couldn't create event, please try again."})
        else:
            return json_response({
                "error" : True,
                "message" : "Please fill up all the fields and try again."})

@app.route('/lawyer/<int:lawyer_id>/list-client',methods=['GET','POST'])
def list_client(lawyer_id=None):
    list_of_clients = Case.lawyers_client(lawyer=lawyer_id)
    if list_of_clients:
        return json_response({
            "error" : False,
            "message" : "Found clients",
            "clients" : list_of_clients})
    else:
        return json_response({
            "error" : True,
            "message" : "No clients found.",})

@app.route('/lawyer/<int:lawyer_id>/get-event',methods=['GET','POST'])
def get_event(lawyer_id=None):
    lawyer = Lawyer.get_by_id(int(lawyer_id))
    events = Event.query(Event.lawyer == lawyer.key).fetch()
    event_dict = []
    for event in events:
        event_dict.append(event.to_dict())
        
    return json_response({"events" : event_dict})

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
            case = Client.get_client(client_id=client_id)
            if case:
                case = Case.save(lawyer=lawyer_id,case_title=case_title,client_id=client_id,case_description=case_description,status='Active')
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
                    "error" : True,
                    "message" : "No client found with that id, please try again."})
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

@app.route('/lawyer/<int:lawyer_id>/get-case',methods=['GET','POST'])
def getAllCase(lawyer_id=None):
    lawyer = Lawyer.get_by_id(int(lawyer_id))
    cases = Case.query(Case.lawyer == lawyer.key).fetch()
    if cases != None:
        case_dict = []
        for case in cases:
            case_dict.append(case.to_dict())
        return json_response({
            "error" : False,
            "message" : `len(case_dict)`+" case(s) found.",
            "cases" : case_dict})
    else:
        return json_response({ 
            "error" : True,
            "message" : "No case found",
            "cases" : "Empty"})

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
        if 'firm' in req_data:
            firm = req_data['firm']
        if 'aboutme' in req_data:
            aboutme = req_data['aboutme']
        if 'law_practice' in req_data:
            law_practice = req_data['law_practice']

        if first_name and last_name and phone and cityOrMunicipality and office and law_practice:
            lawyer = Lawyer.save(id=lawyer_id,first_name=first_name,last_name=last_name,phone=phone,cityOrMunicipality=cityOrMunicipality,office=office,firm=firm,aboutme=aboutme)
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
                    'firm': lawyer.firm,
                    'profile_pic': lawyer.profile_pic,
                    'aboutme' : lawyer.aboutme })
            else:
                return json_response({
                    'error': True,
                    'message': 'Credentials do not match, please try again.',
                    'email' : email})
        else:
            return json_response({
                    'error': True,
                    'message': 'Please check your email and password and try again.',
                    'email' : email})

    if session.get('lawyer') is not None:
        return redirect(url_for('dashboard'))

    return render_template('lawyer/login.html',title='Sign In')

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
        if 'rollno' in req_data:
            rollno = req_data['rollno']
        if 'cityOrMunicipality' in req_data:
            cityOrMunicipality = req_data['cityOrMunicipality']    
        if 'office' in req_data:
            office = req_data['office']
        if 'firm' in req_data:
            firm = req_data['firm']
        if 'law_practice' in req_data:
            law_practice = req_data['law_practice']
        if 'password' in req_data:
            password = req_data['password']
        if 'confirm' in req_data:
            confirm = req_data['confirm']

        #all fields required
        if first_name and last_name and email and phone and rollno and cityOrMunicipality and office and law_practice and password and confirm:
            #valid email address
            if is_email(email):
                lawyer = Lawyer.check_email(email=email)
                if not lawyer:
                    if password == confirm:
                        if get_rollno(str(rollno)):
                            roll_exist = Lawyer.rollno_exist(rollno=rollno)
                            if not roll_exist:
                                lawyer = Lawyer.save(first_name=first_name,last_name=last_name,email=email,phone=phone,rollno=rollno,cityOrMunicipality=cityOrMunicipality,office=office,firm=firm,password=password,status="activated")
                                if lawyer:
                                    # pract as in practice
                                    for pract in law_practice:
                                        Practice.save(lawyer=lawyer.key.id(),pract=pract)
                                    return json_response({
                                        'error': False,
                                        'message': 'Thank you for signing up, you can now log into your account.'})
                                else:
                                    return json_response({
                                        'error': True,
                                        'message': 'Unable to process your request.'})
                            else:
                                return json_response({
                                    'error': True,
                                    'message': 'Account with roll number '+rollno+' already exist. Contact us if you need help.'})
                        else:
                            lawyer = Lawyer.save(first_name=first_name,last_name=last_name,email=email,phone=phone,rollno=rollno,cityOrMunicipality=cityOrMunicipality,office=office,firm=firm,password=password,status="deactivated")
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
                            'message' : "Confirmation password does not match, please try again."})
                else:
                    return json_response({
                            'error': True,
                            'message': 'Email already taken, please try another email.'})
            else:
                return json_response({
                        'error': True,
                        'message': 'You have entered an invalid email address, please try again.'})
        else:
            return json_response({
                        'error': True,
                        'message': 'Please dont leave the fields empty and try again.'})

    if session.get('lawyer') is not None:
        return redirect(url_for('dashboard'))
    global available_practice
    
    return render_template('lawyer/lawyer-signup.html',title='Try it for Free',law_practice=available_practice)

# send email with token client
def send_reset_email(client):
    token = client.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@case.com', recipients=[client.email])
    msg.body  = "To reset your password, visit the following link: \n" + url_for('lawyer_reset_token',token=token, _external=True) +"\n if you did not make this request then simply ignore this email and no changes will be made."
    mail.send(msg)

# ask for email to reset password lawyer
@app.route('/client/reset-password',methods=['GET','POST'])
def client_reset_request():
    if session.get('client') is not None:
        return redirect(url_for('dashboard'))

    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'email' in req_data:
            email = req_data['email']
        if email:
            if is_email(email):
                client = Client.check_email(email)
                if client:
                    send_reset_email(client)
                    return json_response({
                        "error" : False,
                        "message" : "A password reset message was sent to your email. Please click the link in that message to reset your password."})
                else:
                    return json_response({
                        "error": True,
                        "message" : "Sorry, your email does not match our records."})
            else:
                return json_response({
                    "error" : True,
                    "message" : "You have entered an invalid email address, Please try again."})
        else:
            return json_response({
                "error" : True,
                "message" : "Please enter your email and try again."})
    return render_template('client/client-reset-pass.html',title="Reset")

# resetting password with new password lawyer
@app.route('/client/reset-password/<token>',methods=['GET','POST'])
def client_reset_token(token):
    if session.get('client') is not None:
        return redirect(url_for('dashboard'))
    client = Client.verify_reset_token(token)
    if client is None:
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
                    client = client.save(id=client.key.id(),password=password,status="activated")
                    if client:
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
                    "message" : "Please dont leave the fields empty and try again."})
        
    return render_template('client/client-reset-token.html',title="Reset Password",token=token)


# send email with token lawyer
def send_reset_email(lawyer):
    token = lawyer.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@case.com', recipients=[lawyer.email])
    msg.body  = "To reset your password, visit the following link: \n" + url_for('lawyer_reset_token',token=token, _external=True) +"\n if you did not make this request then simply ignore this email and no changes will be made."
    mail.send(msg)

# ask for email to reset password lawyer
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
                    return json_response({
                        "error" : False,
                        "message" : "A password reset message was sent to your email. Please click the link in that message to reset your password."})
                else:
                    return json_response({
                        "error": True,
                        "message" : "Sorry, your email does not match our records."})
            else:
                return json_response({
                    "error" : True,
                    "message" : "You have entered an invalid email address, Please try again."})
        else:
            return json_response({
                "error" : True,
                "message" : "Please enter your email and try again."})
    return render_template('lawyer/lawyer-reset-pass.html',title="Reset")

# resetting password with new password lawyer
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
                    "message" : "Please dont leave the fields empty and try again."})
        
    return render_template('lawyer/lawyer-reset-token.html',title="Reset Password",token=token)


# sign out route
@app.route('/lawyer/signout')
def lawyer_signout():
    del session['lawyer']
    return redirect(url_for('lawyer_signin'))


# sign out route
@app.route('/client/signout')
def client_signout():
    del session['client']
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
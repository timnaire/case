import logging
from flask import Flask, render_template, url_for, request, session, redirect, abort
from flask_mail import Mail, Message
from config import SECRET_KEY
import googlemaps
import json
import requests
from requests_toolbelt.adapters import appengine 
from models.lawyer import Lawyer
from models.client import Client
from models.practice import Practice
from models.case import Case
from models.event import Event
from models.relationship import Relationship
from models.notification import Notification
from models.upload_file import UploadFile
from models.payment import Payment
from models.feedback import Feedback
from models.subcategory import Subcategory
from models.subscription import Subscription
from models.pre_appoint import PreAppoint
from models.incoming_client import IncomingClient
from models.feature import Feature
from models.practice_list import PracticeList
from models.admin import Admin
from models.subpractice_list import SubPracticeList
from models.court import Court
from models.client_type import ClientType
from models.note import Note
from decorators import login_required_lawyer,login_required_client,login_required_admin
from functions import json_response, is_email, save_to_gcs
import pusher
from flask_moment import Moment
app = Flask(__name__)
moment = Moment(app)
appengine.monkeypatch()
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
app.config['FCM_APP_TOKEN'] = 'AAAApfmYrNw:APA91bFF6hkFopiyL_uvaZMX72KTYUG-5046imt9coP5JyEyw8Upj3x-4CFcbTiHsekqbBv6s4KS6QglLoO9iSb0ZqSUgNufiLzaGgw8h-2WDrt15_DNdCm0VH7kilevxDmxc2vD0BMc'
mail = Mail(app)
# Geocoding an address
# geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# pusher_client = pusher.Pusher(
#   app_id='777012',
#   key='86eb9d2db54de852df31',
#   secret='12fe5725a66c8463c2d5',
#   cluster='ap1',
#   ssl=True
# )

# pusher_client = pusher.Pusher(
#   app_id='785330',
#   key='468204a1ab0afbc0b5e0',
#   secret='c6e39bf35aefc89142c4',
#   cluster='ap1',
#   ssl=True
# )

pusher_client = pusher.Pusher(
  app_id='787910',
  key='609f784fb411565752ef',
  secret='03c8f1236b6df18d55a5',
  cluster='ap1',
  ssl=True
)

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
                # return render_template('home.html',title='Client',client=session['client'],law_practice=available_practice)
                return json_response({
                    "error" : False,
                    "message" : "Successfully signed in",
                    "client" : client.key.id(),
                    "first_name" : client.first_name,
                    "last_name" : client.last_name,
                    "email" : client.email,
                    "phone" : client.phone,
                    "sex" : client.sex,
                    "address" : client.address,
                    "profile_pic" : client.profile_pic})
            else:
                return json_response({
                    "error" : True,
                    "message" : "Credentials do not match, please try again."})
        else:
            return json_response({
                "error" : True,
                "message" : "Please check your email and password and try again."})

    if session.get('client') is not None:
        return redirect(url_for('dashboard_client'))

    return render_template('signin.html',title='Sign In')

@app.route('/client/<int:client_id>/account-setting/profile-picture', methods=['POST'])
@login_required_client
def client_update_picture(client_id=None):
    if request.method == "POST":
        f = request.files.get('image')
        if f and f.filename != '':
            profile_pic = save_to_gcs(f).get("serving_url")
            client = Client.save(id=client_id, profile_pic=profile_pic)
            if client:
                return json_response({
                    'error' : False,
                    'message' : "Profile picture has been saved!"})
            else:
                return json_response({
                    'error' : True,
                    'message' : "Profile picture was not saved!"})
    
@app.route('/client/<int:client_id>/myaccount',methods=['GET','POST'])
@login_required_client
def client_account_setting(client_id=None):
    # get the lawyer details in a dictionary format
    global available_practice
    if client_id:
        client_dict = Client.get_by_id(int(client_id))
        if client_dict:
            client_dict = client_dict.to_dict()
        else:
            abort(404)
    client = Client.get_by_id(int(client_id))

    return render_template("account.html",title="Account Setting",client=session.get('client'),client_info=client_dict)
 

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
        if 'sex' in req_data:
            sex = req_data['sex']
        if 'phone' in req_data:
            phone = req_data['phone']
        if 'address' in req_data:
            address = req_data['address']
        if 'password' in req_data:
            password = req_data['password']
        if 'confirm' in req_data:
            confirm = req_data['confirm']
        
        if first_name and last_name and email and sex and phone and address and password:
            if is_email(email=email):
                client = Client.check_email(email)
                if not client:
                    if password == confirm:
                        client = Client.save(first_name=first_name,last_name=last_name,email=email,sex=sex,phone=phone,address=address,password=password)
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
        
    return render_template('signup.html',title="Client Sign up")

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
        if 'sex' in req_data:
            sex = req_data['sex']

        if first_name and last_name and sex and phone and address:
            client = Client.save(id=client_id,first_name=first_name,last_name=last_name,phone=phone,address=address,sex=sex)
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


# available_practice = {'Constitutional Law':"Constitutional Law", 'Criminal Law': 'Criminal Law', 'Business Law': 'Business Law',
#         'Labor Law': 'Labor Law', 'Civil Law' : 'Civil Law', 'Taxation Law': 'Taxation Law' ,'Family Law': 'Family Law'}
available_practice = PracticeList.list_of_practices()
# subcategory = { 'Family Law' : {'Adoptions','Child Custody and Visitation','Child Support','Annulment','Guardianship','Paternity','Separations','Spousal Support or Alimony'},
#                 'Labor Law' : {'Disabilities','Employment Contracts','Employment Discrimination','Pensions and Benefits','Sexual Harassment','Wages and Overtime Pay','Workplace','Wrongful Termination'},
#                 'Criminal Law' : {'Drug Crimes','Drunk Driving / DUI / DWI','Felonies','Misdemeanors','Speeding and Moving Violations'},
#                 'Business Law' : {'Breach of Contract','Business Disputes','Buying and Selling a Business','Contract Drafting and Review','Corps, LLCs, Partnerships, etc.','Entertainment Law'},
#                 'Constitutional Law' : {'Free Speech and Press','Libel and Slander','Right to Bear Arms'},
#                 'Taxation Law': {'Corporate Tax','Income Tax','Internation Tax','Property Tax','Tax Evasion'},
#                 'Civil Law' : {'Defamtion','Breach of Contract','Negligence Resulting in Injury or Death','Property Damage'}
# } 
subcategory = SubPracticeList.list_of_subpractices()

@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'option' in req_data:
            option = req_data['option']

        if option == "add":
            if 'username' in req_data:
                username = req_data['username']
            if 'password' in req_data:
                password = req_data['password']
            if 'confirm' in req_data:
                confirm = req_data['confirm']

            if password == confirm:
                admin = Admin.save(username=username,password=password)
                if admin:
                    return json_response({
                        "error" : False,
                        "message" : "Successfully added new admin."
                    })
                else:
                    return json_response({
                        "error" : True,
                        "message" : "Failed to add new admin."
                    })
        elif option == "login":
            if 'username' in req_data:
                username = req_data['username']
            if 'password' in req_data:
                password = req_data['password']

            if username and password:
                admin = Admin.sign_in(username=username,password=password)
                session['admin'] = admin.key.id()
                if admin:
                    return json_response({
                        "error" : False,
                        "message" : "Successfully signed in."
                    })
                else:
                    return json_response({
                        "error" : True,
                        "message" : "Failed to signed in."
                    })
            
    return render_template("admin.html")

@app.route("/admin-dashboard",methods=['GET','POST'])
@login_required_admin
def admin_dashboard():
    admin_id = session['admin']
    admin = Admin.get_by_id(int(admin_id))

    return render_template("admin-dashboard.html",username=admin.username)

@app.route("/admin-practices",methods=['GET','POST'])
@login_required_admin
def admin_practice():
    admin_id = session['admin']
    admin = Admin.get_by_id(int(admin_id))

    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'practice' in req_data:
            practice = req_data['practice']

        practice = PracticeList.save(practice=practice)
        if practice:
            return json_response({
                "error" : False,
                "message" : "Successfully added new law practice."
            })
        else:
            return json_response({
                "error" : True,
                "message" : "Failed to add law practice."
            })

    return render_template("admin-lawpractice.html",username=admin.username, available_practice=available_practice)

@app.route("/admin-subpractices",methods=['GET','POST'])
@login_required_admin
def admin_subpractice():
    admin_id = session['admin']
    admin = Admin.get_by_id(int(admin_id))
    list_of_subpractices = SubPracticeList.list_of_subpractices()

    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'practice' in req_data:
            practice = req_data['practice']
        if 'subpractice' in req_data:
            subpractice = req_data['subpractice']
     
        if practice:
            if subpractice:
                law_practice = PracticeList.query(PracticeList.law_practice == practice).get()
                sb = SubPracticeList.save(practice=law_practice.key.id(),spractice=subpractice)
                if sb:
                    return json_response({
                        "error" : False,
                        "message" : "Successfully added new sub practice."
                    })
                else:
                    return json_response({
                        "error" : True,
                        "message" : "Failed to add sub practice."
                    })
            else:
                return json_response({
                        "error" : True,
                        "message" : "Please enter the name of sub practice."
                    })
        else:
            return json_response({
                    "error" : True,
                    "message" : "Please select a Law Practice."
                })
    return render_template("admin-subpractice.html",subpractices=list_of_subpractices,username=admin.username, available_practice=available_practice)

@app.route("/admin-client-type",methods=['GET','POST'])
@login_required_admin
def admin_client_type():
    admin_id = session['admin']
    admin = Admin.get_by_id(int(admin_id))
    list_of_cts = ClientType.list_of_cts()

    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'client_type' in req_data:
            client_type = req_data['client_type']

        client_type = ClientType.save(client_type=client_type)
        if client_type:
            return json_response({
                "error" : False,
                "message" : "Successfully added new client type."
            })
        else:
            return json_response({
                "error" : True,
                "message" : "Failed to add client type."
            })
    return render_template("admin-client-type.html",client_type=list_of_cts,username=admin.username)

@app.route("/admin-court",methods=['GET','POST'])
@login_required_admin
def admin_court():
    admin_id = session['admin']
    admin = Admin.get_by_id(int(admin_id))
    list_of_courts = Court.list_of_courts()

    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'court' in req_data:
            court = req_data['court']

        court = Court.save(court=court)
        if court:
            return json_response({
                "error" : False,
                "message" : "Successfully added new court."
            })
        else:
            return json_response({
                "error" : True,
                "message" : "Failed to add court."
            })
    return render_template("admin-court.html",courts=list_of_courts,username=admin.username)

@app.route("/admin-signout",methods=['GET','POST'])
def admin_signout():
    if session.get('admin') is not None:
        del session['admin']
        return redirect(url_for('admin'))

# home page for client
@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    # del session['client']
    available_practice = PracticeList.list_of_practices()
    if session.get('lawyer') is not None:
        lawyer = Lawyer.get_by_id(int(session['lawyer']))
        return render_template('home.html',title='Home',lawyer=session['lawyer'],law_practice=available_practice,lawyer_first=lawyer.first_name)
    elif session.get('client'):
        client = Client.get_by_id(int(session['client']))
        return render_template('home.html',title='Home',law_practice=available_practice,client=session['client'],client_first=client.first_name)    
    else:
        return render_template('home.html',title='Home',law_practice=available_practice)

#####################################################################################################################################
# for lawyers and below

@app.route('/lawyer/<int:client_id>/pre-appoint',methods=['POST'])
def lawyer_clicked(client_id=None):
    if request.method == "POST":
        lawyer_id=None
        req_data = request.get_json(force=True)
        if 'id' in req_data:
            lawyer_id = req_data['id']

        lawyer = Lawyer.get_by_id(int(lawyer_id))
        client = Client.get_by_id(int(client_id))

        preappoint = PreAppoint.isAppointed(client=client_id,lawyer=lawyer_id)

        if not preappoint:
            preappoint = PreAppoint.save(lawyer=lawyer_id,client=client_id,status="")
            json_data = {
                "to": lawyer.fcm_token,     
                "notification":{
                    'click_action' : '.MainActivity',
                    'title': 'Pre-Appointment', 
                    'body': client.first_name + ' ' + client.last_name + ' sends Pre-Appointment request.'
                },
                "data":{
                    'client_id': client_id,
                    'preappoint_id' : preappoint.key.id()
                }
            }

            headers = {'content-type': 'application/json', "Authorization": "key="+app.config['FCM_APP_TOKEN']}
            requests.post(
                'https://fcm.googleapis.com/fcm/send', headers=headers, data=json.dumps(json_data)
            )
            pusher_client.trigger('appointment', 'preappoint', {'lawyer' : lawyer.key.id() ,'message': client.first_name + ' ' + client.last_name + ' sends Pre-Appointment request.'})
            return json_response({
                "error" : False,
                "message" : "Pre-appointment Request has been sent!"
            })
        else:
            return json_response({
                "error" : True,
                "message" : "You already sent a pre appointment!"
            })

@app.route('/lawyer/<int:lawyer_id>/preappointments',methods=['GET','POST'])
def lawyer_preappointments(lawyer_id=None):
    preappoints = PreAppoint.allPreAppointmentApi(lawyer=lawyer_id)

    preappoint_dict = []
    if preappoints:
        for preappoint in preappoints:
            preappoint_dict.append(preappoint.to_dict())
        
    return json_response({
        "error" : False,
        "preappoints" : preappoint_dict,
        "message" : "You have "+`len(preappoint_dict)`+" pre appointment(s)"
    })

@app.route('/lawyer/<int:lawyer_id>/incoming-clients',methods=['GET','POST'])
def lawyer_incomingclients(lawyer_id=None):
    preappoints = PreAppoint.allPendingClientApi(lawyer=lawyer_id)

    preappoint_dict = []
    if preappoints:
        for preappoint in preappoints:
            preappoint_dict.append(preappoint.to_dict())
        
    return json_response({
        "error" : False,
        "preappoints" : preappoint_dict,
        "message" : "You have "+`len(preappoint_dict)`+" pending client(s)"
    })

@app.route('/lawyer/<int:client_id>/pre-appoint-response',methods=['POST'])
def pre_accepted(client_id=None):
    client = Client.get_by_id(int(client_id)) 
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'lawyer_id' in req_data:
            lawyer_id = req_data['lawyer_id']
        if 'status' in req_data:
            status = req_data['status']

        preappoint = PreAppoint.isAppointed(lawyer=lawyer_id,client=client_id)

        if preappoint:
            preappoint_id = preappoint.key.id()
            PreAppoint.save(id=preappoint_id,lawyer=lawyer_id,client=client_id,status=status)
            lawyer = Lawyer.get_by_id(int(lawyer_id))
            json_data = {
                "to": client.fcm_token,
                "notification":{
                    'click_action' : '.MainActivity',
                    'title': 'Pre-Appointment', 
                    'body': lawyer.first_name + ' ' + lawyer.last_name + ' accepted your Pre-Appointment request.'
                },
                "data":{
                    'lawyer_id': lawyer.key.id(),
                    'preappoint_id' : preappoint.key.id()
                }
            }
            headers = {'content-type': 'application/json', "Authorization": "key="+app.config['FCM_APP_TOKEN']}
            requests.post(
                'https://fcm.googleapis.com/fcm/send', headers=headers, data=json.dumps(json_data)
            )
            if status == "accept":
                preappoints = PreAppoint.query(PreAppoint.client == client.key, PreAppoint.status == None).fetch()
                for p in preappoints:
                    p.key.delete()
                pusher_client.trigger('appointment', 'accepted', { 'first_name': client.first_name, 'last_name': client.last_name , 'lawyer': lawyer_id , 'client' : client_id , 'message': lawyer.first_name+" "+ lawyer.last_name + " accepted your pre appointment request."})
                return json_response({
                    "error" : False,
                    'id' : lawyer_id,
                    "message" : "You accepted "+client.first_name+" "+client.last_name+" pre appointment request."
                })
            else:
                pusher_client.trigger('appointment', 'decline', { 'client' : client_id , 'message': lawyer.first_name+" "+ lawyer.last_name + " declined your pre appointment request."})
                return json_response({
                    "error" : False,
                    'id' : lawyer_id,
                    "message" : "You decline "+client.first_name+" "+client.last_name+" pre appointment request."
                })
        else:
            return json_response({
                "error" : True,
                "message" : "You declined "+client.first_name+" "+client.last_name+" pre appointment request."
            })

@app.route('/lawyer/<int:lawyer_id>/incoming-client',methods=['GET','POST'])
def lawyer_incoming_client(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'status' in req_data:
            status = req_data['status']
        if 'client_id' in req_data:
            client_id = req_data['client_id']
        if 'preappoint_id' in req_data:
            preappoint_id = req_data['preappoint_id']    
        lawyer = Lawyer.get_by_id(int(lawyer_id))
        client = Client.get_by_id(int(client_id))
        preappoint = PreAppoint.save(id=preappoint_id,status=status)
        title = None
        if lawyer.sex == "Male":
            title = "his"
        elif lawyer.sex == "Female":
            title = "her"
        
        if preappoint:
            if status == "client":
                json_data = {
                    "to": client.fcm_token,     
                    "notification":{
                        'click_action' : '.MainActivity',
                        'title': 'You are now a client', 
                        'body': lawyer.first_name + ' ' + lawyer.last_name + ' makes you '+title+" client"
                    },
                    "data":{
                        'lawyer_id': lawyer.key.id(),
                        'preappoint' : preappoint.key.id()
                    }
                }
                pusher_client.trigger('client', 'accepted', { 'client' : client_id , 'message': lawyer.first_name+" "+ lawyer.last_name + " makes you "+title+" client"})
                headers = {'content-type': 'application/json', "Authorization": "key="+app.config['FCM_APP_TOKEN']}
                requests.post(
                    'https://fcm.googleapis.com/fcm/send', headers=headers, data=json.dumps(json_data)
                )
                return json_response({
                    "error" : False,
                    "message" : "Great! You have made a new client!"
                })
            elif status == "decline":
                json_data = {
                    "to": client.fcm_token,     
                    "notification":{
                        'click_action' : '.MainActivity',
                        'title': 'Case', 
                        'body': lawyer.first_name + ' ' + lawyer.last_name + ' declined you as '+title+" client"
                    },
                    "data":{
                        'lawyer_id': lawyer.key.id(),
                        'preappoint' : preappoint.key.id()
                    }
                }
                pusher_client.trigger('client', 'decline', { 'client' : client_id , 'message': lawyer.first_name+" "+ lawyer.last_name + " declined you as "+title+" client"})
                headers = {'content-type': 'application/json', "Authorization": "key="+app.config['FCM_APP_TOKEN']}
                requests.post(
                    'https://fcm.googleapis.com/fcm/send', headers=headers, data=json.dumps(json_data)
                )
                return json_response({
                    "error" : False,
                    "message" : "You have declined a client!"
                })
        else:
            return json_response({
                "error" : True,
                "message" : "Something went wrong please"
            })


# auto notify lawyer to unresponded client pre appointment request
@app.route('/lawyer/<int:lawyer_id>/pre-appoint-notification',methods=['GET','POST'])
def number_of_case(lawyer_id=None):
    lawyer = Lawyer.get_by_id(int(lawyer_id))
    relations = Relationship.query(Relationship.lawyer==lawyer.key, Relationship.status == None).fetch()
    # loops through lawyers in relationship with client who didn't response to the pre-appointment and create a script that will auto
    # sends notification again when the lawyer launch the mobile app.
    if relations:
        for r in relations:
            client_key = r.client
            lawyer_key = r.lawyer
            relation_id = r.key.id()

            lawyer = lawyer_key.get()
            client = client_key.get()
            relation_id = r.key.id() 

            json_data = {
                "to": lawyer.fcm_token,     
                "notification":{
                    'click_action' : '.MainActivity',
                    'title': 'Pre-Appointment', 
                    'body': client.first_name + ' ' + client.last_name + ' sends Pre-Appointment request.'
                },
                "data":{
                    'client_id': client.key.id(),
                    'relation_id' : relation_id
                }
            }

            headers = {'content-type': 'application/json', "Authorization": "key="+app.config['FCM_APP_TOKEN']}
            requests.post(
                'https://fcm.googleapis.com/fcm/send', headers=headers, data=json.dumps(json_data)
            )
        return json_response({
            "error" : False,
            "message" : "New notifications"})
    else:
        return json_response({
            "error": True,
            "message" : "No notification"})
    
# find a lawyer route
@app.route('/lawyers',methods=['GET','POST'])
# @app.route('/lawyers?lawpractice=<string:lawpractice>',methods=['GET','POST'])
def find_lawyer(practice=None,cityOrMunicipality=None):
    lawyers = None
    found_lawyers = []
    subcategory = SubPracticeList.list_of_subpractices()
    if request.method == "POST":        

        law_practice = request.form.get('lawpractice')
        cityOrMunicipality = request.form.get('city')
        if law_practice and cityOrMunicipality:
            found_lawyers = Practice.find_practice(law_practice=law_practice, cityOrMunicipality=cityOrMunicipality)
            if found_lawyers:
                lawyers = found_lawyers
                if session.get('lawyer'):
                    return redirect(url_for('find_lawyer',practice=law_practice,cityOrMunicipality=cityOrMunicipality))
                    # return render_template('lawyers.html',title='Lawyers',law_practice=available_practice,results=lawyers,lawyer=session['lawyer'])
                elif session.get('client'):
                    return redirect(url_for('find_lawyer',practice=law_practice,cityOrMunicipality=cityOrMunicipality))
                    # return render_template('lawyers.html',title='Lawyers',law_practice=available_practice,results=lawyers,client=session['client'])
                else:
                    return redirect(url_for('find_lawyer',practice=law_practice,cityOrMunicipality=cityOrMunicipality))
                    # return render_template('lawyers.html',title='Lawyers',law_practice=available_practice,results=lawyers,lawpractice=law_practice)
                # return json_response({"found" : found_lawyers})
            else:
                return redirect(url_for('find_lawyer',practice=law_practice,cityOrMunicipality=cityOrMunicipality))
        else:
            return redirect(url_for('dashboard_client',practice=law_practice,cityOrMunicipality=cityOrMunicipality,msg="Please select your legal issue and city to find lawyer."))
            # return redirect(json_response({
            #     'error' : True,
            #     'message' : "Please select your legal issue and city to find lawyer."}))
    

    law_practice = request.args.get('practice')
    cityOrMunicipality = request.args.get('cityOrMunicipality')

    if law_practice and cityOrMunicipality:
        found_lawyers = Practice.find_practice(law_practice=law_practice, cityOrMunicipality=cityOrMunicipality)
        if found_lawyers:
            lawyers = found_lawyers
        else:
            lawyers = None
    else:
        attorneys = Lawyer.query(Lawyer.status == "activated").fetch()
        lawyers = Practice.all_lawyers(attorneys)
    
    if session.get('lawyer'):
        return render_template('lawyers.html',title='Lawyers',law_practice=available_practice,results=lawyers,lawyer=session['lawyer'],subcategory=subcategory)
    elif session.get('client'):
        return render_template('lawyers.html',title='Lawyers',law_practice=available_practice,results=lawyers,client=session['client'],subcategory=subcategory)
    else:
        return render_template('lawyers.html',title='Lawyers',law_practice=available_practice,results=lawyers,subcategory=subcategory)
        
#dashboard route for lawyers
@app.route('/lawyer/<int:lawyer_id>/dashboard')
@login_required_lawyer
def dashboard(lawyer_id=None):

    preappoints = PreAppoint.allPreAppointment(lawyer=lawyer_id)
    preappoint_dict = []
    if preappoints:
        for preappoint in preappoints:
            preappoint_dict.append(preappoint.to_dict())
        
    list_of_clients = PreAppoint.accept_client(lawyer_id=lawyer_id)
    list_of_courts = Court.list_of_courts()
    list_of_cts = ClientType.list_of_cts()

    lawyer_id = Lawyer.get_by_id(int(lawyer_id))
    lawyer = lawyer_id.to_dict()
    return render_template('lawyer-dashboard.html',title="Welcome to Dashboard",client_type=list_of_cts,courts=list_of_courts,clients=list_of_clients,lawyer=session['lawyer'],results=lawyer,preappointments=preappoint_dict)

#dashboard route for client
@app.route('/client/')
@app.route('/client/dashboard')
@login_required_client
def dashboard_client():
    client = Client.get_by_id(int(session['client']))
    return render_template('home.html',title="Home",client_first=client.first_name,client=session['client'],law_practice=available_practice)

# route for lawyer add file
@app.route('/lawyer/view-case',methods=['GET','POST'])
def viewCase(lawyer_id=None,client_id=None):
        
    client_id = request.args.get('client_id')
    case_id = request.args.get('case_id')
    lawyer_id = request.args.get('lawyer_id')

    case = Case.get_by_id(int(case_id))
    case_dict = []
    if case:
        case_dict.append(case.to_dict())

    if session.get('client') is not None:
        client = Client.get_by_id(int(client_id))
        events = Event.query(Event.client == client.key).fetch()
        event_dict = []
        for event in events:
            event_dict.append(event.to_dict())
        return render_template('case/lawyer-viewCase.html',title="View Case", case_id=case_id,event=event_dict, case= case_dict,client=session['client'])
    
    elif session.get('lawyer'):
        lawyer = Lawyer.get_by_id(int(lawyer_id))
        events = Event.query(Event.lawyer == lawyer.key).fetch()
        event_dict = []
        for event in events:
            event_dict.append(event.to_dict())
        return render_template('case/lawyer-viewCase.html',title="View Case", case_id=case_id,event=event_dict, case= case_dict,lawyer=session['lawyer'])
    else:
        return json_response({
                "error" : True,
                "message" : "Not Signed in"})

# route for lawyer add file web
@app.route('/lawyer/<int:lawyer_id>/add-file-web',methods=['GET','POST'])
def lawyer_add_file_web(lawyer_id=None):
    if request.method == "POST":
        uploaded_by = request.form.get("uploaded_by")
        case = request.form.get("case")
        file_name = request.form.get("file_name")
        file_privacy = request.form.get("file_privacy")

        if file_privacy == "Public":
            file_type = "Public Document"
        elif file_privacy == "Private":
            file_type = "Research"

        for i in range(5):
            case_file = request.files.get("file["+str(i)+"]")
            logging.debug(case_file)
            if case_file and case_file.filename != '':
                case_file_s = save_to_gcs(case_file).get("serving_url")

                identity = Lawyer.get_by_id(int(uploaded_by))
        
                if case and case_file and file_privacy and file_type:
                    upload = UploadFile.save(case=case,case_file=case_file_s,file_name=file_name,file_privacy=file_privacy,file_type=file_type,uploaded_by=identity.key)
                    if upload:
                        return json_response({
                            "error" : False,
                            "message" : "File uploaded !"})
                    else:
                        return json_response({
                            "error" : True,
                            "message" : "Failed upload, please try again."
                        })

# route for client add file 
@app.route('/client/<int:client_id>/add-file-web',methods=['GET','POST'])
def client_add_file_web(client_id=None):
    if request.method == "POST":
        uploaded_by = request.form.get("uploaded_by")
        case = request.form.get("case")
        file_name = request.form.get("file_name")
        file_privacy = request.form.get("file_privacy")

        if file_privacy == "Public":
            file_type = "Public Document"
        elif file_privacy == "Private":
            file_type = "Research"

        for i in range(5):
            case_file = request.files.get("file["+str(i)+"]")
            logging.debug(case_file)
            if case_file and case_file.filename != '':
                case_file_s = save_to_gcs(case_file).get("serving_url")

                identity = Client.get_by_id(int(uploaded_by))
        
                if case and case_file and file_privacy and file_type:
                    upload = UploadFile.save(case=case,case_file=case_file_s,file_name=file_name,file_privacy=file_privacy,file_type=file_type,uploaded_by=identity.key)
                    if upload:
                        return json_response({
                            "error" : False,
                            "message" : "File uploaded !"})

        return json_response({
            "error" : False,
            "message" : "Successfully uploaded"
        })

# route for lawyer add file
@app.route('/lawyer/<int:lawyer_id>/add-file',methods=['GET','POST'])
def add_file(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if "case" in req_data:
            case = req_data['case']
        if "file_name" in req_data:
            file_name = req_data["file_name"]
        if "case_file" in req_data:
            case_file = req_data['case_file']
        if "file_privacy" in req_data:
            file_privacy = req_data["file_privacy"]
        if "uploaded_by" in req_data:
            uploaded_by = req_data['uploaded_by']
        
        if file_privacy == "Public":
            file_type = "Public Document"
        elif file_privacy == "Private":
            file_type = "Research"

        identity = Lawyer.get_by_id(int(uploaded_by))
        
        if case and case_file and file_privacy and file_type:
            upload = UploadFile.save(case=case,case_file=case_file,file_name=file_name,file_privacy=file_privacy,file_type=file_type,uploaded_by=identity.key)
            if upload:
                return json_response({
                    "error" : False,
                    "message" : "File uploaded !"})
        else:
            return json_response({
                "error" : True,
                "message" : "Please fill up all the fields and try again."})

# route for client add file
@app.route('/client/<int:client_id>/add-file',methods=['GET','POST'])
def add_file_client(client_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if "case" in req_data:
            case = req_data['case']
        if "file_name" in req_data:
            file_name = req_data["file_name"]
        if "case_file" in req_data:
            case_file = req_data['case_file']
        if "file_privacy" in req_data:
            file_privacy = req_data["file_privacy"]
        if "uploaded_by" in req_data:
            uploaded_by = req_data['uploaded_by']
        
        if file_privacy == "Public":
            file_type = "Public Document"
        elif file_privacy == "Private":
            file_type = "Research"

        identity = Client.get_by_id(int(uploaded_by))
        
        if case and case_file and file_privacy and file_type:
            upload = UploadFile.save(case=case,case_file=case_file,file_name=file_name,file_privacy=file_privacy,file_type=file_type,uploaded_by=identity.key)
            if upload:
                return json_response({
                    "error" : False,
                    "message" : "File uploaded !"})
        else:
            return json_response({
                "error" : True,
                "message" : "Please fill up all the fields and try again."})

# route for lawyer api deleting file
@app.route('/delete-file',methods=["GET","POST"])
def delete_file_lawyer():
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if "file_id" in req_data:
            file_id = req_data['file_id']
        
        f = UploadFile.get_by_id(int(file_id))
        if f:
            f.key.delete()
            return json_response({
                "error" : False,
                "message" : "File deleted!"})
        else:
            return json_response({
                "error" : True,
                "message" : "File was not deleted"})

# route for client api deleting file
@app.route('/client/delete-file',methods=["GET","POST"])
def delete_file_client():
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if "file_id" in req_data:
            file_id = req_data['file_id']
        if "uploaded_by" in req_data:
            uploaded_by = req_data['uploaded_by']

        client = Client.get_by_id(int(uploaded_by))
        if client:
            f = UploadFile.get_by_id(int(file_id))
            if f:
                f.key.delete()
                return json_response({
                    "error" : False,
                    "message" : "File deleted!"})
            else:
                return json_response({
                    "error" : True,
                    "message" : "File was not deleted"}) 
        else:
            return json_response({
                "error": True,
                "message": "Unauthorized, You cant delete this file."})

# route for client api deleting file
@app.route('/client/delete-file-web',methods=["GET","POST"])
def webdelete_file_client():
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if "file_id" in req_data:
            file_id = req_data['file_id']
        if "client_id" in req_data:
            client_id = req_data['client_id']

        
        if client_id:
            for f in file_id:
                deleted = UploadFile.deleteFilesClient(f=f,client_id=client_id);

            if deleted:
                return json_response({
                "error" : False,
                "message" : "File deleted!"})
            else:
                    return json_response({
                "error" : True,
                "message" : "Unauthorized, You cant delete this file."})

# route for client api deleting file
@app.route('/lawyer/delete-file-web',methods=["GET","POST"])
def webdelete_file_lawyer():
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if "file_id" in req_data:
            file_id = req_data['file_id']
        if "lawyer_id" in req_data:
            lawyer_id = req_data['lawyer_id']

        
        if lawyer_id:
            for f in file_id:
                deleted = UploadFile.deleteFilesLawyer(f=f,lawyer_id=lawyer_id)

            if deleted:
                return json_response({
                "error" : False,
                "message" : "File deleted!"})
            else:
                    return json_response({
                "error" : True,
                "message" : "Unauthorized, You cant delete this file."})

# route for lawyer api getting all documents
@app.route('/lawyer/<int:lawyer_id>/list-all-file',methods=["GET","POST"])
def list_all_file(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if "case" in req_data:
            case = req_data['case']
        
        files = UploadFile.get_all_files(case=case)
        if files:
            return json_response({
                "error" : False,
                "message" : `len(files)` + " files",
                "list_files" : files})
        else:
            return json_response({
                "error" : True,
                "message" : "No files"})

# route for lawyer api getting the research documents
@app.route('/lawyer/<int:lawyer_id>/list-research',methods=["POST"])
def reserach_documents(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if "case" in req_data:
            case = req_data['case']
        
        files = UploadFile.get_research(case=case)
        if files:
            return json_response({
                "error" : False,
                "message" : `len(files)` + " files",
                "list_files" : files})
        else:
            return json_response({
                "error" : True,
                "message" : "No files"})

# route for lawyer api getting the public documents
@app.route('/lawyer/<int:lawyer_id>/list-public-documents',methods=["POST"])
def public_documents(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if "case" in req_data:
            case = req_data['case']
        
        files = UploadFile.get_public_docs(case=case)
        if files:
            return json_response({
                "error" : False,
                "message" : `len(files)` + " files",
                "list_files" : files})
        else:
            return json_response({
                "error" : True,
                "message" : "No files"})

# route for client api getting the public documents
@app.route('/client/<int:client_id>/list-public-documents',methods=["POST"])
def public_documents_clients(client_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if "case" in req_data:
            case = req_data['case']
        
        files = UploadFile.get_public_docs(case=case)
        if files:
            return json_response({
                "error" : False,
                "message" : `len(files)` + " files",
                "list_files" : files})
        else:
            return json_response({
                "error" : True,
                "message" : "No files"})

# route for client event create
@app.route('/client/<int:client_id>/add-event',methods=['GET','POST'])
def add_event_client(client_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'lawyer_id' in req_data:
            lawyer_id = req_data['lawyer_id']
        if 'event_title' in req_data:
            event_title = req_data['event_title']
        if 'event_location' in req_data:
            event_location = req_data['event_location']
        if 'event_details' in req_data:
            event_details = req_data['event_details']
        if 'event_date' in req_data:
            event_date = req_data['event_date']
        if 'event_time' in req_data:
            event_time = req_data['event_time'] 
        if 'event_type' in req_data:
            event_type = req_data['event_type']
        if 'event_owner' in req_data:
            event_owner = req_data['event_owner']

        event_owner = Client.get_by_id(int(event_owner))

        if client_id and event_title and event_location and event_details and event_date and event_time and event_type:
            event = Event.save(lawyer=lawyer_id, client=client_id,event_title=event_title,event_location=event_location,event_details=event_details,event_date=event_date,event_time=event_time,event_type=event_type,event_owner=event_owner.key)
            client = Client.get_by_id(int(client_id))
            lawyer = Lawyer.get_by_id(int(lawyer_id))
            # sends mobile notification to the client if the lawyer creates an event 
            json_data = {
                "to": lawyer.fcm_token,     
                "notification":{
                    'click_action' : '.MainActivity',
                    'title': event_title, 
                    'body': event_details
                },
                "data":{
                    'client_id': client.key.id()
                }
            }
            headers = {'content-type': 'application/json', "Authorization": "key="+app.config['FCM_APP_TOKEN']}
            requests.post(
                'https://fcm.googleapis.com/fcm/send', headers=headers, data=json.dumps(json_data)
            )
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

# route for lawyer event create
@app.route('/lawyer/<int:lawyer_id>/add-event',methods=['GET','POST'])
def add_event_lawyer(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'client_id' in req_data:
            client_id = req_data['client_id']
        if 'event_title' in req_data:
            event_title = req_data['event_title']
        if 'event_location' in req_data:
            event_location = req_data['event_location']
        if 'event_details' in req_data:
            event_details = req_data['event_details']
        if 'event_date' in req_data:
            event_date = req_data['event_date']
        if 'event_time' in req_data:
            event_time = req_data['event_time'] 
        if 'event_type' in req_data:
            event_type = req_data['event_type']
        if 'event_owner' in req_data:
            event_owner = req_data['event_owner']

        event_owner = Lawyer.get_by_id(int(event_owner))

        if client_id and event_title and event_location and event_details and event_date and event_time and event_type:
            event = Event.save(lawyer=lawyer_id, client=client_id,event_title=event_title,event_location=event_location,event_details=event_details,event_date=event_date,event_time=event_time,event_type=event_type,event_owner=event_owner.key)
            client = Client.get_by_id(int(client_id))
            lawyer = Lawyer.get_by_id(int(lawyer_id))
            # sends mobile notification to the client if the lawyer creates an event 
            json_data = {
                "to": client.fcm_token,     
                "notification":{
                    'click_action' : '.MainActivity',
                    'title': event_title, 
                    'body': event_details
                },
                "data":{
                    'lawyer_id': lawyer.key.id()
                }
            }
            headers = {'content-type': 'application/json', "Authorization": "key="+app.config['FCM_APP_TOKEN']}
            requests.post(
                'https://fcm.googleapis.com/fcm/send', headers=headers, data=json.dumps(json_data)
            )
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

# route for client event update
@app.route('/client/<int:client_id>/update-event',methods=['GET','POST'])
def update_event_client(client_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'event_id' in req_data:
            event_id = req_data['event_id']
        if 'lawyer_id' in req_data:
            lawyer_id = req_data['lawyer_id']
        if 'event_title' in req_data:
            event_title = req_data['event_title']
        if 'event_location' in req_data:
            event_location = req_data['event_location']
        if 'event_details' in req_data:
            event_details = req_data['event_details']
        if 'event_date' in req_data:
            event_date = req_data['event_date']
        if 'event_time' in req_data:
            event_time = req_data['event_time'] 
        if 'event_type' in req_data:
            event_type = req_data['event_type']
        if 'event_owner' in req_data:
            event_owner = req_data['event_owner']

        event_owner = Client.get_by_id(int(event_owner))

        if client_id and event_title and event_location and event_details and event_date and event_time and event_type:
            event = Event.save(id=event_id,lawyer=lawyer_id, client=client_id,event_title=event_title,event_location=event_location,event_details=event_details,event_date=event_date,event_time=event_time,event_type=event_type,event_owner=event_owner.key)
            client = Client.get_by_id(int(client_id))
            lawyer = Lawyer.get_by_id(int(lawyer_id))
            # sends mobile notification to the client if the lawyer creates an event 
            if event:
                return json_response({
                    "error" : False,
                    "message" : "Event updated !"})
            else:
                return json_response({
                    "error" : True,
                    "message" : "Couldn't update event, please try again."})
        else:
            return json_response({
                "error" : True,
                "message" : "Please fill up all the fields and try again."})

# route for lawyer event update
@app.route('/lawyer/<int:lawyer_id>/update-event',methods=['GET','POST'])
def update_event_lawyer(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'event_id' in req_data:
            event_id = req_data['event_id']
        if 'client_id' in req_data:
            client_id = req_data['client_id']
        if 'event_title' in req_data:
            event_title = req_data['event_title']
        if 'event_location' in req_data:
            event_location = req_data['event_location']
        if 'event_details' in req_data:
            event_details = req_data['event_details']
        if 'event_date' in req_data:
            event_date = req_data['event_date']
        if 'event_time' in req_data:
            event_time = req_data['event_time'] 
        if 'event_type' in req_data:
            event_type = req_data['event_type']
        if 'event_owner' in req_data:
            event_owner = req_data['event_owner']

        event_owner = Lawyer.get_by_id(int(event_owner))

        if client_id and event_title and event_location and event_details and event_date and event_time and event_type:
            event = Event.save(id=event_id,lawyer=lawyer_id, client=client_id,event_title=event_title,event_location=event_location,event_details=event_details,event_date=event_date,event_time=event_time,event_type=event_type,event_owner=event_owner.key)
            client = Client.get_by_id(int(client_id))
            lawyer = Lawyer.get_by_id(int(lawyer_id))
            # sends mobile notification to the client if the lawyer creates an event 
            if event:
                return json_response({
                    "error" : False,
                    "message" : "Event updated !"})
            else:
                return json_response({
                    "error" : True,
                    "message" : "Couldn't update event, please try again."})
        else:
            return json_response({
                "error" : True,
                "message" : "Please fill up all the fields and try again."})

# route for lawyer event update
@app.route('/edit-event',methods=['GET','POST'])
def edit_event():
    if request.method == "POST":
        req_data = request.get_by_id(force=True)
        if "event_id" in req_data:
            event_id = req_data
        if "event_owner" in req_data:
            event_owner = req_data
        event = Event.query(Event.key.id == event_id, Event.event_owner == event_owner).get()
        if event:
            return json_response({
                "error" : False,
                "event_title" : event.event_title,
                "event_location" : event.event_location,
                "event_details" : event.event_details,
                "event_date" : event.event_date,
                "event_time" : event.event_time,
                "event_type" : event.event_type})
        else:
            return json_response({
                "error" : True,
                "message" : "Event was not updated."})

@app.route('/lawyer/<int:lawyer_id>/clients',methods=['GET','POST'])
@login_required_lawyer
def list_client_web(lawyer_id=None):
    list_of_clients = PreAppoint.my_clients(lawyer_id=lawyer_id)
    lawyer_id = Lawyer.get_by_id(int(lawyer_id))
    lawyer = lawyer_id.to_dict()
    return render_template("lawyer-clients.html",clients=list_of_clients,lawyer=session['lawyer'])

@app.route('/client/<int:client_id>/lawyers',methods=['GET','POST'])
@login_required_client
def list_lawyer_web(client_id=None):
    list_of_lawyers = PreAppoint.my_lawyers(client_id=client_id)
    feedbacks = Feedback.getAllFeedbacks(client_id=client_id)
    client_id = Client.get_by_id(int(client_id))
    return render_template("mylawyers.html",feedbacks=feedbacks,lawyers=list_of_lawyers,client=session['client'])

@app.route('/lawyer/<int:lawyer_id>/list-client',methods=['GET','POST'])
def list_client(lawyer_id=None):
    list_of_clients = PreAppoint.my_clients(lawyer_id=lawyer_id)
    if list_of_clients:
        return json_response({
            "error" : False,
            "message" : "Found clients",
            "clients" : list_of_clients})
    else:
        return json_response({
            "error" : True,
            "message" : "No clients found.",})

@app.route('/client/<int:client_id>/list-lawyer',methods=['GET','POST'])
def list_lawyer(client_id=None):
    list_of_lawyers = PreAppoint.my_lawyers(client_id=client_id)
    feedbacks = Feedback.getAllFeedbacks(client_id=client_id)
    
    if not feedbacks:
        feedbacks = None

    if list_of_lawyers:
        return json_response({
            "error" : False,
            "message" : "Found lawyers",
            "lawyers" : list_of_lawyers,
            "feedbacks": feedbacks})
    else:
        return json_response({
            "error" : True,
            "message" : "No lawyers found.",})

@app.route('/court-status',methods=['GET','POST'])
def list_court_status(lawyer_id=None):
    list_of_courts = Court.list_court_status()
    if list_of_courts:
        return json_response({
            "error" : False,
            "message" : "Found clients",
            "court_status" : list_of_courts})
    else:
        return json_response({
            "error" : True,
            "message" : "No clients found.",})

@app.route('/client-type',methods=['GET','POST'])
def list_client_type(lawyer_id=None):
    list_of_cts = ClientType.list_client_type()
    if list_of_cts:
        return json_response({
            "error" : False,
            "message" : "Found clients",
            "client_type" : list_of_cts})
    else:
        return json_response({
            "error" : True,
            "message" : "No clients found.",})

# route for lawyer, getting the event
@app.route('/lawyer/<int:lawyer_id>/get-event',methods=['GET','POST'])
def get_event_lawyer(lawyer_id=None):
    lawyer = Lawyer.get_by_id(int(lawyer_id))
    events = Event.query(Event.lawyer == lawyer.key).fetch()
    event_dict = []
    for event in events:
        event_dict.append(event.to_dict())
        
    if event_dict:
        return json_response({"error":False,"message": `len(event_dict)`+" events","events" : event_dict})
    else:
        return json_response({"error":True,"message": "No event(s) found"})

# route for web lawyer, getting the event
@app.route('/lawyer/<int:lawyer_id>/events',methods=['GET','POST'])
def web_get_event_lawyer(lawyer_id=None):
    list_of_clients = PreAppoint.my_clients(lawyer_id=lawyer_id)
    lawyer = Lawyer.get_by_id(int(lawyer_id))
    events = Event.query(Event.lawyer == lawyer.key).fetch()
    event_dict = []
    for event in events:
        event_dict.append(event.to_dict())
        
        # return json_response({"error":False,"message": `len(event_dict)`+" events","events" : event_dict})
    return render_template('lawyer-events.html',clients=list_of_clients,lawyer=session['lawyer'],events=event_dict)
    # else:
        # return json_response({"error":True,"message": "No event(s) found"})
        # return render_template('lawyer-events.html',events=event_dict)

# route for web client, getting the event
@app.route('/client/<int:client_id>/events',methods=['GET','POST'])
def web_get_event_client(client_id=None):
    list_of_lawyers = PreAppoint.my_lawyers(client_id=client_id)
    client = Client.get_by_id(int(client_id))
    events = Event.query(Event.client == client.key).fetch()
    event_dict = []
    for event in events:
        event_dict.append(event.to_dict())
        
        # return json_response({"error":False,"message": `len(event_dict)`+" events","events" : event_dict})
    return render_template('events.html',lawyers=list_of_lawyers,client=session['client'],events=event_dict)

# route for lawyer, getting the event
@app.route('/client/<int:client_id>/get-event',methods=['GET','POST'])
def get_event_client(client_id=None):
    client = Client.get_by_id(int(client_id))
    events = Event.query(Event.client == client.key).order(-Event.created).fetch()
    event_dict = []
    for event in events:
        event_dict.append(event.to_dict())
        
    if event_dict:
        return json_response({"error":False,"message": `len(event_dict)`+" events","events" : event_dict})
    else:
        return json_response({"error":True,"message": "No event(s) found"})

# route for lawyer, getting the event
@app.route('/client/<int:client_id>/delete-event',methods=['GET','POST'])
def delete_event_client(client_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'event_id' in req_data:
            event_id = req_data['event_id']
        event = Event.get_by_id(int(event_id))
        if event:
            event.key.delete()
            return json_response({"error":False,"message": "Event deleted !"})
        else:
            return json_response({"error":True,"message": "Event was not deleted"})

# route for lawyer, getting the event
@app.route('/lawyer/<int:lawyer_id>/delete-event',methods=['GET','POST'])
def delete_event_lawyer(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'event_id' in req_data:
            event_id = req_data['event_id']
        event = Event.get_by_id(int(event_id))
        if event:
            event.key.delete()
            return json_response({"error":False,"message": "Event deleted !"})
        else:
            return json_response({"error":True,"message": "Event was not deleted"})

# token for lawyer needed to identify which device should be notified
@app.route('/lawyer/<int:lawyer_id>/fcm-token',methods=['POST'])
def save_lawyer_token(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'fcm_token' in req_data:
            fcm_token = req_data['fcm_token']

        token = Lawyer.save(id=lawyer_id,fcm_token=fcm_token)
        if token:
            return json_response({"error":False,"message":"FCM Token saved!"})
        else: 
            return json_response({"error":True,"message":"FCM Token was not saved."})

# token for client needed to identify which device should be notified
@app.route('/client/<int:client_id>/fcm-token',methods=['POST'])
def save_client_token(client_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'fcm_token' in req_data:
            fcm_token = req_data['fcm_token']

        token = Client.save(id=client_id,fcm_token=fcm_token)
        if token:
            return json_response({"error":False,"message":"FCM Token saved!"})
        else: 
            return json_response({"error":True,"message":"FCM Token was not saved."})

# edit case route for lawyers 
@app.route('/lawyer/<int:lawyer_id>/edit-case', methods=['GET','POST'])
def edit_case(lawyer_id=None):
    case_id=request.args.get('case_id')
    if request.method == "POST":
        remarks = ""
        req_data = request.get_json(force=True)        
        if 'case_id' in req_data:
            case_id = req_data['case_id']
        if 'case_title' in req_data:
            case_title = req_data['case_title']
        if 'case_description' in req_data:
            case_description = req_data['case_description']
        if 'case_status' in req_data:
            case_status = req_data['case_status']
        if 'remarks' in req_data:
            remarks = req_data['remarks']
        if 'court_status' in req_data:
            court_status = req_data['court_status']
        if 'client_type' in req_data:
            client_type = req_data['client_type']
        
        if case_title and case_description:
            case = Case.save(id=case_id,case_title=case_title,case_description=case_description,court_status=court_status,client_type=client_type,case_status=case_status,remarks=remarks)
            if case:
                return json_response({
                    "error" : False,
                    "message" : "Case updated!"})
            else:
                return json_response({
                    "error" : True,
                    "message" : "Case was not updated!"})

# mycase route for lawyers 
@app.route('/lawyer/<int:lawyer_id>/newcase', methods=['GET','POST'])
def addcase(lawyer_id=None):
    available_practice = PracticeList.list_of_practices()
    if request.method == "POST":
        court_status = client_type = ""
        req_data = request.get_json(force=True)
        if 'case_title' in req_data:
            case_title = req_data['case_title']
        if 'client_id' in req_data:
            client_id = req_data['client_id']
        if 'case_description' in req_data:
            case_description = req_data['case_description']
        if 'client_type' in req_data:
            client_type = req_data['client_type']
        if 'court_status' in req_data:
            court_status = req_data['court_status']
        
        # payment = Payment.lawyer_subscribed(lawyer_id=lawyer_id)
        mycases = Case.my_case(lawyer_id=lawyer_id)
        lawyer = Lawyer.get_by_id(int(lawyer_id))
        if mycases > int(lawyer.limit_case):
            return json_response({
                "error":True,
                "message": "You already reached your limit as a free user, to add more case please Subscribe!"})
        else:
            if case_title and client_id and case_description:
                case = Client.get_client(client_id=client_id)
                if case:
                    case = Case.save(lawyer=lawyer_id,case_title=case_title,client_id=client_id,case_description=case_description,client_type=client_type,court_status=court_status,case_status='Case Open',remarks='')
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

    clients = Relationship.my_clients(lawyer_id=lawyer_id)


    return render_template('lawyer/lawyer-createCase.html',title="My Case",lawyer=session['lawyer'],cases=case_dict,clients=clients,available_practice=available_practice)

@app.route("/lawyer/addnote",methods=['GET','POST'])
def lawyer_add_note():
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if "case_id" in req_data:
            case_id = req_data['case_id']
        if "note" in req_data:
            note = req_data['note']
        if "title" in req_data:
            title = req_data['title']
        if "uploaded_by" in req_data:
            uploaded_by = req_data['uploaded_by']
        uploaded_by = Lawyer.get_by_id(int(uploaded_by))
        if note:
            note = Note.save(case=case_id,note=note,title=title,uploaded_by=uploaded_by.key)

            if note:
                return json_response({
                    "error" : False,
                    "message" : "Note has been added!"
                })
            else:
                return json_response({
                    "error" : False,
                    "message" : "Note was not added!"
                })

@app.route("/client/addnote",methods=['GET','POST'])
def client_add_note():
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if "case_id" in req_data:
            case_id = req_data['case_id']
        if "note" in req_data:
            note = req_data['note']
        if "title" in req_data:
            title = req_data['title']
        if "uploaded_by" in req_data:
            uploaded_by = req_data['uploaded_by']
        uploaded_by = Client.get_by_id(int(uploaded_by))
        if note:
            note = Note.save(case=case_id,note=note,title=title,uploaded_by=uploaded_by.key)

            if note:
                return json_response({
                    "error" : False,
                    "message" : "Note has been added!"
                })
            else:
                return json_response({
                    "error" : False,
                    "message" : "Note was not added!"
                })

@app.route('/lawyer/<int:lawyer_id>/mycases/<int:case_id>',methods=['GET','POST'])
def lawyer_single_case(lawyer_id=None,case_id=None):
    available_practice = PracticeList.list_of_practices()
    list_of_clients = PreAppoint.my_clients(lawyer_id=lawyer_id)
    lawyer_id = Lawyer.get_by_id(int(lawyer_id))
    # 1 case
    case = Case.get_by_id(int(case_id))
    case_dict_one = case.to_dict()
        
    files = UploadFile.get_all_files(case=case_id)
    list_of_courts = Court.list_of_courts()
    list_of_cts = ClientType.list_of_cts()
    list_of_notes = Note.list_of_notes()

    lawyer = lawyer_id.to_dict()
    return render_template('lawyer-cases-single.html',notes=list_of_notes,courts=list_of_courts,client_type=list_of_cts,files=files,results=lawyer,lawyer=session['lawyer'],title="Case "+case.case_title,case=case_dict_one,clients=list_of_clients)

# route for lawyer listing all case for lawyer
@app.route('/lawyer/<int:lawyer_id>/mycases',methods=['GET','POST'])
def getAllCase(lawyer_id=None):
    available_practice = PracticeList.list_of_practices()
    lawyer = Lawyer.get_by_id(int(lawyer_id))
    cases = Case.query(Case.lawyer == lawyer.key).order(-Case.created).fetch()
    if cases != None:
        case_dict = []
        for case in cases:
            case_dict.append(case.to_dict())
    else:
        case_dict="Empty"

    list_of_clients = PreAppoint.my_clients(lawyer_id=lawyer_id)
    list_of_courts = Court.list_of_courts()
    list_of_cts = ClientType.list_of_cts()

    lawyer_id = Lawyer.get_by_id(int(lawyer_id))
    lawyer = lawyer_id.to_dict()
    return render_template('lawyer-cases.html',courts=list_of_courts,client_type=list_of_cts,clients=list_of_clients,lawyer=session['lawyer'],cases=case_dict,title="My Cases",available_practice=available_practice,results=lawyer)

# route for lawyer listing all case for lawyer
@app.route('/client/<int:client_id>/cases',methods=['GET','POST'])
def getAllCase_web(client_id=None):
    available_practice = PracticeList.list_of_practices()
    client = Client.get_by_id(int(client_id))
    cases = Case.query(Case.client == client.key).order(-Case.created).fetch()
    if cases != None:
        case_dict = []
        for case in cases:
            case_dict.append(case.to_dict())
    else:
        case_dict="Empty"
    return render_template('cases.html',client=session['client'],cases=case_dict,title="My Cases",available_practice=available_practice)

@app.route('/client/<int:client_id>/cases/<int:case_id>',methods=['GET','POST'])
def client_case_single(client_id=None,case_id=None):
    available_practice = PracticeList.list_of_practices()
    client = Client.get_by_id(int(client_id))

    case = Case.get_by_id(int(case_id))
    case_dict_one = case.to_dict()
    list_of_notes = Note.list_of_notes()

    files = UploadFile.get_all_files(case=case_id)

    return render_template('cases-single.html',notes=list_of_notes,files=files,client=session['client'],case=case_dict_one,title="My Cases",available_practice=available_practice)

# route for client listing all case for client
@app.route('/client/<int:client_id>/get-case',methods=['GET','POST'])
def get_case_clients(client_id=None):
    client = Client.get_by_id(int(client_id))
    cases = Case.query(Case.client == client.key).order(-Case.created).fetch()
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

# route for lawyer listing all case for client
@app.route('/lawyer/<int:lawyer_id>/get-case',methods=['GET','POST'])
def get_case_lawyers(lawyer_id=None):
    lawyer = Lawyer.get_by_id(int(lawyer_id))
    cases = Case.query(Case.lawyer == lawyer.key).order(-Case.created).fetch()
    if cases != None:
        case_dict = []
        for case in cases:
            case_dict.append(case.to_dict())
        return render_template('lawyer/lawyer-mycases   .html',client=session['client'],cases=case_dict,title="My Cases",available_practice=available_practice)
    else:
        return json_response({ 
            "error" : True,
            "message" : "No case found",
            "cases" : "Empty"})
    
    return render_template('lawyer/lawyer-mycases.html',client=session['client'],cases=case_dict,title="My Cases")

# route for lawyer listing all case for client
@app.route('/lawyer/<int:lawyer_id>/mobile/get-case',methods=['GET','POST'])
def get_case_mlawyers(lawyer_id=None):
    lawyer = Lawyer.get_by_id(int(lawyer_id))
    cases = Case.query(Case.lawyer == lawyer.key).order(-Case.created).fetch()
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
    
    return render_template('lawyer/lawyer-mycases.html',client=session['client'],cases=case_dict,title="My Cases")

# route for lawyer deleting case 
@app.route('/lawyer/<int:lawyer_id>/delete-case',methods=['POST'])
def deleteCase(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if "case_id" in req_data:
            case_id = req_data["case_id"]

        case = Case.get_by_id(int(case_id))
        if case:
            case.key.delete()
            return json_response({
                "error": False,
                "message" : "Case deleted!"})
        else:
            return json_response({
                "error": True,
                "message" : "Case was not deleted"})

# route for mobile client payment ~~~~~~~
@app.route('/client/<int:client_id>/payment',methods=['POST'])
def client_payment(client_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        # payment id receive after paying using paypal, consider it as receipt
        if 'lawyer_id' in req_data:
            lawyer_id = req_data['lawyer_id']
        if 'payment_id' in req_data:
            payment_id = req_data['payment_id']
        if 'payment_method' in req_data:
            payment_method = req_data['payment_method']
        if 'payment_amount' in req_data:
            payment_amount = req_data['payment_amount']

        payment = Payment.save(lawyer=lawyer_id,client=client_id,payment_id=payment_id,payment_method=payment_method,payment_amount=payment_amount)
        if payment:
            return json_response({
                "error" : False,
                "message" : "Payment Success!"})
        else:
            return json_response({
                "error" : True,
                "message" : "Unsuccessful payment, please try again."})
        
# route for mobile lawyer subscription ~~~~~~~
@app.route('/lawyer/<int:lawyer_id>/subscribe',methods=['POST'])
def lawyer_subscribe(lawyer_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        # payment id receive after paying using paypal, consider it as receipt
        if 'payment_id' in req_data:
            payment_id = req_data['payment_id']
        if 'payment_method' in req_data:
            payment_method = req_data['payment_method']
        if 'payment_amount' in req_data:
            payment_amount = req_data['payment_amount']

        payment = Payment.save(lawyer=lawyer_id,payment_id=payment_id,payment_method=payment_method,payment_amount=payment_amount)
        if payment:

            subscribe = Subscription.save(payment=payment.id(),status="subscribed")
            if subscribe:
                return json_response({
                    "error" : False,
                    "message" : "Thank you for subscribing"})
            else:
                return json_response({
                    "error" : True,
                    "message" : "Subscription failed, please try again."})
        else:
            return json_response({
                "error" : True,
                "message" : "Unsuccessful payment, please try again."})

# save client's feedback to lawyer
@app.route('/client/<int:client_id>/lawyer/feedback',methods=['POST'])
def save_feedback(client_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'lawyer_id' in req_data:
            lawyer_id = req_data['lawyer_id']
        if 'rating' in req_data:
            rating = str(req_data['rating'])
        if 'feedback' in req_data:
            feedback = req_data['feedback']
        if 'fid' in req_data:
            fid = req_data['fid']
        if not fid:
            feedback = Feedback.save(lawyer=lawyer_id,client=client_id,rating=rating,feedback=feedback)
        elif fid:
            feedback = Feedback.save(id=fid,lawyer=lawyer_id,client=client_id,rating=rating,feedback=feedback)

        if feedback:
            return json_response({
                "error" : False,
                "message" : "Feedback saved!"})
        else:
            return json_response({
                "error" : True,
                "message" : "Feedback was not saved."})

# delete client's feedback to lawyer
@app.route('/client/<int:client_id>/lawyer/feedback-delete',methods=['POST'])
def delete_feedback(client_id=None):
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'fid' in req_data:
            fid = req_data['fid']

        if fid:
            feedback = Feedback.get_by_id(int(fid))
            if feedback:
                feedback.key.delete()
                return json_response({
                    "error" : False,
                    "message" : "Feedback deleted!"})
            else:
                return json_response({
                    "error" : True,
                    "message" : "Feedback was not deleted."})

# get client's feedback to lawyer
@app.route('/client/<int:client_id>/lawyer/feedback/<int:fid>',methods=['GET','POST'])
def solo_feedback(client_id=None,fid=None):
    feedback = Feedback.get_by_id(int(fid))
    if feedback:
        return json_response({
            "error" : False,
            "message" : "Feedback deleted!",
            "feedback": feedback.to_dict()})
    else:
        return json_response({
            "error" : True,
            "message" : "No feedback found."})


# get all feedback info
@app.route('/lawyer/total-feedback',methods=['POST'])
def feedback_info(client_id=None):
    counter = 0
    if request.method == "POST":
        req_data = request.get_json(force=True)
        if 'lawyer_id' in req_data:
            lawyer_id = req_data['lawyer_id']
        
        lawyer = Lawyer.get_by_id(int(lawyer_id))
        fb_dict = []
        feedbacks = Feedback.query(Feedback.lawyer == lawyer.key).order(-Feedback.created).fetch()
        if feedbacks:
            for f in feedbacks:
                fb_dict.append(f.to_dict())
                counter = counter + 1
        
            return json_response({
                "error" : False,
                "message" : "list of feedback",
                "feedback" : fb_dict,
                "total" : counter})
        else:
            return json_response({
                "error" : False,
                "message" : "no feedback found"})
    
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
        if 'sex' in req_data:
            sex = req_data['sex']
        if 'law_practice' in req_data:
            law_practice = req_data['law_practice']
        if 'subcategory' in req_data:
            subcategory = req_data['subcategory']

        if first_name and last_name and phone and cityOrMunicipality and office and law_practice:
            lawyer = Lawyer.save(id=lawyer_id,first_name=first_name,last_name=last_name,sex=sex,phone=phone,cityOrMunicipality=cityOrMunicipality,office=office,firm=firm,aboutme=aboutme)
            if lawyer:
                lawyer = Lawyer.get_by_id(int(lawyer_id))
                practices = Practice.query(Practice.lawyer == lawyer.key).fetch()
                for practice in practices:
                    practice.key.delete()
                # saving new pick practice
                for pract in law_practice:
                    Practice.save(lawyer=lawyer_id,pract=pract)
                
                # saving subcategory
                subpractices = Subcategory.query(Subcategory.lawyer == lawyer.key).fetch()
                for subpractice in subpractices:
                    subpractice.key.delete()
                for subpract in subcategory:
                    Subcategory.save(lawyer=lawyer.key.id(),subcategory=subpract)

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

# feature case for lawyer
@app.route('/lawyer/<int:lawyer_id>/feature',methods=['GET','POST'])
def feature_case(lawyer_id=None):
    lawyer = Lawyer.get_by_id(int(lawyer_id))
    if request.method == 'POST':
        req_data = request.get_json(force=True)
        if 'feature1' in req_data:
            feature1 = req_data['feature1']
        if 'feature2' in req_data:
            feature2 = req_data['feature2']
        if 'feature3' in req_data:
            feature3 = req_data['feature3']
        
        if feature1 and feature2 and feature3:

            features = Feature.query(Feature.lawyer == lawyer.key).fetch()

            for feature in features:
                feature.key.delete()
            
            Feature.save(lawyer=lawyer_id,case=feature1)
            Feature.save(lawyer=lawyer_id,case=feature2)
            Feature.save(lawyer=lawyer_id,case=feature3)

        return json_response({
            "error" : False,
            "message" : "Featurd Case saved!"
        })


#main render template for account setting for lawyers / editing profile route
@app.route('/lawyer/<int:lawyer_id>/myaccount',methods=['GET','POST'])
@login_required_lawyer
def lawyer_account_setting(lawyer_id=None):
    # get the lawyer details in a dictionary format
    available_practice = PracticeList.list_of_practices()
    subcategory = SubPracticeList.list_of_subpractices()
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
        practice_dict.append(practice.practice())

    subpractices = Subcategory.query(Subcategory.lawyer == lawyer.key).fetch()
    subpract_dict = []
    for subpractice in subpractices:
        subpract_dict.append(subpractice.subpract())

    cases = Case.query(Case.lawyer == lawyer.key).fetch()
    if cases != None:
        case_dict = []
        for case in cases:
            case_dict.append(case.to_dict())

    return render_template("lawyer-myaccount.html",cases=case_dict,title="Account Setting",lawyer=session.get('lawyer'),law_practice=available_practice,subcategory=subcategory,practices=practice_dict,lawyer_info=lawyer_dict,subpractices=subpract_dict)
    
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
                    'aboutme' : lawyer.aboutme,
                    'sex' : lawyer.sex,
                    'firm' : lawyer.firm })
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

    return render_template('lawyer-signin.html',title='Sign In')

#sign up lawyer route
@app.route('/lawyer/signup', methods=['GET','POST'])
def lawyer_signup():
    if session.get('client'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        req_data = request.get_json(force=True)

        firm = None
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
        if 'sex' in req_data:
            sex = req_data['sex']
        if 'law_practice' in req_data:
            law_practice = req_data['law_practice']
        if 'password' in req_data:
            password = req_data['password']
        if 'confirm' in req_data:
            confirm = req_data['confirm']

        #all fields required
        if first_name and sex and last_name and email and phone and rollno and cityOrMunicipality and office and law_practice and password and confirm:
            #valid email address
            if is_email(email):
                lawyer = Lawyer.check_email(email=email)
                if not lawyer:
                    if password == confirm:
                        if get_rollno(str(rollno)):
                            roll_exist = Lawyer.rollno_exist(rollno=rollno)
                            if not roll_exist:
                                lawyer = Lawyer.save(first_name=first_name,last_name=last_name,email=email,phone=phone,rollno=rollno,sex=sex,cityOrMunicipality=cityOrMunicipality,office=office,firm=firm,password=password,status="activated",limit_case="5")
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
                            lawyer = Lawyer.save(first_name=first_name,last_name=last_name,email=email,phone=phone,rollno=rollno,cityOrMunicipality=cityOrMunicipality,office=office,firm=firm,password=password,status="deactivated",limit_case="5")
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
    available_practice = PracticeList.list_of_practices()
    
    return render_template('lawyer-signup.html',title='Lawyer Sign Up',law_practice=available_practice)

# send email with token client
def send_reset_email_client(client):
    token = client.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@case.com', recipients=[client.email])
    msg.body  = "To reset your password, visit the following link: \n" + url_for('client_reset_token',token=token, _external=True) +"\n if you did not make this request then simply ignore this email and no changes will be made."
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
                    send_reset_email_client(client)
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
    return render_template('forgot.html',title="Reset")

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
        
    return render_template('reset.html',title="Reset Password",token=token)


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
    return render_template('lawyer-forgot.html',title="Reset")

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
        
    return render_template('lawyer-reset.html',title="Reset Password",token=token)

# see more details
@app.route('/lawyer/find/lawyer-details/<string:lawyer_email>')
def see_more(lawyer_email):
    lawyer= []
    if lawyer_email:
        lawyer = Lawyer.check_email(lawyer_email)
        if lawyer:
            # return json_response({
            #         "error" : True,
            #         "message" : lawyer_details})
            logging.info(lawyer.key.id())
            features = Feature.get_all_feature(lawyer_id=lawyer.key.id())
            practices = Practice.query(Practice.lawyer == lawyer.key).fetch()
            practice_dict = []
            for practice in practices:
                practice_dict.append(practice.practice())
            subpractices = Subcategory.query(Subcategory.lawyer == lawyer.key).fetch()
            subpract_dict = []
            for subpractice in subpractices:
                subpract_dict.append(subpractice.subpract())
            if session.get('lawyer'):
                return render_template('lawyer-single.html',title='Lawyer Details',features=features,subcategory=subpract_dict,practices=practice_dict,lawyer=session['lawyer'],result=lawyer)
            elif session.get('client'):
                return render_template('lawyer-single.html',title='Lawyer Details',features=features,subcategory=subpract_dict,practices=practice_dict,client=session['client'],result=lawyer)
            else:
                return render_template('lawyer-single.html',title='Lawyer Details',features=features,subcategory=subpract_dict,practices=practice_dict,result=lawyer)
        else:
            return json_response({
                    "error" : True,
                    "message" : "didnt retrieve"})

    else:
        return json_response({
                    "error" : True,
                    "message" : "No lawyer is selected"})

    return render_template('lawyer-single.html',lawyer=session['lawyer'],title="Lawyer Details")

@app.route('/lawyer/<int:lawyer_id>/deactivate')
@login_required_lawyer
def lawyer_deactivate(lawyer_id=None):
    
    if lawyer_id:
        lawyer = Lawyer.get_by_id(int(lawyer_id))
        if lawyer:
            deactivated = Lawyer.save(id=lawyer_id,status="deactivated")
            
            if deactivated:

                return render_template('login.html')
            
            else:
                return json_response({
                    "error" : True,
                    "message" : "Lawyer not deactivated"})

        else:
            return json_response({
                    "error" : True,
                    "message" : "Lawyer not Recognized"})
    else:
        return json_response({
                    "error" : True,
                    "message" : "Lawyer Id not transferred"})

@app.route("/about",methods=['GET'])
def about():
    if session.get('lawyer') is not None:
        return render_template('about.html',title='About Us',lawyer=session['lawyer'])
    elif session.get('client') is not None:
        return render_template('about.html',title='About Us',client=session['client'])
    else:
        return render_template("about.html",title="About Us")

@app.route("/contact",methods=['GET'])
def contact():
    if session.get('lawyer') is not None:
        return render_template('contact.html',title='Contact',lawyer=session['lawyer'])
    elif session.get('client') is not None:
        return render_template('contact.html',title='Contact',client=session['client'])
    else:
        return render_template("contact.html",title="Contact")

# sign out route
@app.route('/signout')
def signout():
    if session.get('client') is not None:
        del session['client']
        return redirect(url_for('client_signin'))
    if session.get('lawyer') is not None:
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
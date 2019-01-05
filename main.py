from flask import Flask, render_template, url_for, request, session, redirect, jsonify
from config import SECRET_KEY

from models.lawyer import Lawyer


app = Flask(__name__)
app.secret_key = SECRET_KEY

#home route
@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        main_category = request.form.get('main_category')
        location = request.form.get('location')
    
        return redirect(url_for('sub_category',main_category=main_category,location=location))

    return render_template('home.html',title='Home')

#login route
@app.route('/lawyer_login')
def lawyer_login():
    return render_template('lawyer_login.html',title='Lawyer Login')


#sign up attorney route
@app.route('/attorneys', methods=['GET','POST'])
def attorneys():
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
        if 'office' in req_data:
            office = req_data['office']
        if 'specialize' in req_data:
            specialize = req_data['specialize']
        if 'bar_number' in req_data:
            bar_number = req_data['bar_number']

        lawyer = Lawyer.save(first_name=first_name,last_name=last_name,email=email,phone=phone,office=office,specialize=specialize,bar_number=bar_number,password='')
        if lawyer:
            return redirect(url_for('verify'))
        else:
                return redirect(
                    url_for('attorneys',
                        err=1, m="Something went wrong please try again."))

    return render_template('attorneys.html',title='Attorney Registration')

@app.route('/lawyers',methods=['GET','POST'])
def lawyer():
    main_category = request.form.get('main_category')
    location = request.form.get('location')
    return render_template('lawyer.html',title='Lawyers',main_category=main_category,location=location)

@app.route('/verify')
def verify():
    return render_template('verify.html', title='Verifying details')

if __name__ == '__main__':
    app.run(debug=True)
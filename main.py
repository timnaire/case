from flask import Flask, render_template, url_for, request, session, redirect
from config import SECRET_KEY

from models.lawyer import Lawyer


app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.route('/lawyer_login')
def lawyer_login():
    return render_template('lawyer_login.html',title='Lawyer Login')

@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        main_category = request.form.get('main_category')
        location = request.form.get('location')
    
        return redirect(url_for('sub_category',main_category=main_category,location=location))

    return render_template('home.html',title='Home')

@app.route('/attorneys', methods=['GET','POST'])
def attorneys():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        office = request.form.get('office')
        specialize = request.form.get('specialize')
        bar_number = request.form.get('bar_number')

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
from functools import wraps

from flask import render_template, redirect, url_for, flash, request, session
from flask_wtf import FlaskForm
from flask_login import login_user, current_user, logout_user, login_required

from lms import app, db, bcrypt
from lms.forms import RegistrationForm, LoginForm, AddLibrarianForm
from lms.models import Admin, Librarian

''' OPTIONAL
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404 '''

''' LANDING PAGE '''
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

'''LOGIN FOR ALL USERS '''
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        if form.user_type.data == 'adm':
            session['user_type'] = 'admin'
            admin = Admin.query.filter_by(email=form.email.data).first()
            if admin and bcrypt.check_password_hash(admin.password, form.password.data):
                login_user(admin, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Invalid email/password', 'danger')
        elif form.user_type.data == 'lib':
            session['user_type'] = 'librarian'
            librarian = Librarian.query.filter_by(email=form.email.data).first()
            if librarian and bcrypt.check_password_hash(librarian.password, form.password.data):
                login_user(librarian, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Invalid email/password', 'danger')
    return render_template('login.html', title='Login', form=form)

'''REGISTRATION OF ADMIN'''
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        admin = Admin(username=form.username.data, name=form.name.data, email=form.email.data, 
            password=hashed_pw, institute=form.institute.data.lower())
        db.session.add(admin)
        db.session.commit()
        flash(f'Account created for {form.username.data} from {form.institute.data}! Please login to access', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

''' LOGOUT '''
@app.route('/logout')
def logout():
    logout_user()
    session['user_type'] = None
    return redirect(url_for('login'))


''' PROFILE PAGE FOR ALL USERS '''
# @app.route('/profile', methods=['GET', 'POST'], endpoint='profile')
# @login_required
# def profile():
#     # form = ChangeFieldForm()
    # if form.validate_on_submit():
    #     if bcrypt.check_password_hash(current_user.password, form.password.data):
    #         return redirect(url_for('logout'))
            # flash('Changes saved! Please login with your new credentials')
            # return redirect(url_for('logout'))
    # return render_template('profile.html', title='My Profile', form=form)
    
@app.route('/profile/chng_uname', methods=['GET', 'POST'], endpoint='chng_uname')
@login_required
def chng_uname():
    form = request.form
    if form.cur_password.validate() and form.new_username.validate():
        if bcrypt.check_password_hash(current_user.password, form.password.data):
            # update it
            flash('Changes saved! Please login with your new credentials')
            return redirect(url_for('logout'))
        else:
            form.cur_password.errors.append('Invalid password')
    return render_template('chng_uname.html', form=form)


''' ADMIN PAGES '''

@app.route('/admin/add-librarian', methods=['GET', 'POST'], endpoint='add_librarian')
@login_required
def add_librarian():
    form = AddLibrarianForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        librarian = Librarian(username=form.username.data, name=form.name.data, email=form.email.data, 
            password=hashed_pw, admin_id=current_user.id)
        db.session.add(librarian)
        db.session.commit()
        flash(f'Account created for {form.username.data} from {current_user.institute}! Please login to access', 'success')
        return redirect(url_for('add_librarian'))
    return render_template('admin/add_librarian.html', title='Add Librarian', form=form)


''' format pls '''
@app.route('/admin/remove-librarian', methods=['GET', 'POST'], endpoint='remove_librarian')
@login_required
def remove_librarian():
    form = request.form
    if form:
        if form.get('email') == '' and form.get('remove') == '':
            #delete the record
            id = form.get('id')
            Librarian.query.filter_by(id=id).delete()
            db.session.commit()
            flash('Librarian account deleted', 'success')
        elif form.get('cancel') == '':
            return redirect(url_for('remove_librarian'))
        else:
            librarian = Librarian.query.filter_by(email=form.get('email')).first()
            if librarian:
                return render_template('admin/remove_librarian.html', title='Remove Librarian', librarian=librarian)
            else:
                flash('Librarian record does not exist', 'danger')
    return render_template('admin/remove_librarian.html', title='Remove Librarian', librarian=None)

@app.route('/admin/view-librarian', endpoint='view_librarian')
@login_required
def view_librarian():
    print(current_user.librarians)
    return render_template('admin/view_librarian.html', title='View Librarian')
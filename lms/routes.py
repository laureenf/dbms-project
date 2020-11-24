from functools import wraps
from sqlalchemy import text
from flask import render_template, redirect, url_for, flash, request, session
from flask_wtf import FlaskForm
from flask_login import login_user, current_user, logout_user, login_required

from lms import app, db, bcrypt
from lms.forms import RegistrationForm, LoginForm, AddLibrarianForm, AddStudentForm, AddBookForm
from lms.models import *

db.create_all()
db.session.execute(text('PRAGMA foreign_keys = ON'))

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
            password=hashed_pw, admin_id=current_user.id, address=form.address.data, contact_no=form.contact_no.data)
        db.session.add(librarian)
        db.session.commit()
        flash(f'Account created for {form.username.data} from {current_user.institute}! Please login to access', 'success')
        return redirect(url_for('add_librarian'))
    return render_template('admin/add_librarian.html', title='Add Librarian', form=form)

@app.route('/admin/remove-librarian', methods=['GET', 'POST'], endpoint='remove_librarian')
@login_required
def remove_librarian():
    form = request.form
    if form:
        if form.get('id') == '' and form.get('remove') == '':
            #delete the record
            id = form.get('id1')
            Librarian.query.filter_by(id=id).delete()
            db.session.commit()
            flash('Librarian account deleted', 'success')
        elif form.get('cancel') == '':
            return redirect(url_for('remove_librarian'))
        else:
            librarian = Librarian.query.filter_by(id=form.get('id')).first()
            if librarian:
                return render_template('admin/remove_librarian.html', title='Remove Librarian', librarian=librarian)
            else:
                flash('Librarian record does not exist', 'danger')
    return render_template('admin/remove_librarian.html', title='Remove Librarian', librarian=None)

@app.route('/admin/view-librarian', endpoint='view_librarian')
@login_required
def view_librarian():
    return render_template('admin/view_librarian.html', title='View Librarian')

'''END OF ADMIN PAGES'''

'''LIBRARIAN PAGES'''
#student functions
@app.route('/librarian/add-student', methods=['GET', 'POST'], endpoint='add_student')
@login_required
def add_student():
    form = AddStudentForm()
    if form.validate_on_submit():
        dept = Department.query.filter_by(name=form.dept.data).first()
        #if dept exists, just add student record else, create dept and then add student record
        if dept:
            student = Student(name=form.name.data, year=form.year.data, address=form.address.data, 
             contact_no=form.contact_no.data, dept=dept, admin=current_user.admin)
        else:
            dept = Department(name=form.dept.data)
            student = Student(name=form.name.data, year=form.year.data, address=form.address.data, 
             contact_no=form.contact_no.data, dept=dept, admin=current_user.admin)
            db.session.add(dept)
            db.session.commit()
        db.session.add(student)
        db.session.commit()
        flash('Student record created', 'success')
        return redirect(url_for('add_student'))
    return render_template('librarian/add_student.html', form=form, title='Add Student')

@app.route('/librarian/remove-student', methods=['GET', 'POST'], endpoint='remove_student')
@login_required
def remove_student():
    form = request.form
    if form:
        if form.get('id') == '' and form.get('remove') == '':
            #delete the record
            id = form.get('id1')
            Student.query.filter_by(id=id).delete()
            db.session.commit()
            flash('Student record deleted', 'success')
        elif form.get('cancel') == '':
            return redirect(url_for('remove_student'))
        else:
            student = Student.query.filter_by(id=form.get('id')).first()
            if student:
                return render_template('librarian/remove_student.html', title='Remove student', student=student)
            else:
                flash('Student record does not exist', 'danger')
    return render_template('librarian/remove_student.html', title='Remove Student', student=None)

@app.route('/librarian/view-student', endpoint='view_student')
@login_required
def view_student():
    return render_template('librarian/view_student.html')

#book functions
@app.route('/librarian/add-book', methods=['GET', 'POST'], endpoint='add_book')
@login_required
def add_book():
    form = AddBookForm()
    if form.validate_on_submit():
        book = Book(name=form.name.data, edition=form.edition.data, price=form.price.data)
        #add dept
        dept = Department.query.filter_by(name=form.dept.data.lower()).one_or_none()
        if not dept:
            dept = Department(name=form.dept.data)
            db.session.add(dept)
            db.session.commit()
        book.dept = dept
        #add authors
        authors_book = [author.strip() for author in form.authors.data.split(',')]
        for author in authors_book:
            authr = Author.query.filter_by(name=author).one_or_none()
            if not authr:
                authr = Author(name=author)
                book.authors.append(authr)
                db.session.add(authr)
        db.session.add(book)
        db.session.commit()
        #add copies available
        inst_book = InstituteBooks(copies_available=form.copies_available.data)
        inst_book.admin = current_user.admin
        inst_book.book = book
        db.session.add(inst_book)
        db.session.commit()
        flash('Book record created', 'success')
        return redirect(url_for('add_book'))
    return render_template('librarian/add_book.html', form=form, title='Add Book')

@app.route('/librarian/remove-book', methods=['GET', 'POST'], endpoint='remove_book')
@login_required
def remove_book():
    form = request.form
    if form:
        if form.get('id'):
            #print details
            inst_book = InstituteBooks.query.filter_by(book_id=form.get('id'), admin=current_user.admin).one_or_none()
            if inst_book:
                return render_template('librarian/remove_book.html', inst_book=inst_book, copies=form.get('copies'))
            else:
                flash('Book record not found', 'danger')
        elif form.get('remove') == '':
            #delete record
            inst_book = InstituteBooks.query.filter_by(book_id=form.get('id1'), admin=current_user.admin).one_or_none()
            if inst_book:
            #it exists in the institute
                copies = int(form.get('copies1'))
                if copies > 0 and copies < inst_book.copies_available:
                #delete specified no of copies
                    inst_book.copies_available = inst_book.copies_available - copies
                    db.session.add(inst_book)
                    db.session.commit()
                    flash(f"Specified no of copies deleted. Remaining copies are {inst_book.copies_available}", 'success')
                elif copies == inst_book.copies_available:
                #delete book record
                    InstituteBooks.query.filter_by(book_id=inst_book.book_id, admin=current_user.admin).delete()
                    db.session.commit()
                    flash('Book record deleted', 'success')
                else:
                    flash('Invalid no of copies', 'danger')
                return redirect(url_for('remove_book'))
        elif form.get('cancel') == '':
            #cancel
            return redirect(url_for('remove_book'))
    return render_template('librarian/remove_book.html', inst_book=None)

@app.route('/librarian/view-book', endpoint='view_book')
@login_required
def view_book():
    inst_books = InstituteBooks.query.filter_by(admin=current_user.admin).all()
    return render_template('librarian/view_book.html', inst_books=inst_books)
'''END OF LIBRARIAN PAGES'''
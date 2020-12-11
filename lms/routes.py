from functools import wraps
from sqlalchemy import text, desc
from datetime import date
from flask import render_template, redirect, url_for, flash, request, session
from flask_wtf import FlaskForm
from flask_login import login_user, current_user, logout_user, login_required

from lms import app, db, bcrypt
from lms.forms import *
from lms.models import *

db.create_all()
db.session.execute(text('PRAGMA foreign_keys = ON'))

'''PAGE NOT FOUND'''
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404 


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


''' PROFILE PAGE FOR ADMIN AND LIBRARIAN '''
@app.route('/profile', methods=['GET', 'POST'], endpoint='profile')
@login_required
def profile():
    return render_template('profile.html', title='My Profile')
    
@app.route('/profile/change-username', methods=['GET', 'POST'], endpoint='change_username')
@login_required
def change_username():
    form = ChangeUsernameForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.cur_password.data):
            # update it
            current_user.username = form.new_username.data
            db.session.commit()
            flash(f'Changes saved!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid password', 'danger')
    return render_template('profile/change_username.html', form=form, title='Change Username')

@app.route('/profile/change-email', methods=['GET', 'POST'], endpoint='change_email')
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.cur_password.data):
            # update it
            current_user.email = form.new_email.data
            db.session.commit()
            flash('Changes saved! Please login with your new credentials', 'success')
            return redirect(url_for('logout'))
        else:
            flash('Invalid password', 'danger')
    return render_template('profile/change_email.html', form=form, title='Change Email')

@app.route('/profile/change-password', methods=['GET', 'POST'], endpoint='change_password')
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.cur_password.data):
            # update it
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            db.session.commit()
            flash('Changes saved! Please login with your new credentials', 'success')
            return redirect(url_for('logout'))
        else:
            flash('Invalid password', 'danger')
    return render_template('profile/change_password.html', form=form, title='Change Password')

'''END OF PROFILE PAGES'''

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

@app.route('/admin/delete-account', methods=['GET', 'POST'], endpoint='delete_account')
@login_required
def delete_account():
    form = request.form
    if form:
        if form.get('password'):
            if bcrypt.check_password_hash(current_user.password, form.get('password')):
                return render_template('profile/delete_account.html', title='Delete Account', submit=True)
            else:
                flash('Invalid password', 'danger')
                return redirect(url_for('delete_account'))
        elif form.get('delete') == '':
            Admin.query.filter_by(id=current_user.id).delete()
            db.session.commit()
            return redirect(url_for('logout'))
        elif form.get('cancel') == '':
            return redirect(url_for('delete_account'))
    return render_template('profile/delete_account.html', title='Delete Account', submit=False)

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
                return render_template('librarian/remove_student.html', title='Remove Student', student=student)
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
        book = Book.query.filter_by(name=form.name.data, edition=form.edition.data, price=form.price.data).one_or_none()
        if not book:
            #book doesn't exist
            #add dept
            book = Book(name=form.name.data, edition=form.edition.data, price=form.price.data)
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
                    db.session.add(authr)
                book.authors.append(authr)
            db.session.add(book)
            db.session.commit()
            #add copies available
        inst_book = InstituteBooks.query.filter_by(book=book, admin=current_user.admin).one_or_none()
        if inst_book:
            inst_book.copies_available = inst_book.copies_available + form.copies_available.data
        else:
            inst_book = InstituteBooks(copies_available=form.copies_available.data)
            inst_book.admin = current_user.admin
            inst_book.book = book
        db.session.add(inst_book)
        db.session.commit()
        flash('Book record created/updated', 'success')
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
    return render_template('librarian/view_book.html', inst_books=inst_books, available=True)

@app.route('/librarian/issue-book', methods=['GET', 'POST'], endpoint='issue_book')
@login_required
def issue_book():
    form = request.form
    if form:
        if form.get('book_id'):
            #print details
            book = InstituteBooks.query.filter_by(book_id=form.get('book_id'), admin=current_user.admin).one_or_none()
            student = Student.query.filter_by(id=form.get('student_id')).one_or_none()
            if book:
                if not book.copies_available:
                    flash("Book unavailable at the moment", 'danger')
                    return redirect(url_for('issue_book'))
            else:
                flash("Book record doesn't exist", 'danger')
                return redirect(url_for('issue_book'))
            if not student:
                flash("Student record doesn't exist", 'danger')
                return redirect(url_for('issue_book'))
            if IssuedBooks.query.filter_by(book_id=book.book_id, student_id=student.id, is_returned=False).one_or_none():
                flash("Book has already been issued to student", 'danger')
                return redirect(url_for('issue_book'))
            return render_template('librarian/issue_book.html', inst_book=book, student=student)
        elif form.get('issue') == '':
            #issue book
            inst_bk = InstituteBooks.query.filter_by(book_id=form.get('bk_id'), admin=current_user.admin).first()
            book_issue = IssuedBooks(book_id=form.get('bk_id'), student_id=form.get('st_id'))
            inst_bk.copies_available = inst_bk.copies_available - 1
            db.session.add(book_issue)
            db.session.add(inst_bk)
            db.session.commit()
            flash("Book issued successfully", 'success')
            return redirect(url_for('issue_book'))
        elif form.get('cancel') == '':
            #go back
            return redirect(url_for('issue_book'))
    return render_template('librarian/issue_book.html', book=None, student=None, title='Issue Book')

@app.route('/librarian/return-book', methods=['GET', 'POST'], endpoint='return_book')
@login_required
def return_book():
    duration = 5 
    form = request.form
    if form:
        if form.get('book_id'):
            issued_book = IssuedBooks.query.filter_by(book_id=form.get('book_id'), student_id=form.get('student_id'), is_returned=False).one_or_none()
            if not issued_book:
                flash("Record doesn't exist", 'danger')
                return redirect(url_for('return_book'))
            else:
                #print details
                issued_book.return_date = date.today()
                interval = (issued_book.return_date - issued_book.issue_date).days
                if interval > duration:
                    #calculate fine
                    issued_book.fine_due = interval * 5
                return render_template('librarian/return_book.html', title='Return Book', issued_book=issued_book)
        elif form.get('return') == '':
            #return book
            issued_book = IssuedBooks.query.filter_by(book_id=form.get('bk_id'), student_id=form.get('st_id'), is_returned=False).one_or_none()
            issued_book.return_date = date.today()
            interval = (issued_book.return_date - issued_book.issue_date).days
            if interval > duration:
                    #calculate fine
                    issued_book.fine_due = interval * 5
            issued_book.is_returned = True
            db.session.add(issued_book)
            db.session.commit()
            return redirect(url_for('return_book'))
        elif form.get('cancel') == '':
            #cancel
            return redirect(url_for('return_book'))
    return render_template('librarian/return_book.html', title='Return Book', issued_book=None)

@app.route('/librarian/student-history/<int:id>/current', endpoint='student_history_current')
@login_required
def student_history_current(id):
    student_history_current = IssuedBooks.query.filter_by(student_id=id, is_returned=False).all()
    return render_template('librarian/student_history.html', student_history=student_history_current, is_current=True, student_id=id)

@app.route('/librarian/student-history/<int:id>/past', endpoint='student_history_past')
@login_required
def student_history_past(id):
    student_history_past = IssuedBooks.query.filter_by(student_id=id, is_returned=True).order_by(desc(IssuedBooks.return_date)).all()
    return render_template('librarian/student_history.html', student_history=student_history_past, is_current=False, student_id=id)
'''END OF LIBRARIAN PAGES'''
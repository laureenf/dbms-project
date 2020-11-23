from datetime import datetime, date
from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, HiddenField, IntegerField, FloatField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError, NumberRange
from lms.models import Admin, Librarian

class Base():
    def validate_email(self, email):
        if Admin.query.filter_by(email=email.data.lower()).first() or \
        Librarian.query.filter_by(email=email.data.lower()).first():
            raise ValidationError('This email has already been registered. Please choose a different one.')
    
    def validate_username(self, username):
        if Admin.query.filter_by(username=username.data.lower()).first() or \
        Librarian.query.filter_by(username=username.data.lower()).first():
            raise ValidationError('This username has already been registered. Please choose a different one.')

class RegistrationForm(FlaskForm, Base):
    institute = StringField('Institute Name', validators=[
        DataRequired(), Length(min=3, max=50, message='Institute name must be between 3 and 50 characters')])
    name = StringField('Name', validators=[
        DataRequired(), Length(min=3, max=20, message='Name must be between 3 and 20 characters')])
    username = StringField('Username', validators=[
        DataRequired(), Length(min=3, max=20), 
        Regexp(r'^\w+$', message='Username must contain only letters, numbers, underscores')])
    email = StringField('Email', validators=[
        Email(), DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords do not match')
    ])
    submit = SubmitField('Sign Up')
    
    def validate_institute(self, institute):
        adm = Admin.query.filter_by(institute=institute.data.lower()).first()
        if adm:
            raise ValidationError('This institute has already been registered. Please contact your institute for further details.')


class LoginForm(FlaskForm):
    user_type = SelectField('Login as ', choices=[('adm', 'Admin'), ('lib', 'Librarian')]) 
    email = StringField('Email', validators=[
        Email(), DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

# class ChangeFieldForm(FlaskForm):
#     id = HiddenField()
#     cur_password = PasswordField('Enter your current password', validators=[
#         DataRequired()])
#     new_username = StringField('Enter your new username', validators=[
#         DataRequired(), Length(min=3, max=20), 
#         Regexp('^\w+$', message='Username must contain only letters, numbers, underscores')])
#     new_email = StringField('Enter your new email', validators=[
#         Email(), DataRequired()])
#     new_password = PasswordField('Enter your new password', validators=[
#         DataRequired()])
#     confirm_password = PasswordField('Confirm password', validators=[
#         DataRequired(), EqualTo('password', message='Passwords do not match')
#     ])
#     save_changes = SubmitField('Save Changes')

#     def validate_email(self, new_email):
#         user1 = Admin.query.filter_by(email=new_email.data).first()
#         user2 = Librarian.query.filter_by(email=new_email.data).first()
#         user3 = Borrower.query.filter_by(email=new_email.data).first()
#         if user1 or user2 or user3:
#             raise ValidationError('This email has already been registered. Please choose a different one.')
    
#     def validate_username(self, new_username):
#         user1 = Admin.query.filter_by(username=new_username.data).first()
#         user2 = Librarian.query.filter_by(username=new_username.data).first()
#         user3 = Borrower.query.filter_by(username=new_username.data).first()
#         if user1 or user2 or user3:
#             raise ValidationError('This username has already been registered. Please choose a different one.')

class AddLibrarianForm(FlaskForm, Base):
    join_date = DateField('Join Date', default=datetime.today, format='%Y-%m-%d')
    name = StringField('Name', validators=[
        DataRequired(), Length(min=3, max=20, message='Name must be between 3 and 20 characters')])
    username = StringField('Username', validators=[
        DataRequired(), Length(min=3, max=20), 
        Regexp('^\w+$', message='Username must contain only letters, numbers, underscores')])
    email = StringField('Email', validators=[
        Email(), DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired()])
    address = StringField('Address', validators=[
        DataRequired(), Length(min=3, message='Address must be more than 3 characters long')])
    contact_no = StringField('Contact No', validators=[
        DataRequired(), 
        Regexp(r'^\d{10}$', message='Contact no must contain 10 digits')])
    submit = SubmitField('Add Librarian') 

    def validate_join_date(self, join_date):
        if str(join_date.data) < '1970-01-01' or str(join_date.data) > str(date.today()):
            raise ValidationError('Invalid date')

class AddStudentForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(), Length(min=3, max=20, message='Name must be between 3 and 20 characters')])
    year = SelectField('Year', choices=[('1', '1st'), ('2', '2nd'), ('3', '3rd'), ('4', '4th')])
    address = StringField('Address', validators=[
        DataRequired(), Length(min=3, message='Address must be more than 3 characters long')])
    contact_no = StringField('Contact No', validators=[
        DataRequired(), 
        Regexp(r'^\d{10}$', message='Contact no must contain 10 digits')])
    dept = SelectField('Department', 
        choices=[('cse', 'CSE'), ('ece', 'ECE'), ('eee', 'EEE'), ('me', 'ME'), ('civ', 'CIVIL'), ('mca', 'MCA'), ('mba', 'MBA')])
    submit = SubmitField('Add Student')

    def validate_year(self, year):
        if self.dept.data == 'mca' and (year.data == '3' or year.data == '4'):
            raise ValidationError('Duration of MCA is 2 years')

class AddBookForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(), Length(min=3, max=20, message='Name must be between 3 and 20 characters')])
    authors = StringField('Author(s)', validators=[
        DataRequired()])
    dept = SelectField('Department', 
        choices=[('cse', 'CSE'), ('ece', 'ECE'), ('eee', 'EEE'), ('me', 'ME'), ('mca', 'MCA'), ('mba', 'MBA'),
        ('mat', 'MATH'), ('chem', 'CHEMISTRY'), ('phy', 'PHYSICS'), ('eng', 'ENGLISH')])
    edition = IntegerField('Edition', validators=[
        DataRequired(), NumberRange(min=1, message='Edition has to be greater than or equal to 1')])
    price = FloatField('Price', validators=[
        DataRequired(), NumberRange(min=1, message='Price has to be positive')])
    copies_available = IntegerField('Copies Available', validators=[
        DataRequired(), NumberRange(min=1, message='Copies available has to be greater than or equal to 1')])
    submit = SubmitField('Add Book')

    

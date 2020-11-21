from datetime import datetime, date
from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, HiddenField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError
from lms.models import Admin, Librarian, Borrower

class Base():
    def validate_email(self, email):
        if Admin.query.filter_by(email=email.data.lower()).first() or \
        Librarian.query.filter_by(email=email.data.lower()).first() or \
        Borrower.query.filter_by(email=email.data.lower()).first():
            raise ValidationError('This email has already been registered. Please choose a different one.')
    
    def validate_username(self, username):
        if Admin.query.filter_by(username=username.data.lower()).first() or \
        Librarian.query.filter_by(username=username.data.lower()).first() or \
        Borrower.query.filter_by(username=username.data.lower()).first():
            raise ValidationError('This username has already been registered. Please choose a different one.')

class RegistrationForm(FlaskForm, Base):
    institute = StringField('Institute Name', validators=[
        DataRequired(), Length(min=3, max=50, message='Institute name must be between 3 and 50 characters')])
    name = StringField('Name', validators=[
        DataRequired(), Length(min=3, max=20, message='Name must be between 3 and 20 characters')])
    username = StringField('Username', validators=[
        DataRequired(), Length(min=3, max=20), 
        Regexp('^\w+$', message='Username must contain only letters, numbers, underscores')])
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
    user_type = SelectField('Login as ', choices=[('adm', 'Admin'), ('lib', 'Librarian'), ('bor', 'Borrower')]) 
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
    submit = SubmitField('Add Librarian')

    def validate_join_date(self, join_date):
        # start_date = datetime.strptime(, '%Y-%m-%d')
        if str(join_date.data) < '1970-01-01' or str(join_date.data) > str(date.today()):
            raise ValidationError('Invalid date')
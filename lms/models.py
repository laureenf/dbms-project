from datetime import datetime
from lms import db, login_manager
from flask import session
from flask_login import UserMixin, current_user

@login_manager.user_loader
def load_user(user_id):
    if session['user_type'] == 'admin':
        return Admin.query.get(int(user_id))
    elif session['user_type'] == 'librarian':
        return Librarian.query.get(int(user_id))
    else:
        return None

class User(db.Model):
    __abstract__ = True
    name = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Admin(User, UserMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    institute = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"Admin('{self.name}', '{self.email}', '{self.institute}')"

class Librarian(User, UserMixin):
    __tablename__ = 'librarian'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(120), nullable=False, default='Mangaluru')
    contact_no = db.Column(db.String(10), nullable=False)
    join_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)

    admin = db.relationship('Admin', backref='librarians', foreign_keys=[admin_id])

    def __repr__(self):
        return f"Librarian('{self.name}', '{self.email}', {self.join_date}, '{self.address}', {self.contact_no})"

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(5), unique=True, nullable=False)

    def __repr__(self):
        return f"Dept({self.id}, '{self.name}')"

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(120), nullable=False, default='Mangaluru')
    contact_no = db.Column(db.String(10), nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey('department.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)

    dept = db.relationship('Department', foreign_keys=[dept_id])
    admin = db.relationship('Admin', backref='students', foreign_keys=[admin_id])

    def __repr__(self):
        return f"Student('{self.name}', '{self.admin.institute}', '{self.dept.name}', {self.year}, {self.address}', {self.contact_no})"

class InstituteBooks(db.Model):
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True, nullable=False)
    copies_available = db.Column(db.Integer, nullable=False, default=1)

    book = db.relationship('Book', backref='institutes')
    admin = db.relationship('Admin', backref='books')

    def __repr__(self):
        return f"InstBook('{self.book.name}', '{self.admin.institute}', {self.copies_available})"

class IssuedBooks(db.Model):
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    issue_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.Date)
    fine_due = db.Column(db.Integer, nullable=False, default=0)

    book = db.relationship('Book', backref='students')
    student = db.relationship('Student', backref='books')

    def __repr__(self):
        return f"IssuedBook('{self.book.name}', '{self.student.name}', '{self.issue_date}', {self.fine_due})"

# Association table for author and book
author_books = db.Table('author_books',
    db.Column('author_id', db.Integer, db.ForeignKey('author.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    edition = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)

    dept_id = db.Column(db.Integer, db.ForeignKey('department.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    dept = db.relationship('Department', foreign_keys=[dept_id]) 
    authors = db.relationship('Author', secondary=author_books)
    

    def __repr__(self):
        return f"Book({self.name}, {self.edition}, {self.price}, '{self.dept.name}', {self.no_of_copies})"

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Author({self.id}, '{self.name}')"
    
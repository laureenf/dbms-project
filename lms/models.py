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
    join_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)

    admin = db.relationship('Admin', backref='librarians', foreign_keys=[admin_id])

    def __repr__(self):
        return f"Librarian('{self.name}', '{self.email}', {self.join_date})"

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(5), unique=True, nullable=False)

    def __repr__(self):
        return f"Dept({self.id}, '{self.name}')"

class Borrower(db.Model):
    __tablename__ = 'borrower'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey('department.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)

    dept = db.relationship('Department', foreign_keys=[dept_id])
    admin = db.relationship('Admin', backref='borrowers', foreign_keys=[admin_id])

    def __repr__(self):
        return f"Borrower('{self.name}', '{self.admin.institute}', '{self.dept.name}')"

# Association table for author and book
# author_books = db.Table('author_books',
#     db.Column('author_id', db.Integer, db.ForeignKey('author.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
#     db.Column('book_id', db.Integer, db.ForeignKey('book.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
# )

# class Book(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(20), nullable=False)
#     edition = db.Column(db.Integer, nullable=False, default=1)
#     price = db.Column(db.Float, nullable=False)
#     copies_available = db.Column(db.Integer, nullable=False)
#     branch = db.Column(db.String(5), nullable=False)
#     authors = db.relationship('Author', secondary=author_books, lazy='subquery', backref=db.backref('books', lazy=True))
#     # student = db.relationship('Borrower', backref='hello', lazy=True)

#     def __repr__(self):
#         return f"Book({self.name}, {self.edition}, {self.price}, '{self.branch}', {self.no_of_copies})"

# class Author(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(20), nullable=False)

#     def __repr__(self):
#         return f"Author({self.id}, '{self.name}')"

# # class IssuedBooks(db.Model):
# #     book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
# #     student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
# #     issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    
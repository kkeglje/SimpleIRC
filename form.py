from flask_wtf import Form
from wtforms import TextField,SubmitField,validators,PasswordField,ValidationError

class RegistrationForm(Form):
    """Registration class with validators"""
    email = TextField('Enter email',[validators.email('Please enter email')])
    username = TextField('Enter username',[validators.Required('Please enter username')])
    password = PasswordField('Enter your password')
    rpassword = PasswordField('Confirm your password') 
    submit = SubmitField('Send')

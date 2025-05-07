from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, DateField, DecimalField, TextAreaField
from wtforms.validators import Length, NumberRange, EqualTo, DataRequired, ValidationError, Optional
from datetime import date
from aadhar import validate as vd
from dateutil.relativedelta import relativedelta
from function import pass_hash
import mysql.connector
from flask_login import current_user

mydb = mysql.connector.connect(host="localhost", user="bank_user", password="secure_password", database="virtual_banking")
cursor = mydb.cursor()


def validate_aadhar(form, field):
    if not vd(field.data):
        raise ValidationError(message="Invalid Aadhar number")


def validate_date(form, field):
    if field.data > (date.today()-relativedelta(years=18)):
        raise ValidationError(message="You must be 18 years old to open a bank account")


def validate_pass(form, field):
    password = field.data
    if len(password) < 8:
        raise ValidationError(message='Password must be longer than 8 characters.')
    elif password.islower():
        raise ValidationError(message='Password must contain an uppercase letter.')
    elif not (any(i.isdigit()) for i in password):
        raise ValidationError(message='Password must contain at least 1 digit.')


def validate_m_status(form, field):
    if field.data == 'Married' or field.data == 'Single':
        pass
    else:
        raise ValidationError('Select an appropriate option.')


def validate_e_status(form, field):
    if field.data == 'Employed' or field.data == 'Unemployed':
        pass
    else:
        raise ValidationError('Select an appropriate option.')


def validate_type_of_account(form, field):
    if field.data == 'Savings' or field.data == 'Current':
        pass
    else:
        raise ValidationError('Select an appropriate option.')


def validate_user_id(form, field):
    cursor.execute("select user_id from user_details where user_id = {}".format(field.data))
    global user_id, test
    test = 0
    data = cursor.fetchone()
    if data is not None:
        user_id = data
        test = 1
    else:
        raise ValidationError(message='No such user found.')


def validate_password(form, field):
    if test == 1:
        cursor.execute("select password from user_details where user_id = {}".format(user_id[0]))
        data = cursor.fetchone()
        data = data[0]
        if data == pass_hash(field.data):
            pass
        else:
            raise ValidationError(message='Enter a correct password.')

def validate_loan_interest(form, field):
    if field.data == '16%':
        pass
    else:
        raise ValidationError('Select an appropriate option.')

def validate_loan_type(form, field):
    if field.data == 'Personal Loan' or field.data == 'Home Loan' or field.data == 'Car Loan':
        pass
    else:
        raise ValidationError('Select an appropriate option.')

def validate_type_of_transaction(form, field):
    if field.data == 'Withdraw' or field.data == 'Deposit':
        pass
    else:
        raise ValidationError('Select an appropriate option.')


class register_form(FlaskForm):
    name = StringField(validators=[Length(min=3, max=30, message='Length of name must be between 3 to 30 characters.'), DataRequired(message='Enter an appropriate name.')])
    father_name = StringField(validators=[Length(min=3, max=30, message='Length of name must be between 3 to 30 characters.'), DataRequired(message='Enter an appropriate name.')])
    mother_name = StringField(validators=[Length(min=3, max=30, message='Length of name must be between 3 to 30 characters.'), DataRequired(message='Enter an appropriate name.')])
    aadhar_number = IntegerField(validators=[DataRequired(message='Enter an aadhar number.'), validate_aadhar])
    address = StringField(validators=[Length(min=10, max=60, message='Length of address must be between 3 to 30 characters.'), DataRequired(message='Enter an appropriate address.')])
    type_of_account = SelectField(choices=['Choose...', 'Savings', 'Current'], default='Choose...', validators=[DataRequired(), validate_type_of_account])
    dob = DateField(format='%Y-%m-%d', validators=[DataRequired(message='Enter an appropriate date.'), validate_date])
    marital_status = SelectField(choices=['Choose...', 'Married', 'Single'], default='Choose...', validators=[DataRequired(), validate_m_status])
    employment_status = SelectField(choices=['Choose...', 'Employed', 'Unemployed'], default='Choose...', validators=[DataRequired(), validate_e_status])
    pass_input = PasswordField(validators=[DataRequired(message='Enter an appropriate password.'), validate_pass])
    pass_confirm = PasswordField(validators=[EqualTo('pass_input', message='Both passwords must match.')])
    submit = SubmitField("Create Account")


class transaction_form(FlaskForm):
    amount = IntegerField(validators=[DataRequired(message='Enter an amount')])
    type_of_transaction = SelectField(choices=['Choose...', 'Withdraw', 'Deposit'], validators=[DataRequired(), validate_type_of_transaction])
    password = PasswordField()
    submit = SubmitField(label='Submit')


class user_login_form(FlaskForm):
    user_id = IntegerField(validators=[DataRequired(message='Enter an user ID.'), validate_user_id])
    password = PasswordField(validators=[DataRequired(message='Enter a password'), Length(min=8, message='Password must be 8 characters long.'), validate_password])
    submit = SubmitField(label='Login')


class fd_form(FlaskForm):
    time_period = SelectField(choices=['Choose...', '333', '444', '555', '666'], default='Choose...', validators=[DataRequired(message='Select a valid data field.')])
    rate_of_interest = SelectField(choices=['Choose...', '7% per annum'], default='Choose...', validators=[DataRequired(message='Enter a valid rate of interest.')])
    amount = IntegerField(validators=[DataRequired(message='Enter a valid amount')])
    password = PasswordField(validators=[DataRequired(message='Enter a password to proceed.')])
    submit = SubmitField(label='Create new FD')


class close_account(FlaskForm):
    name = StringField(validators=[DataRequired(message='Enter a name')])
    aadhar_number = IntegerField(validators=[validate_aadhar])
    address = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField(label='Submit')

class loan_application(FlaskForm):
    loan_type = SelectField("Loan Type",
                            choices=["Choose...", "Personal Loan", "Home Loan", "Car Loan"],
                            default='Choose...',
                            validators=[DataRequired(), validate_loan_type])
    loan_amount = DecimalField("Loan Amount (INR)", validators=[DataRequired(), NumberRange(min=1)])
    tenure_months = IntegerField("Tenure (Months)", validators=[DataRequired(), NumberRange(min=1)])
    issue_date = DateField("Issue Date", validators=[DataRequired()])
    interest_rate = SelectField(
        "Interest Rate",
        choices=["Choose...","16%"],
        default='Choose...',
        validators=[DataRequired(), validate_loan_interest]
    )
    submit = SubmitField("Apply for Loan")
    

class FeedbackForm(FlaskForm):
    rating = IntegerField("Rating (1-5)", validators=[DataRequired(), NumberRange(min=1, max=5)])
    comments = TextAreaField("Comments (optional)")
    submit = SubmitField("Submit Feedback")


class TicketForm(FlaskForm):
    title = StringField('Issue Title', validators=[DataRequired()])
    description = TextAreaField('Describe the issue', validators=[DataRequired()])
    transaction_id = SelectField('Select Related Transaction (Optional)', choices=[], default=None, validators=[Optional()])
    priority = SelectField('Priority', choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], validators=[DataRequired()])
    submit = SubmitField('Submit Ticket')
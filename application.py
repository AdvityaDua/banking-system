import datetime
from flask import Flask, render_template, redirect, flash, request, url_for, Response
from forms import register_form, transaction_form, user_login_form, pass_hash, fd_form, close_account
from flask_login import LoginManager, login_user, UserMixin, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from function import register_new_user, withdraw_amount, deposit_amount, create_fd, check_fd_rd, calculate_interest, account_close
import mysql.connector
import razorpay
import random

mydb = mysql.connector.connect(host="localhost", user="advitya", password="320@Kshivaji", database="mydatabase")
my_cursor = mydb.cursor()

client = razorpay.Client(auth=("rzp_test_04ShHLE0GaoZng", "QVPNqTakCiZOcpbmQS5A0obZ"))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bf603aefb078ed6650460e3f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://host:abcd1234@localhost/mydatabase'
db = SQLAlchemy(app)
app.config['TESTING'] = False
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'user_login'
login_manager.login_message = 'Kindly Login to access this page.'
login_manager.login_message_category = 'info'


class user_details(db.Model, UserMixin):
    name = db.Column(db.String(length=20), nullable=False)
    age = db.Column(db.Integer(), nullable=False)
    father_name = db.Column(db.String(length=20), nullable=False)
    mother_name = db.Column(db.String(length=20), nullable=False)
    aadhar_number = db.Column(db.Integer(), nullable=False)
    address = db.Column(db.String(length=60), nullable=False)
    type_of_account = db.Column(db.String(length=10), nullable=False)
    dob = db.Column(db.Date())
    m_status = db.Column(db.String(length=10), nullable=False)
    e_status = db.Column(db.String(length=10), nullable=False)
    user_id = db.Column(db.Integer(), nullable=False, primary_key=True)
    password = db.Column(db.String(), nullable=False)
    current_balance = db.Column(db.Integer(), nullable=False, default=0)
    role = db.Column(db.String(length=5), nullable=False)

    def get_id(self):
        alternative_id = self.user_id
        return alternative_id

    def get_role(self):
        return self.role


class staff_details(db.Model, UserMixin):
    name = db.Column(db.String(length=20), nullable=False)
    age = db.Column(db.Integer(), nullable=False)
    address = db.Column(db.String(length=60), nullable=False)
    dob = db.Column(db.Date())
    user_id = db.Column(db.Integer(), nullable=False, primary_key=True)
    password = db.Column(db.String(), nullable=False)
    role = db.Column(db.String(length=5), nullable=False)

    def get_id(self):
        return self.user_id

    def get_role(self):
        return self.role


@login_manager.user_loader
def load_user(user_id):
    return user_details.query.get(int(user_id))


@app.route('/')
@app.route('/home')
def home():
    if current_user.is_authenticated:
        return redirect('/main_menu')
    return render_template('home.html')


@app.route('/new_user_registration', methods=["GET", "POST"])
def new_user():
    if current_user.is_authenticated:
        return redirect('/main_menu')
    else:
        form = register_form()
        if form.validate_on_submit():
            user_id = register_new_user(mydb, my_cursor, form)
            attempted_user = user_details.query.get(user_id)
            login_user(attempted_user)
            flash(message=f'Account successfully created. Your user ID is {current_user.user_id}', category='success')
            return redirect('/main_menu')
        if form.errors != {}:
            for error in form.errors.values():
                flash(error, category='danger')
        return render_template('new_user.html', form=form)


@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if current_user.is_authenticated:
        return redirect('/main_menu')
    else:
        form = user_login_form()
        if form.validate_on_submit():
            attempted_user = user_details.query.get(form.user_id.data)
            login_user(attempted_user)
            flash(message='Login Successful.', category='success')
            return redirect('/main_menu')
        if form.errors != {}:
            for error in form.errors.values():
                flash(error, category='danger')
        return render_template('user_login.html', form=form)


@app.route('/official_login', methods=['GET', 'POST'])
def official_login():
    if current_user.is_authenticated:
        return redirect('/main_menu')
    else:
        return render_template('official_login.html')


@app.route('/main_menu')
@login_required
def main_menu():
    user = user_details.query.get(current_user.user_id)
    return render_template('main_menu.html', user=user)


@app.route('/main_menu/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, age=current_user.age, father_name=current_user.father_name, mother_name=current_user.mother_name, aadhar_number=current_user.aadhar_number, address=current_user.address, type_of_account=current_user.type_of_account, user_id=current_user.user_id)


@app.route('/main_menu/transaction', methods=['POST', 'GET'])
@login_required
def perform_a_transaction():
    form = transaction_form()
    if form.validate_on_submit():
        if form.password.data == '':
            flash(message='Enter a password.', category='danger')
        else:
            if pass_hash(form.password.data) != current_user.password:
                flash(message='Incorrect password. Try again.', category='danger')
            else:
                if form.type_of_transaction.data == 'Withdraw':
                    if form.amount.data > current_user.current_balance:
                        flash(message='Low balance. Could not complete the transaction.', category='danger')
                    else:
                        withdraw_amount(user_id=current_user.user_id, current_balance=current_user.current_balance,
                                        form=form)
                        flash(message='Amount successfully withdrawn.', category='success')
                        return redirect('/main_menu')
                elif form.type_of_transaction.data == 'Deposit':
                    return redirect(url_for('make_payment', amount=form.amount.data))
    return render_template('perform_a_transaction.html', form=form, show='hidden', amount=0, id='00000000')


@app.route('/make_payment', methods=['GET', 'POST'])
def make_payment():
    amount = request.args.get('amount', None)
    global time_of_transaction
    time_of_transaction = datetime.datetime.now().strftime("%H:%M:%S")
    my_cursor.execute("insert into transaction_details(date, time, type_of_transaction, amount, user_id, status, current_balance) values('{}', '{}', 'Deposit', {}, {}, 'Failed', {})".format(datetime.date.today(), time_of_transaction, amount, current_user.user_id, current_user.current_balance))
    mydb.commit()
    data = {"amount": int(amount)*100, "currency": "INR", "receipt": str(random.randint(000000, 999999))}
    payment = client.order.create(data=data)
    return render_template('make_payment.html', payment=payment)


@app.route('/main_menu/transaction/verify_payment', methods=['POST', 'GET'])
@login_required
def verify_payment():
    if request.method == 'GET':
        return redirect('/main_menu')
    order_id = request.form['razorpay_order_id']
    payment_id = request.form['razorpay_payment_id']
    razorpay_signature = request.form['razorpay_signature']
    my_cursor.execute(f"update transaction_details set status = 'Pending', order_id = '{order_id}' where user_id = {current_user.user_id} and date = '{datetime.date.today()}' and time = '{time_of_transaction}'")
    if client.utility.verify_payment_signature({
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': razorpay_signature
    }):
        my_cursor.execute(f"select amount from transaction_details where user_id = {current_user.user_id} and date = '{datetime.date.today()}' and time =  '{time_of_transaction}'")
        data = my_cursor.fetchone()
        amount = data[0]
        updated_balance = current_user.current_balance + amount
        my_cursor.execute(f"update transaction_details set transaction_id = '{payment_id}', status='Success' where user_id = {current_user.user_id} and date = '{datetime.date.today()}' and time = '{time_of_transaction}'")
        my_cursor.execute("update user_details set current_balance = {} where user_id = {}".format(updated_balance, current_user.user_id))
        mydb.commit()
        flash(message='Transaction successful.', category='success')
        return redirect('/main_menu')
    return render_template('verify_payment.html')


@app.route('/main_menu/current_balance')
@login_required
def get_current_balance():
    current_balance = current_user.current_balance
    return render_template('current_balance.html', balance=current_balance)


@app.route('/main_menu/transaction_history')
@login_required
def history():
    my_cursor.execute(f'select date, time, type_of_transaction, amount, status from transaction_details where user_id = {current_user.user_id}')
    data = my_cursor.fetchall()
    data.sort(reverse=True)
    return render_template('transaction_history.html', data=data)


@app.route('/main_menu/fd', methods=['GET', 'POST'])
@login_required
def new_fd():
    form = fd_form()
    if form.validate_on_submit():
        if form.time_period.data == '333' or form.time_period.data == '444' or form.time_period.data == '555' or form.time_period.data == '666':
            if form.rate_of_interest.data == '7% per annum':
                if pass_hash(form.password.data) == current_user.password:
                    if form.amount.data < current_user.current_balance:
                        create_fd(form, id=current_user.user_id, balance=current_user.current_balance)
                        flash(message='Transaction successful. FD created successfully.', category='success')
                        return redirect('/main_menu')
                    else:
                        flash(message='Could not complete the request. Low account balance.', category='danger')
                else:
                    flash(message='Enter a correct password.', category='danger')
            else:
                flash(message='Please select an appropriate rate of interest.', category='danger')
        else:
            flash(message='Select an appropriate time period.', category='danger')
    return render_template('new_fd.html', form=form)


@app.route('/main_menu/interest')
@login_required
def interest():
    data = check_fd_rd(id=current_user.user_id)
    new_data = []
    for item in data:
        item = list(item)
        open_date = item[0]
        current_date = datetime.date.today()
        number_of_days = (current_date - open_date).days
        profit = calculate_interest(amount=item[2], time=number_of_days, rate=7)
        item.append(profit)
        new_data.append(item)
    return render_template('interest.html', data=new_data)


@app.route('/main_menu/close_account', methods=['POST', 'GET'])
@login_required
def cls():
    form = close_account()
    if form.validate_on_submit():
        if form.name.data == current_user.name:
            if form.aadhar_number.data == current_user.aadhar_number:
                if form.address.data == current_user.address:
                    if pass_hash(form.password.data) == current_user.password:
                        flash(message='Account successfully deleted.', category='success')
                        return redirect('/main_menu/close_account/close')
                    else:
                        flash(message='Enter a correct password.', category='danger')
                else:
                    flash(message='Enter a correct address.', category='danger')
            else:
                flash(message='Enter a valid aadhar number.', category='danger')
        else:
            flash(message='Enter a valid name.', category='danger')
    return render_template('close_account.html', form=form)


@app.route('/main_menu/close_account/close')
@login_required
def close():
    account_close(current_user.user_id)
    logout_user()
    return redirect('/home')


@app.route('/logout_page')
@login_required
def logout():
    logout_user()
    return redirect('/home')


@app.route('/official/dashboard')
@login_required
def official_dashboard():
    if current_user.role == 'official':
        return render_template('official_dashboard.html')
    else:
        flash(message='You need to be an admin to access this page.', category='danger')
        return redirect('/main_menu')

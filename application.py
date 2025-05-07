import datetime
from flask import Flask, render_template, redirect, flash, request, url_for, Response
from forms import register_form, transaction_form, user_login_form, pass_hash, fd_form, close_account, loan_application, FeedbackForm, TicketForm
from flask_login import LoginManager, login_user, UserMixin, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from function import register_new_user, withdraw_amount, create_fd, check_fd_rd, calculate_interest, account_close
import mysql.connector
import razorpay
import random

mydb = mysql.connector.connect(host="localhost", user="bank_user", password="secure_password", database="virtual_banking")
my_cursor = mydb.cursor()

client = razorpay.Client(auth=("rzp_test_04ShHLE0GaoZng", "QVPNqTakCiZOcpbmQS5A0obZ"))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bf603aefb078ed6650460e3f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://bank_user:secure_password@localhost/virtual_banking'
db = SQLAlchemy(app)
app.config['TESTING'] = False
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'user_login'
login_manager.login_message = 'Kindly Login to access this page.'
login_manager.login_message_category = 'info'

class user_details(db.Model, UserMixin):
    __tablename__ = 'user_details'

    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    father_name = db.Column(db.String(20), nullable=False)
    mother_name = db.Column(db.String(20), nullable=False)
    aadhar_number = db.Column(db.BigInteger, unique=True, nullable=False)
    address = db.Column(db.String(60), nullable=False)
    type_of_account = db.Column(db.String(10), nullable=False)
    dob = db.Column(db.Date)
    m_status = db.Column(db.String(10), nullable=False)
    e_status = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    current_balance = db.Column(db.Integer, nullable=False, default=0)

    def get_id(self):
        return self.user_id



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




@app.route('/main_menu')
@login_required
def main_menu():
    user = user_details.query.get(current_user.user_id)
    return render_template('main_menu.html', user=user)


@app.route('/main_menu/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, father_name=current_user.father_name, mother_name=current_user.mother_name, aadhar_number=current_user.aadhar_number, address=current_user.address, type_of_account=current_user.type_of_account, user_id=current_user.user_id)


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
        open_date = item[1]
        current_date = datetime.date.today()
        number_of_days = (current_date - open_date).days
        profit = calculate_interest(amount=int(item[3]), time=number_of_days, rate=7)
        item.append(profit)
        print(item)
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

from datetime import timedelta
from math import pow

@app.route('/main_menu/loans', methods=['POST', 'GET'])
@login_required
def loans():
    form = loan_application()
    if form.validate_on_submit():
        loan_type = form.loan_type.data
        loan_amount = form.loan_amount.data
        interest_rate_str = form.interest_rate.data
        tenure_months = form.tenure_months.data
        issue_date = form.issue_date.data

        # Validate amount based on loan type
        limits = {
            "Home Loan": 1000000,
            "Car Loan": 500000,
            "Personal Loan": 200000
        }

        if loan_type in limits and loan_amount > limits[loan_type]:
            flash(message='Loan amount exceeds the limit.', category='danger')
            return render_template("loans.html", form=form)

        try:
            user_id = current_user.user_id

            # Convert interest rate string to float
            annual_rate = 16 / 100 
            monthly_rate = annual_rate / 12

            # Calculate EMI
            P = int(loan_amount)
            R = monthly_rate
            N = tenure_months
            emi = (P * R * pow(1 + R, N)) / (pow(1 + R, N) - 1) if R > 0 else P / N
            emi = round(emi, 2)

            # Calculate closing date
            closing_date = issue_date + timedelta(days=30 * tenure_months)
            status = "Approved"

            # Update user's balance: Assume loan amount is disbursed to user
            my_cursor.execute("SELECT current_balance FROM user_details WHERE user_id = %s", (user_id,))
            current_balance = my_cursor.fetchone()[0]
            updated_balance = current_balance + loan_amount

            my_cursor.execute("UPDATE user_details SET current_balance = %s WHERE user_id = %s", (updated_balance, user_id))
            
            sql = """INSERT INTO loan_records (
                        loan_type, loan_amount, interest_rate, tenure_months,
                        issue_date, closing_date, status, user_id, monthly_emi
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (
                loan_type, loan_amount, interest_rate_str, tenure_months,
                issue_date, closing_date, status, user_id, emi
            )
            my_cursor.execute(sql, values)
            
            transaction_sql = """
                INSERT INTO transaction_details (
                    user_id, date, time, type_of_transaction, amount,
                    current_balance
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """

            transaction_values = (
                user_id,
                datetime.date.today(),
                datetime.datetime.now().strftime("%H:%M:%S"),
                "Loan Deposit",
                int(loan_amount),
                updated_balance,
            )

            my_cursor.execute(transaction_sql, transaction_values)

            mydb.commit()
            flash(message='Loan application submitted successfully.', category='success')
            return redirect('/main_menu')

        except Exception as e:
            mydb.rollback()
            flash(message=f"Error while submitting loan: {str(e)}", category='danger')

    return render_template("loans.html", form=form)

@app.route('/main_menu/loan_history', methods=['GET'])
@login_required
def loan_history():
    user_id = current_user.user_id
    my_cursor.execute("SELECT * FROM loan_records WHERE user_id = %s", (user_id,))
    loan_data = my_cursor.fetchall()
    loan_data = list(loan_data)
    return render_template('loan_history.html', data=loan_data)

@app.route('/main_menu/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        user_id = current_user.user_id
        rating = form.rating.data
        comments = form.comments.data
        now = datetime.datetime.now()
        date = now.date()
        time = now.time()

        sql = """INSERT INTO feedback (user_id, date, time, rating, comments)
                 VALUES (%s, %s, %s, %s, %s)"""
        values = (user_id, date, time, rating, comments)
        
        try:
            my_cursor.execute(sql, values)
            mydb.commit()
            flash("Thank you for your feedback. We will work on improving our services." if rating <=3 else "Thank you for your positive feedback!", 'success')
            
            return redirect('/main_menu')
        except Exception as e:
            mydb.rollback()
            flash(f"Error submitting feedback: {str(e)}", 'danger')

    # Fetch submitted feedbacks
    my_cursor.execute("SELECT date, time, rating, comments FROM feedback ORDER BY date DESC, time DESC")
    feedback_data = my_cursor.fetchall()
    feedback_data = list(feedback_data)
    print(feedback_data)
    return render_template('feedback.html', form=form, feedback_data=feedback_data)

@app.route('/main_menu/ticket', methods=['GET', 'POST'])
@login_required
def submit_ticket():
    

    # Fetch the user's transactions
    my_cursor.execute("""
        SELECT id, amount, date FROM transaction_details WHERE user_id = %s
    """, (current_user.user_id,))
    transactions = my_cursor.fetchall()

    # Prepare choices for the transaction_id SelectField
    transaction_choices = [(str(txn[0]), f"ID: {txn[0]} | ₹{txn[1]} | {txn[2]}") for txn in transactions]
    
    form = TicketForm()
    form.transaction_id.choices = [(None, 'None')] + transaction_choices  # Add 'None' as an option

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        transaction_id = form.transaction_id.data
        priority = form.priority.data

        # If no transaction selected, set transaction_id to None
        if transaction_id == 'None':
            transaction_id = None

        my_cursor.execute("""
            INSERT INTO tickets (user_id, transaction_id, title, description, priority, status, date_submitted)
            VALUES (%s, %s, %s, %s, %s, 'Open', CURDATE())
        """, (current_user.user_id, transaction_id, title, description, priority))
        mydb.commit()

        flash('Ticket submitted successfully!', 'success')
        return redirect('/main_menu')

    return render_template('submit_ticket.html', form=form)

@app.route('/main_menu/view_tickets', methods=['GET'])
@login_required
def view_tickets():
    
    query = '''
        SELECT id, user_id, transaction_id, title, description, priority, status, date_submitted, last_updated 
        FROM tickets 
        WHERE user_id = %s
        ORDER BY last_updated DESC
    '''
    parameters = (current_user.user_id,)
    my_cursor.execute(query, parameters)
    tickets = my_cursor.fetchall()

    return render_template('view_tickets.html', tickets=tickets)

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


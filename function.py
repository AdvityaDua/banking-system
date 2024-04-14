import datetime
import random
import hashlib
import mysql.connector
from datetime import datetime as dt
from datetime import timedelta

mydb = mysql.connector.connect(host="localhost", user="advitya", password="320@Kshivaji", database="mydatabase")
my_cursor = mydb.cursor()


def pass_hash(password):
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    return password


def register_new_user(mydb, cursor, form):
    def user_id_generation(type_of_account, e_status, cursor):
        type_of_account = type_of_account.lower()
        e_status = e_status.lower()
        user_id = "2125"
        if type_of_account == "savings":
            user_id = user_id + "001"
        elif type_of_account == "current":
            user_id = user_id + "002"
        if e_status == "employed":
            user_id = user_id + "212"
        elif e_status == "unemployed":
            user_id = user_id + "121"
        random_id = random.randint(0000, 9999)
        random_id = str(random_id)
        user_id = user_id + random_id
        user_id = int(user_id)
        cursor.execute("select user_id from user_details where user_id = {}".format(user_id))
        data = cursor.fetchall()
        if data:
            user_id_generation(type_of_account, e_status, cursor)
        else:
            return user_id

    name = form.name.data
    age = form.age.data
    father_name = form.father_name.data
    mother_name = form.mother_name.data
    aadhar_number = form.aadhar_number.data
    address = form.address.data
    type_of_account = form.type_of_account.data
    dob = form.dob.data
    m_status = form.marital_status.data
    e_status = form.employment_status.data
    user_id = user_id_generation(type_of_account, e_status, cursor)
    password = pass_hash(form.pass_input.data)
    current_balance = 0
    role = 'user'
    sql = "INSERT INTO user_details (name, age, father_name, mother_name, aadhar_number, address, type_of_account, dob, m_status, e_status, user_id, password, current_balance, role) VALUES ('{}',{},'{}','{}',{},'{}','{}','{}','{}','{}', {}, '{}', {}, '{}')".format(
        name, age, father_name, mother_name, aadhar_number, address, type_of_account, dob, m_status, e_status, user_id,
        password, current_balance, role)
    cursor.execute(sql)
    mydb.commit()
    return user_id


def withdraw_amount(user_id, current_balance, form):
    date = dt.today().strftime("%Y-%m-%d")
    time = dt.now().strftime("%H:%M:%S")
    updated_balance = current_balance - form.amount.data
    # noinspection PyUnboundLocalVariable
    sql = "insert into transaction_details(date, time, type_of_transaction, amount, user_id, status, current_balance) values('{}', '{}', '{}', {}, {}, 'Success', {})".format(
        date, time, form.type_of_transaction.data, form.amount.data, user_id, updated_balance)
    my_cursor.execute(sql)
    my_cursor.execute(f"update user_details set current_balance = {updated_balance} where user_id = {user_id}")
    mydb.commit()


def deposit_amount(user_id, current_balance, amount):
    date = dt.today().strftime("%Y-%m-%d")
    time = dt.now().strftime("%H:%M:%S")
    updated_balance = current_balance + amount
    # noinspection PyUnboundLocalVariable
    sql = "insert into transaction_details(date, time, type_of_transaction, amount, current_balance, user_id) values('{}', '{}', 'deposit', {}, {}, {})".format(
        date, time, amount, updated_balance, user_id)
    my_cursor.execute(sql)
    my_cursor.execute("update user_details set current_balance = {} where user_id = {}".format(updated_balance, user_id))
    mydb.commit()


def create_fd(form, id, balance):
    date = datetime.date.today()
    time = dt.now().strftime("%H:%M:%S")
    number_of_days = int(form.time_period.data)
    amount = int(form.amount.data)
    rate_of_interest = form.rate_of_interest.data
    closing_date = date + timedelta(days=number_of_days)
    my_cursor.execute(
        "insert into fd_records(date_of_opening, number_of_days, invested_amount, rate_of_interest, closing_date, user_id) values('{}', {}, {}, '{}', '{}', {})".format(
            date, number_of_days, amount, rate_of_interest, closing_date, id))
    my_cursor.execute(f"update user_details set current_balance = {balance - amount} where user_id = {id}")
    my_cursor.execute(
        f"insert into transaction_details(date, time, type_of_transaction, amount, current_balance, user_id, status) values('{date}', '{time}', 'FD withdrawal', {amount}, {balance - amount}, {id}, 'Success')")
    mydb.commit()


def check_fd_rd(id):
    my_cursor.execute(f'select * from fd_records where user_id = {id}')
    data = my_cursor.fetchall()
    return data


def calculate_interest(amount, rate, time):
    profit = amount*pow((1 + rate/365), time/365)
    return '%.2f' % profit


def account_close(user_id):
    my_cursor.execute(f'delete from user_details where user_id = {user_id}')
    my_cursor.execute(f'delete from fd_records where user_id = {user_id}')
    my_cursor.execute(f'delete from transaction_details where user_id = {user_id}')
    mydb.commit()

CREATE TABLE user_details(
    user_id BIGINT PRIMARY KEY,
    name varchar(30) NOT NULL,
    father_name varchar(30) NOT NULL,
    mother_name varchar(30) NOT NULL,
    aadhar_number BIGINT UNIQUE NOT NULL,
    address varchar(60) NOT NULL,
    type_of_account varchar(10) NOT NULL CHECK (type_of_account IN ('Saving', 'Current')),
    dob DATE DEFAULT NULL,
    m_status varchar(10) NOT NULL CHECK (m_status IN ('Married', 'Unmarried')),
    e_status varchar(10) NOT NULL CHECK (e_status IN ('Employed', 'Unemployed', 'Student')),
    password varchar(255) NOT NULL,
    current_balance INT NOT NULL DEFAULT 0
)



CREATE TABLE transaction_details(
    date DATE NOT NULL,
    time TIME NOT NULL,
    type_of_transaction varchar(30) DEFAULT NULL CHECK (type_of_transaction IN ('Deposit', 'Withdraw', 'FD Deposit', 'FD Withdrawal', 'Loan Deposit')),
    amount INT NOT NULL,
    user_id BIGINT NOT NULL,
    status varchar(10) NOT NULL DEFAULT 'Success',
    current_balance INT NOT NULL,
    order_id varchar(60) DEFAULT NULL,
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    transaction_id varchar(60) DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES user_details(user_id) ON DELETE CASCADE ON UPDATE CASCADE
)

CREATE TABLE fd_records(
    fd_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    date_of_opening DATE NOT NULL,
    number_of_days INT NOT NULL CHECK (number_of_days > 0),
    invested_amount decimal(12,2) NOT NULL CHECK (invested_amount > 0),
    rate_of_interest varchar(20) NOT NULL,
    closing_date DATE NOT NULL,
    user_id BIGINT NOT NULL,
    amount BIGINT DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES user_details(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
)


CREATE TABLE loan_records(
    loan_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    loan_type varchar(20) NOT NULL CHECK (loan_type IN ('Personal', 'Home', 'Car')),
    loan_amount decimal(12,2) NOT NULL CHECK (loan_amount > 0),
    interest_rate varchar(10) NOT NULL,
    tenure_months INT NOT NULL CHECK (tenure_months > 0),
    issue_date DATE NOT NULL,
    closing_date DATE NOT NULL,
    status varchar(15) NOT NULL,
    monthly_emi decimal(12,2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user_details(user_id) ON DELETE CASCADE ON UPDATE CASCADE
)


CREATE TABLE tickets(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    transaction_id INT DEFAULT NULL,
    title varchar(255) NOT NULL,
    description TEXT NOT NULL,
    priority ENUM('Low', 'Medium', 'High') NOT NULL,
    status ENUM('Open', 'In Progress', 'Resolved', 'Closed') NOT NULL DEFAULT 'Open',
    date_submitted DATE DEFAULT (CURDATE()),
    last_updated TIMESTAMP NULL DEFAULT (NOW()) ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_details(user_id),
    FOREIGN KEY (transaction_id) REFERENCES transaction_details(id)
)


CREATE TABLE feedback(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    date date NOT NULL,
    time time NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comments TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user_details(user_id) ON DELETE CASCADE ON UPDATE CASCADE
)
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_ENABLED'] = False
app.config['SESSION_PROTECTION'] = 'strong'
db = SQLAlchemy(app)

login_manager = LoginManager(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor = db.Column(db.String(100))
    food_item = db.Column(db.String(100))
    location = db.Column(db.String(100))
    submitter_username = db.Column(db.String(100))

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requested_item = db.Column(db.String(100))
    location = db.Column(db.String(100))
    submitter_username = db.Column(db.String(100))

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Successfully signed up. Please log in.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists. Please choose a different one.', 'error')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Successfully logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/')
def index():
    donations = Donation.query.all()
    requests = Request.query.all()
    return render_template('index.html', donations=donations, requests=requests)

@app.route('/donate', methods=['POST'])
def donate():
    donor = request.form['donor']
    food_item = request.form['food_item']
    location = request.form['location']
    submitter_username = current_user.username
    new_donation = Donation(donor=donor, food_item=food_item, location=location, submitter_username=submitter_username)
    db.session.add(new_donation)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/request', methods=['POST'])
def request_food():
    requested_item = request.form['requested_item']
    location = request.form['location']
    submitter_username = current_user.username
    new_request = Request(requested_item=requested_item, location=location, submitter_username=submitter_username)
    db.session.add(new_request)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit_donation/<int:donation_id>', methods=['GET', 'POST'])
def edit_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    if request.method == 'POST':
        donation.donor = request.form['donor']
        donation.food_item = request.form['food_item']
        donation.location = request.form['location']
        db.session.commit()
        flash('Donation updated successfully', 'success')
        return redirect(url_for('index'))
    return render_template('edit_donation.html', donation=donation)

@app.route('/delete_donation/<int:donation_id>', methods=['POST'])
def delete_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    db.session.delete(donation)
    db.session.commit()
    flash('Donation deleted successfully', 'success')
    return redirect(url_for('index'))

@app.route('/edit_request/<int:request_id>', methods=['GET', 'POST'])
def edit_request(request_id):
    request_item = Request.query.get_or_404(request_id)
    if request.method == 'POST':
        request_item.requested_item = request.form['requested_item']
        request_item.location = request.form['location']
        db.session.commit()
        flash('Request updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('edit_request.html', request_item=request_item)

@app.route('/delete_request/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    request_item = Request.query.get_or_404(request_id)
    db.session.delete(request_item)
    db.session.commit()
    flash('Request deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
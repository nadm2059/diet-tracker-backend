from flask_cors import CORS

CORS(app, supports_credentials=True)

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True
)
app.secret_key = os.getenv("SECRET_KEY", "your_secret")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diet.db'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from models import User, Meal
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user:
            flash("Username taken")
            return redirect(url_for('register'))
        hashed = generate_password_hash(request.form['password'])
        user = User(username=request.form['username'], password=hashed, calorie_goal=2000)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash("Invalid login")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        meal = Meal(name=request.form['meal'], calories=int(request.form['calories']),
                    timestamp=datetime.utcnow(), user_id=current_user.id)
        db.session.add(meal)
        db.session.commit()
    meals = Meal.query.filter_by(user_id=current_user.id).all()
    total = sum(meal.calories for meal in meals)
    remaining = current_user.calorie_goal - total
    return render_template('dashboard.html', meals=meals, total=total, remaining=remaining)

@app.route('/api/calorie_data')
@login_required
def calorie_data():
    meals = Meal.query.filter_by(user_id=current_user.id).all()
    data = {}
    for meal in meals:
        day = meal.timestamp.strftime('%Y-%m-%d')
        data[day] = data.get(day, 0) + meal.calories
    return jsonify({'dates': list(data.keys()), 'calories': list(data.values())})

if __name__ == "__main__":
    app.run()

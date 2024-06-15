from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os
import hashlib
import bleach
from config import Config
from models import db, User, Role, Book, Genre, Cover, BookGenre, Review
from forms import LoginForm, RegistrationForm, BookForm, ReviewForm

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для выполнения данного действия необходимо пройти процедуру аутентификации'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Невозможно аутентифицироваться с указанными логином и паролем')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    books = Book.query.order_by(Book.year.desc()).paginate(page, 10, False)
    next_url = url_for('index', page=books.next_num) if books.has_next else None
    prev_url = url_for('index', page=books.prev_num) if books.has_prev else None
    return render_template('index.html', books=books.items, next_url=next_url, prev_url=prev_url)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    reviews = Review.query.filter_by(book_id=book_id).all()
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    return render_template('book_detail.html', book=book, reviews=reviews, user_review=user_review)

def save_cover_file(file):
    filename = secure_filename(file.filename)
    md5_hash = hashlib.md5(file.read()).hexdigest()
    file.seek(0)  # Reset file pointer to the beginning after reading for hash calculation

    existing_cover = Cover.query.filter_by(md5_hash=md5_hash).first()
    if existing_cover:
        return existing_cover.id

    cover = Cover(filename=filename, mime_type=file.mimetype, md5_hash=md5_hash)
    db.session.add(cover)
    db.session.commit()
    
    cover_path = os.path.join(app.config['UPLOAD_FOLDER'], str(cover.id))
    file.save(cover_path)
    return cover.id

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if current_user.role.name != 'Administrator':
        flash('У вас недостаточно прав для выполнения данного действия.')
        return redirect(url_for('add_book'))
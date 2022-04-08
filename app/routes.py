import datetime
import os

from werkzeug.utils import secure_filename

from app import app
from flask import render_template, request, redirect, url_for, flash, Response, send_from_directory, current_app, \
    send_file

from app.forms import LoginForm, FragenForm
from app.models import User, Question

from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

required_ammound = 500

def add_user(username, password):
    user = User(username=username)
    exists = User.query.filter_by(username=username).first()
    if not exists:
        user.set_password(password)
        user.insert()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


@app.route("/")
def index():
    username = get_username_from_current_user()
    recent_ammound = len(Question.query.all())
    return render_template('home.html', recent_ammound=recent_ammound, required_ammound=required_ammound, username=username)


@app.route('/question/add')
def add_question():
    form = FragenForm()
    username = get_username_from_current_user()
    return render_template('add_question.html', title='Frage', form=form, username=username)


@app.route('/question/add', methods=["POST"])
def add_question_post():
    form = FragenForm()
    question = Question(form.frage.data, form.antwort.data, form.kategorie.data, form.name.data)
    question.insert()
    flash('added Question')
    return redirect(url_for("add_question_post"))


@app.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)


@app.route('/login', methods=['POST'])
def login_post():
    form = LoginForm()
    user_dummy = User.query.filter_by(username=form.username.data).first()
    if user_dummy is None or not user_dummy.check_password(form.password.data):
        flash('Invalid username or password')
        return redirect(url_for('login'))
    login_user(user_dummy, remember=form.remember_me.data)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('all_questions')
    return redirect(next_page)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('add_question'))


@app.route("/all_questions")
@login_required
def all_questions():
    username = get_username_from_current_user()
    questions = Question.query.all()
    return render_template('all_questions.html', title='Questions', username=username, questions=questions)


@app.route("/edit/<question_id>", methods=['GET'])
@login_required
def edit_question(question_id):
    aktuelle_frage = Question.query.filter_by(id=int(question_id)).first()
    form = FragenForm()
    first = []
    rest = []
    kategorien = form.kategorie.choices
    for kategorie in kategorien:
        if kategorie == aktuelle_frage.kategory:
            first = [kategorie]
        else:
            rest.append(kategorie)
    form.kategorie.choices = first + rest

    username = get_username_from_current_user()
    print(aktuelle_frage)
    return render_template('edit_question.html', title='Frage', form=form, username=username, aktuelle_frage=aktuelle_frage)


@app.route("/edit/<question_id>", methods=['POST'])
@login_required
def edit_question_post(question_id):
    form = FragenForm()
    aktuelle_frage = Question.query.filter_by(id=int(question_id)).first()
    aktuelle_frage.question = form.frage.data
    aktuelle_frage.answer = form.antwort.data
    aktuelle_frage.kategory = form.kategorie.data
    aktuelle_frage.username = form.name.data
    aktuelle_frage.save()
    return redirect(url_for("all_questions"))


@app.route("/delete/<question_id>", methods=['POST'])
@login_required
def delete_question_post(question_id):
    print(question_id)

    Question.query.filter_by(id=int(question_id)).first().delete()
    return redirect(url_for("all_questions"))


def get_username_from_current_user():
    if User.query.filter_by(id=current_user.get_id()).first():
        return User.query.filter_by(id=current_user.get_id()).first().username
    else:
        return None


@app.route("/download_all", methods=['GET'])
@login_required
def download_all():
    questions = Question.query.all()
    output = ""
    for question in questions:
        question_question = question.answer
        if question_question:
            question_question = question_question.replace("\n", "")
        question_answer = question.answer
        if question_answer:
            question_answer = question_answer.replace("\n", "")
        question_kategory = question.kategory
        if question_kategory:
            question_kategory = question_kategory.replace("\n", "")
        question_username = question.username
        if question_username:
            question_username = question_username.replace("\n", "")
        output = output + ("{};{};{};{};{}\n".format(question.id, question_question, question_answer, question_kategory, question_username))
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition":
                     "attachment; filename=fragen_export_" + str(datetime.datetime.now().timestamp())+ ".csv"})


@app.route("/download_db", methods=['GET'])
@login_required
def download_db():
    uploads = os.path.join(current_app.root_path, "app.db")
    return send_file(uploads, as_attachment=True)

@app.route("/uplaod", methods=["POST"])
def upload():
    print(request.files)
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    print(file)
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        file.close()
        ammount = 0
        with open(file_path, "r", encoding="utf-8", errors='replace') as file2:
            print("file red")
            for line in file2:
                new_line = line.split(";")
                if len(new_line) == 2:
                    question = Question(new_line[0], new_line[1], None, None)
                    question.insert()
                    ammount = ammount + 1
                    print("line")
                elif len(new_line) == 5:
                    question = Question(new_line[1], new_line[2], new_line[3], new_line[4])
                    question.insert()
                    ammount = ammount + 1
                    print("line")
            print()
        os.remove(file_path)
        flash("inserted " + str(ammount) + " Questions")
    return redirect(url_for('add_question'))



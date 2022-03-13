import datetime
import os

from app import app
from flask import render_template, request, redirect, url_for, flash, Response, send_from_directory, current_app, \
    send_file

from app.forms import LoginForm, FragenForm
from app.models import User, Question

from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


def add_user(username, password):
    user = User(username=username)
    exists = User.query.filter_by(username=username).first()
    if not exists:
        user.set_password(password)
        user.insert()


@app.route("/")
def index():
    username = get_username_from_current_user()
    return render_template('topnav.html', username=username)


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
        output = output + ("{};{};{};{};{}\n".format(question.id, question.question, question.answer, question.kategory, question.username))
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


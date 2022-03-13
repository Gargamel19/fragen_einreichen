import click
from flask.cli import with_appcontext
from app.extentions import db

@click.command(name='add_user')
@with_appcontext
@click.argument("name")
@click.argument("pw")
def add_user(name, pw):
    print("add_user")
    print(name, pw)
    from app import routes
    routes.add_user(name, pw)

# add_user name=fettarmqp, pw=passwort

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    print("create tables")
    from app import app
    print(app.config["SQLALCHEMY_DATABASE_URI"])
    db.create_all()


@click.command(name='create_test_tables')
@with_appcontext
def create_test_tables():
    print("create test tables")
    from app import app
    import app.config_test as config_test
    app.config["SQLALCHEMY_DATABASE_URI"] = config_test.SQLALCHEMY_DATABASE_URI
    db.create_all()
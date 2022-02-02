import os

import psycopg2
from flask import Flask, render_template, request, make_response
from flask_sqlalchemy import SQLAlchemy

import redis

app = Flask(__name__)

uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
	uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

db = SQLAlchemy(app)
r = redis.Redis(host='wild-meadow-7683.internal', port=6379, db=0, password='redis')


class Ingredient(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), nullable=False)
	color = db.Column(db.String(80), nullable=True)

	def __init__(self, name, color):
		self.name = name
		self.color = color

	def __str__(self):
		return f"Ingredient #{self.id} | {self.color} {self.name}"


@app.route('/')
def home():
	r.incr('counter')
	out = ''
	for i in Ingredient.query.all():
		out += str(i)
	return f'{out}<a href="/addperson"><button> Click here </button></a> <p>{int(r.get("counter"))} visits today.'


@app.route("/addperson")
def addperson():
	return render_template("index.html")


@app.before_first_request
def first():
	r.set('visits', 0)
	with app.app_context():
		db.drop_all()  # warning: every time you redeploy, you'll reset your database! Included here for simplicity.
		db.create_all()
		db.session.commit()

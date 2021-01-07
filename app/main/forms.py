from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, widgets, IntegerField, validators, HiddenField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired

class KnownForm(FlaskForm):
    known = SubmitField(label='Known')
    blurry = SubmitField(label='Blurry')
    unknown = SubmitField(label='Unknown')
    noshow = SubmitField(label='No show')
    query = SubmitField(label='Query')
    exit = SubmitField()
    check = BooleanField('Show Sentence')

class SentenceKnownForm(FlaskForm):
    known = SubmitField(label='Known')
    blurry = SubmitField(label='Blurry')
    unknown = SubmitField(label='Unknown')
    noshow = SubmitField(label='No show')
    query = SubmitField(label='Query')
    exit = SubmitField()
    check = BooleanField('Show Sentence')

class ImportsForm(FlaskForm):
    importfolder = SubmitField(label="Import folder")
    exit = SubmitField()

class TryingForm(FlaskForm):
    check = BooleanField('check')
    index = StringField()
    submit = SubmitField()
    exit = SubmitField()

class QueryForm(FlaskForm):
    querystring = StringField(label='Word')
    submit = SubmitField()
    exit = SubmitField()





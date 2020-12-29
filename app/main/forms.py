from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, widgets, IntegerField, validators, HiddenField, SelectMultipleField
from wtforms.validators import DataRequired

class KnownForm(FlaskForm):
    known = SubmitField(label='Known')
    blurry = SubmitField(label='Blurry')
    unknown = SubmitField(label='Unknown')
    noshow = SubmitField(label='No show')
    query = SubmitField(label='Query')
    exit = SubmitField()

class ImportsForm(FlaskForm):
    importfolder = SubmitField(label="Import folder")
    exit = SubmitField()

class TryingForm(FlaskForm):
    index = StringField()
    submit = SubmitField()
    exit = SubmitField()

class QueryForm(FlaskForm):
    querystring = StringField(label='Word')
    submit = SubmitField()
    exit = SubmitField()





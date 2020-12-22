from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, widgets, IntegerField, validators, HiddenField, SelectMultipleField
from wtforms.validators import DataRequired

class KnownForm(FlaskForm):
    known = SubmitField(label='Known')
    blurry = SubmitField(label='Blurry')
    unknown = SubmitField(label='Unknown')
    noshow = SubmitField(label='No show')
    exit = SubmitField()

class ImportsForm(FlaskForm):
    # name = StringField("What's your name?",validators=[DataRequired()])
    # select_file = SelectMultipleField(choices=['a','b','c'])
    importdict = SubmitField(label="Import dictionary")
    exit = SubmitField()

class TryingForm(FlaskForm):
    index = StringField()
    submit = SubmitField()
    exit = SubmitField()





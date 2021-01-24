from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, widgets, SelectField, \
    BooleanField, FieldList, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Length

class KnownForm(FlaskForm):
    known = SubmitField(label='Known')
    blurry = SubmitField(label='Blurry')
    unknown = SubmitField(label='Unknown')
    noshow = SubmitField(label='No show')
    # query = SubmitField(label='Query')
    exit = SubmitField()
    check = BooleanField('Show Sentence')

class SentenceKnownForm(FlaskForm):
    known = SubmitField(label='Known')
    blurry = SubmitField(label='Blurry')
    unknown = SubmitField(label='Unknown')
    noshow = SubmitField(label='No show')
    repeat = SubmitField(label='Repeat')
    # query = SubmitField(label='Query')
    exit = SubmitField()
    show = BooleanField('Show translation')
    speed = SelectField(label='Speed',
                        choices=[('200','1x'),('100','0.5x'),('300','1.5x'),('400','2x'),('600','3x')],
                        validators=[DataRequired(), Length(1,64)])

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

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class UpdateMywordForm(FlaskForm):
    choices = MultiCheckboxField('Routes', coerce=int)
    submit = SubmitField("Update my word")
    exit = SubmitField("Exit")

class UpdateArticleShowForm(FlaskForm):
    choices = MultiCheckboxField('Routes', coerce=int)
    submit = SubmitField("Update article no show")
    exit = SubmitField("Exit")

class UpdateTextForm(FlaskForm):
    title = StringField('', validators=[DataRequired()])
    text = TextAreaField('',render_kw={'class': 'form-control', 'rows': 20}, validators=[DataRequired()])
    submit = SubmitField('Update')

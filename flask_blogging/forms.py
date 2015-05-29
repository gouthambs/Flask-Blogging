from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class BlogEditor(Form):
    title = StringField("title", validators=[DataRequired()])
    text = TextAreaField("text", validators=[DataRequired()])
    tags = StringField("tags", validators=[DataRequired()])
    submit = SubmitField("submit")

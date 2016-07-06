from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class BlogEditor(Form):
    title = StringField("title", validators=[DataRequired()])
    text = TextAreaField("text", validators=[DataRequired()])
    tags = StringField("tags", validators=[DataRequired()])
    draft = BooleanField("draft", default=False)
    submit = SubmitField("submit")

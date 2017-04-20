from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class BlogEditor(FlaskForm):
    title = StringField("title", validators=[DataRequired()])
    text = TextAreaField("text", validators=[DataRequired()])
    tags = StringField("tags", validators=[DataRequired()])
    draft = BooleanField("draft", default=False)
    submit = SubmitField("submit")

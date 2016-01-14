from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class BlogEditor(Form):
    title = StringField("title", validators=[DataRequired()])
    text = TextAreaField("text", validators=[DataRequired()])
    tags = StringField("tags", validators=[DataRequired()])
    draft = BooleanField("draft", default=False)
    seo_title = StringField("seo_title")
    seo_description = StringField("seo_description")
    submit = SubmitField("submit")

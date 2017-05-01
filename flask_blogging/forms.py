from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField,\
    FileField
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.validators import DataRequired


class BlogEditor(FlaskForm):
    title = StringField("title", validators=[DataRequired()])
    text = TextAreaField("text", validators=[DataRequired()])
    tags = StringField("tags", validators=[DataRequired()])
    draft = BooleanField("draft", default=False)
    submit = SubmitField("submit")


class UploadForm(FlaskForm):
    ALLOWED_EXTENSIONS = ["jpeg", "jpg", "png", "gif"]

    upload_name = StringField(
        'Name', validators=[DataRequired()],
        render_kw={"placeholder": "Images: " + ", ".join(ALLOWED_EXTENSIONS)})

    upload_img = FileField(
        validators=[FileRequired(),
                    FileAllowed(ALLOWED_EXTENSIONS, 'Images/gif`s only!')])

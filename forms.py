from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, EmailField
from wtforms.validators import DataRequired, email_validator, Length, Email


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField(
        'E-mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class UserEditForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    email = StringField(
        'E-mail', validators=[DataRequired()])
    image_url = StringField('(Optional) Image URL:')
    header_image_url = StringField('(Optional) Header Image URL:')
    bio = TextAreaField("Bio:")
    location = StringField("Location:")
    password = PasswordField('Current Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

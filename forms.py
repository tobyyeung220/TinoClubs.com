from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class EditClubForm(FlaskForm):
    name = StringField(render_kw={'readonly': True})
    aka = StringField(validators=[Length(max=20)])
    category = StringField(render_kw={'readonly': True})
    description_in_markdown = TextAreaField(validators=[DataRequired(), Length(max=5000)])
    meeting_time = StringField(validators=[DataRequired(), Length(max=100)])
    meeting_location = StringField(validators=[DataRequired(), Length(max=100)])
    tags_separated_by_comma = StringField(validators=[Length(max=100)])
    submit = SubmitField()

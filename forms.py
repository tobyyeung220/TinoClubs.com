from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, URL, NoneOf


REQUIRED = DataRequired()
LEN_100 = Length(max=100)


class EditClubForm(FlaskForm):
    name = StringField(render_kw={'readonly': True})
    aka = StringField(validators=[Length(max=20)])
    category = StringField(render_kw={'readonly': True})
    description_in_markdown = TextAreaField(validators=[REQUIRED, Length(max=5000)])
    meeting_time = StringField(validators=[REQUIRED])
    meeting_location = StringField(validators=[REQUIRED, LEN_100])
    tags_separated_by_comma = StringField(validators=[LEN_100])
    submit = SubmitField()


class LeadershipsForm(FlaskForm):
    advisor = StringField([REQUIRED, LEN_100])
    co_advisor = StringField(validators=[LEN_100])
    president = StringField(validators=[REQUIRED, LEN_100])
    co_president = StringField(validators=[LEN_100])
    secretary = StringField(validators=[[REQUIRED, LEN_100]])
    treasurer = StringField(validators=[[REQUIRED, LEN_100]])


class SocialMediasForm(FlaskForm):
    email_address = StringField(validators=[REQUIRED, Email(), Length(max=200)])
    discord_invite_link = StringField(validators=[LEN_100, URL()])
    instagram_profile_link = StringField(validators=[LEN_100, URL()])
    facebook_profile_link = StringField(validators=[LEN_100, URL()])
    youtube_profile_link = StringField(validators=[LEN_100, URL()])
    tiktok_profile_link = StringField(validators=[LEN_100, URL()])
    twitter_profile_link = StringField(validators=[LEN_100, URL()])
    linktree_link = StringField(validators=[LEN_100, URL()])

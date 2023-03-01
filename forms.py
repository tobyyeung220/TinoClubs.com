from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FormField
from wtforms.validators import DataRequired, Length, Email, URL


REQUIRED = DataRequired()
LEN_100 = Length(max=100)


class LeadershipsForm(FlaskForm):
    advisor_full_name = StringField([REQUIRED, LEN_100])
    co_advisor_full_name = StringField(validators=[LEN_100])
    president_full_name = StringField(validators=[REQUIRED, LEN_100])
    co_president_full_name = StringField(validators=[LEN_100])
    secretary_full_name = StringField(validators=[REQUIRED, LEN_100])
    treasurer_full_name = StringField(validators=[REQUIRED, LEN_100])


class SocialMediasForm(FlaskForm):
    email_address = StringField(validators=[REQUIRED, Email(), Length(max=200)])
    discord_invite_link = StringField(validators=[LEN_100, URL()])
    instagram_profile_link = StringField(validators=[LEN_100, URL()])
    facebook_profile_link = StringField(validators=[LEN_100, URL()])
    youtube_profile_link = StringField(validators=[LEN_100, URL()])
    tiktok_profile_link = StringField(validators=[LEN_100, URL()])
    twitter_profile_link = StringField(validators=[LEN_100, URL()])
    linktree_link = StringField(validators=[LEN_100, URL()])


class EditClubForm(FlaskForm):
    aka = StringField("Acronym(s)", validators=[Length(max=30)])
    description_in_markdown = TextAreaField("Club Description (Use the eye icon to preview your description. Use bullet points, emojis, bold, italic, and headings to make your description stand out!)",
                                            validators=[REQUIRED, Length(max=5000)],
                                            description='Max 5000 characters. Reach out to ASB if you need help with editing your description. Clubs with high quality description will be prioritized on TinoClubs.com')
    meeting_time = StringField(validators=[REQUIRED, LEN_100])
    meeting_location = StringField(validators=[REQUIRED, LEN_100])
    tags_separated_by_comma = StringField("Hashtags (please separate it by comma)", validators=[LEN_100],
                                          description="Example: #RecruitingNewMembers, #EveryoneCanJoin, #MeetingToday, #NoMeetingThisWeek, #OfficerApplicationOpen, #Fundraising")
    leaderships = FormField(LeadershipsForm)
    social_medias = FormField(SocialMediasForm)
    submit = SubmitField()

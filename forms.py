from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FormField
from wtforms.validators import DataRequired, Length, Email, URL
import json


REQUIRED = DataRequired()
LEN_100 = Length(max=100)


class LeadershipsForm(FlaskForm):
    advisor_full_name = StringField(validators=[REQUIRED, LEN_100])
    co_advisor_full_name = StringField("Co-Advisor Full Name (if applicable)", validators=[LEN_100])
    president_full_name = StringField(validators=[REQUIRED, LEN_100])
    co_president_full_name = StringField("Co-President Full Name (if applicable)", validators=[LEN_100])
    vice_president_1_full_name = StringField("Vice-President 1 Full Name", validators=[REQUIRED, LEN_100])
    vice_president_2_full_name = StringField("Vice-President 2 Full Name (if applicable)", validators=[LEN_100])
    vice_president_3_full_name = StringField("Vice-President 3 Full Name (if applicable)", validators=[LEN_100])
    secretary_full_name = StringField(validators=[REQUIRED, LEN_100])
    treasurer_full_name = StringField(validators=[REQUIRED, LEN_100], description="Treasurer can be the same person as the secretary")

    def fill(self, leaderships_in_json: str or None):
        leaderships = json.loads(leaderships_in_json or '[]')


class SocialMediasForm(FlaskForm):
    instagram_username = StringField(validators=[LEN_100, URL()])
    facebook_username = StringField(validators=[LEN_100, URL()])
    youtube_username = StringField(validators=[LEN_100, URL()])
    tiktok_username = StringField(validators=[LEN_100, URL()])
    twitter_username = StringField(validators=[LEN_100, URL()])
    discord_invite_code = StringField(validators=[LEN_100, URL()])
    linktree_link = StringField(validators=[LEN_100, URL()])

    def fill(self, social_medias_in_json: str or None):
        social_medias = json.loads(social_medias_in_json or '[]')
        for field in self._fields:
            platform_name = field.split('_')[0]
            possible_info = [media for media in social_medias if media['name'] == platform_name]
            if possible_info:
                getattr(self, field).data = possible_info[0]['text']


class EditClubForm(FlaskForm):
    aka = StringField("Acronym(s)", validators=[Length(max=30)])
    description_in_markdown = TextAreaField("Club Description (Use the eye icon to preview your description. Use bullet points, emojis, bold, italic, and headings to make your description stand out!)",
                                            validators=[REQUIRED, Length(max=5000)],
                                            description='Max 5000 characters. Reach out to ASB if you need help with editing your description. Clubs with high quality description will be prioritized on TinoClubs.com')
    email = StringField(validators=[REQUIRED, Email(), LEN_100])
    meeting_time = StringField(validators=[REQUIRED, LEN_100])
    meeting_location = StringField(validators=[REQUIRED, LEN_100])
    tags_separated_by_comma = StringField("Hashtags (separated by comma)", validators=[LEN_100],
                                          description="Example: #RecruitingNewMembers, #EveryoneCanJoin, #MeetingToday, #NoMeetingThisWeek, #OfficerApplicationOpen, #Fundraising")
    leaderships = FormField(LeadershipsForm)
    social_medias = FormField(SocialMediasForm)
    submit = SubmitField("Save All Changes")

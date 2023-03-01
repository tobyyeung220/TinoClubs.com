from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, ValidationError
import calendar
import json
from db import Club

VALID_ROLE_PREFIXES = {'advisor', 'president', 'vice', 'secretary', 'treasurer'}
VALID_SOCIAL_MEDIA = {'instagram', 'facebook', 'youtube', 'tiktok', 'twitter', 'discord', 'linktree'}


class EditClubInfoForm(FlaskForm):
    aka = StringField("Acronym(s)", validators=[Length(max=30)])
    tags_separated_by_comma = StringField("Hashtags (separated by comma)", validators=[Length(max=100)],
                                          description="Example: #RecruitingNewMembers, #EveryoneCanJoin, #MeetingToday, #NoMeetingThisWeek, #OfficerApplicationOpen, #Fundraising")
    email = StringField(validators=[DataRequired(), Email(), Length(max=100)])
    meeting_time = StringField(validators=[DataRequired(), Length(max=100)],
                               description="Example: Every Monday at lunch, Every other Tuesday after school, First Monday of the month")
    meeting_location = StringField(validators=[DataRequired(), Length(max=100)])
    description_in_markdown = TextAreaField(
        "Club Description (Use the eye icon to preview your description. Use bullet points, emojis, bold, italic, and headings to make your description stand out!)",
        validators=[Length(max=5000)],
        description='Max 5000 characters. Reach out to ASB if you need help with editing your description. Clubs with high quality description will be prioritized on TinoClubs.com')

    advisor_1_full_name = StringField(validators=[DataRequired(), Length(max=100)])
    advisor_2_full_name = StringField("Advisor 2 Full Name (optional)", validators=[Length(max=100)])
    president_1_full_name = StringField(validators=[DataRequired(), Length(max=100)])
    president_2_full_name = StringField("President 2 Full Name (optional)", validators=[Length(max=100)])
    vice_president_1_full_name = StringField("Vice President 1 Full Name (optional)", validators=[Length(max=100)])
    vice_president_2_full_name = StringField("Vice President 2 Full Name (optional)", validators=[Length(max=100)])
    vice_president_3_full_name = StringField("Vice President 3 Full Name (optional)", validators=[Length(max=100)])
    secretary_full_name = StringField(validators=[DataRequired(), Length(max=100)])
    treasurer_full_name = StringField(validators=[DataRequired(), Length(max=100)],
                                      description="Treasurer can be the same person as the secretary")

    instagram_username = StringField(validators=[Length(max=100)])
    facebook_username = StringField(validators=[Length(max=100)])
    youtube_username = StringField(validators=[Length(max=100)])
    tiktok_username = StringField(validators=[Length(max=100)])
    twitter_username = StringField(validators=[Length(max=100)])
    discord_invite_code = StringField(validators=[Length(max=100)])
    linktree_link = StringField(validators=[Length(max=100)])

    submit = SubmitField("Save all changes")

    def validate_meeting_time(self, field):
        days_of_week = [calendar.day_name[i] for i in range(7)]
        if not any(day.lower() in field.data.lower() for day in days_of_week):
            raise ValidationError(
                f"Please ensure your meeting time contains one of the following keywords: {', '.join(days_of_week)}")

    def register_leaderships(self, leaderships: list[dict]):
        for person in leaderships:
            field_name_prefix = person['role'].lower().replace(' ', '_')
            if hasattr(self, field_name_prefix + '_full_name') and not getattr(self,
                                                                               field_name_prefix + '_full_name').data:
                getattr(self, field_name_prefix + '_full_name').data = person['name']
            else:
                for i in range(1, 3):
                    if hasattr(self, f'{field_name_prefix}_{i}_full_name') and not getattr(self,
                                                                                           f'{field_name_prefix}_{i}_full_name').data:
                        getattr(self, f'{field_name_prefix}_{i}_full_name').data = person['name']
                        break

    @property
    def leaderships_in_json(self) -> str:
        leaderships = []
        for field in self._fields:
            if not any(field.startswith(prefix) for prefix in VALID_ROLE_PREFIXES):
                continue
            if field.startswith('vice'):
                role = 'Vice President'
            else:
                role = field.split('_')[0]
            name = getattr(self, field).data.strip()
            if not name:
                continue
            leaderships.append({'name': name, 'role': role.title()})
        return json.dumps(leaderships)

    def register_social_medias(self, social_medias: list[Club.SocialMedia]):
        for field in self._fields:
            platform_name = field.split('_')[0]
            if not any(platform == platform_name for platform in VALID_SOCIAL_MEDIA):
                continue
            possible_info = [media for media in social_medias if media.name == platform_name]
            if possible_info and not getattr(self, field).data:
                getattr(self, field).data = possible_info[0].text

    @property
    def social_medias_in_json(self) -> str:
        social_medias = []
        for field in self._fields:
            platform_name = field.split('_')[0]
            if not any(platform == platform_name for platform in VALID_SOCIAL_MEDIA):
                continue
            text = getattr(self, field).data.strip()
            if not text:
                continue
            social_medias.append({'name': platform_name, 'text': text})
        return json.dumps(social_medias)

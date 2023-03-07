from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, ValidationError
import calendar
import json
from db import Club, ClubCategory

VALID_ROLE_PREFIXES = {'advisor', 'president', 'vice', 'secretary', 'treasurer'}
VALID_SOCIAL_MEDIA = {'instagram', 'facebook', 'youtube', 'tiktok', 'twitter', 'discord', 'linktree'}


class EditClubInfoForm(FlaskForm):
    aka = StringField("Acronym", validators=[Length(max=30)])
    category = SelectField(validators=[DataRequired()],
                           choices=[(member.value, name.capitalize()) for name, member in ClubCategory.__members__.items()])
    tags_separated_by_comma = StringField("Hashtags (separated by comma)", validators=[Length(max=100)],
                                          description="Example: #RecruitingNewMembers, #EveryoneCanJoin, #MeetingToday, #NoMeetingThisWeek, #OfficerApplicationOpen, #Fundraising")
    email = StringField(validators=[DataRequired(), Email(), Length(max=100)])
    meeting_time = StringField(validators=[DataRequired(), Length(max=100)],
                               description="Example: Every Monday at lunch, Every other Tuesday after school, First Monday of the month")
    meeting_location = StringField(validators=[DataRequired(), Length(max=100)])
    description_in_markdown = TextAreaField("Club Description", validators=[Length(max=5000)],
        description='Max 5000 characters. Clubs with high quality description will automatically receive prioritized ranking on TinoClubs.com')

    leaderships_information = TextAreaField("Advisor(s) and Officers Information",
                                            validators=[DataRequired(), Length(max=1000)],
                                            description="Please make sure every advisor or officer is in its own line, "
                                                        "and each line follows the format of Role: Firstname Lastname")

    instagram_username = StringField(validators=[Length(max=100)])
    facebook_username = StringField(validators=[Length(max=100)])
    youtube_username = StringField(validators=[Length(max=100)])
    tiktok_username = StringField(validators=[Length(max=100)])
    twitter_username = StringField(validators=[Length(max=100)])
    discord_link = StringField(validators=[Length(max=100)])
    linktree_link = StringField(validators=[Length(max=100)])

    submit = SubmitField("Save all changes")

    def validate_meeting_time(self, field):
        days_of_week = [calendar.day_name[i] for i in range(7)]
        if not any(day.lower() in field.data.lower() for day in days_of_week):
            raise ValidationError(
                f"Please ensure your meeting time contains one of the following keywords: {', '.join(days_of_week)}")

    def validate_leaderships_information(self, field):
        try:
            leaderships = json.loads(self.leaderships_in_json)
        except Exception:
            raise ValidationError("Incorrect format. Please make sure every advisor or officer is in its own line, "
                                  "and each line follows the format of Role: Firstname Lastname")
        required_roles = ['advisor', 'president', 'secretary', 'treasurer']
        missing_roles = set()
        for role in required_roles:
            if not any(role in person['role'].lower() for person in leaderships):
                missing_roles.add(role)
        if missing_roles:
            raise ValidationError(f"Please provide information regarding: {', '.join(r.capitalize() for r in missing_roles)}")

    def register_leaderships(self, leaderships: list[dict]):
        self.leaderships_information.data = '\n'.join(f'{person["role"]}: {person["name"]}' for person in leaderships)
        self.leaderships_information.render_kw = {'rows': len(leaderships)}

    @property
    def leaderships_in_json(self) -> str:
        leaderships = []
        for line in self.leaderships_information.data.split('\n'):
            if not line:
                continue
            line = line.strip().replace('  ', ' ').replace(': ', ':')
            role, name = line.split(':')
            leaderships.append({'role': role.title(), 'name': name})
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

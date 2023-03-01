from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, ValidationError
import calendar
import json


class MyForm(FlaskForm):
    def __init__(self, prefix_name, *args, **kwargs):
        kwargs['prefix'] = prefix_name
        super().__init__(*args, **kwargs)
        assert hasattr(self, 'submit'), 'MyForm must have a "submit" attribute!'

    @property
    def string_field_names(self):
        return [f for f in self._fields if isinstance(getattr(self, f), StringField) and not f.startswith('csrf')]

    def validate_on_submit(self, extra_validators=None):
        return super().validate_on_submit(extra_validators) and self.submit.data


class EditBasicInfoForm(MyForm):
    def __init__(self, *args, **kwargs):
        super(EditBasicInfoForm, self).__init__(prefix_name='edit_basic_info', *args, **kwargs)

    aka = StringField("Acronym(s)", validators=[Length(max=30)])
    description_in_markdown = TextAreaField("Club Description (Use the eye icon to preview your description. Use bullet points, emojis, bold, italic, and headings to make your description stand out!)",
                                            validators=[DataRequired(), Length(max=5000)],
                                            description='Max 5000 characters. Reach out to ASB if you need help with editing your description. Clubs with high quality description will be prioritized on TinoClubs.com')
    email = StringField(validators=[DataRequired(), Email(), Length(max=100)])
    meeting_time = StringField(validators=[DataRequired(), Length(max=100)])
    meeting_location = StringField(validators=[DataRequired(), Length(max=100)])
    tags_separated_by_comma = StringField("Hashtags (separated by comma)", validators=[Length(max=100)],
                                          description="Example: #RecruitingNewMembers, #EveryoneCanJoin, #MeetingToday, #NoMeetingThisWeek, #OfficerApplicationOpen, #Fundraising")
    submit = SubmitField("Save Club Info Changes")

    def validate_meeting_time(self, field):
        days_of_week = [calendar.day_name[i] for i in range(7)]
        if not any(day.lower() in field.data.lower() for day in days_of_week):
            raise ValidationError(f"Please ensure your meeting time contains one of the following keywords: {', '.join(days_of_week)}")


class EditLeadershipsForm(MyForm):
    def __init__(self, *args, **kwargs):
        super(EditLeadershipsForm, self).__init__(prefix_name='edit_leaderships_info', *args, **kwargs)

    advisor_1_full_name = StringField(validators=[DataRequired(), Length(max=100)])
    advisor_2_full_name = StringField("Advisor 2 Full Name (if applicable)", validators=[Length(max=100)])
    president_1_full_name = StringField(validators=[DataRequired(), Length(max=100)])
    president_2_full_name = StringField("President 2 Full Name (if applicable)", validators=[Length(max=100)])
    vice_president_1_full_name = StringField("Vice President 1 Full Name", validators=[DataRequired(), Length(max=100)])
    vice_president_2_full_name = StringField("Vice President 2 Full Name (if applicable)", validators=[Length(max=100)])
    vice_president_3_full_name = StringField("Vice President 3 Full Name (if applicable)", validators=[Length(max=100)])
    secretary_full_name = StringField(validators=[DataRequired(), Length(max=100)])
    treasurer_full_name = StringField(validators=[DataRequired(), Length(max=100)], description="Treasurer can be the same person as the secretary")
    submit = SubmitField("Save Leadership Info Changes")

    def fill(self, leaderships: list[dict]):
        for person in leaderships:
            field_name_prefix = person['role'].lower().replace(' ', '_')
            if hasattr(self, field_name_prefix + '_full_name') and not getattr(self, field_name_prefix + '_full_name'):
                getattr(self, field_name_prefix + '_full_name').data = person['name']
            else:
                for i in range(1, 3):
                    if hasattr(self, f'{field_name_prefix}_{i}_full_name') and not getattr(self, f'{field_name_prefix}_{i}_full_name').data:
                        getattr(self, f'{field_name_prefix}_{i}_full_name').data = person['name']
                        break

    def to_json(self) -> str:
        ...


class EditSocialMediasForm(MyForm):
    def __init__(self, *args, **kwargs):
        super(EditSocialMediasForm, self).__init__(prefix_name='edit_social_medias_', *args, **kwargs)

    instagram_username = StringField(validators=[Length(max=100)])
    facebook_username = StringField(validators=[Length(max=100)])
    youtube_username = StringField(validators=[Length(max=100)])
    tiktok_username = StringField(validators=[Length(max=100)])
    twitter_username = StringField(validators=[Length(max=100)])
    discord_invite_code = StringField(validators=[Length(max=100)])
    linktree_link = StringField(validators=[Length(max=100)])
    submit = SubmitField("Save Social Media Changes")

    def fill(self, social_medias: list['SocialMedia']):
        for field in self.string_field_names:
            platform_name = field.split('_')[0]
            possible_info = [media for media in social_medias if media.name == platform_name]
            if possible_info and not getattr(self, field).data:
                getattr(self, field).data = possible_info[0].text

    def to_json(self):
        social_medias = []
        for field in self.string_field_names:
            platform_name = field.split('_')[0]
            text = getattr(self, field).data.strip()
            if not text:
                continue
            social_medias.append({'name': platform_name, 'text': text})
        return json.dumps(social_medias)

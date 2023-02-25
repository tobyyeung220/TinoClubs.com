import enum
import json
from flask_sqlalchemy import SQLAlchemy


class ClubCategory(enum.Enum):
    stem = 'stem'
    business = 'business'
    volunteering = 'volunteering'
    culture_and_identity = 'culture_and_identity'
    sports = 'sports'
    hobbies = 'hobbies'

    __display_names_mapping = {'stem': 'STEM & Technology', 'business': 'Business', 'volunteering': 'Volunteering',
                               'culture_and_identity': 'Culture & Identity', 'sports': 'Sports', 'hobbies': 'Hobbies'}

    @property
    def img(self):
        return f'/static/categories/{self.name}.png'

    @property
    def display_name(self):
        return ClubCategory.__display_names_mapping[self.value]


db = SQLAlchemy()  # "app: Flask" argument will be passed into later during main.py


class Club(db.Model):
    __tablename__ = 'club'
    name = db.Column(db.String, primary_key=True, index=True)
    aka = db.Column(db.String, index=True)  # can be null
    category = db.Column(db.Enum(ClubCategory), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)  # will be rendered as markdown
    meeting_time = db.Column(db.String, nullable=False)
    meeting_location = db.Column(db.String, nullable=False)
    raw_tags = db.Column(db.String, nullable=False, index=True)  # comma separated
    raw_social_medias = db.Column(db.String, nullable=False)  # JSON array; see admin.py for allowed values
    raw_leaderships = db.Column(db.String, nullable=False)  # JSON array; see admin.py for allowed values
    is_new = db.Column(db.Boolean, nullable=False, index=True)

    @property
    def tags(self) -> list[str]:
        return self.raw_tags.split()

    @property
    def social_medias(self) -> list[dict]:
        return json.loads(self.raw_social_medias)

    @property
    def leaderships(self) -> list[dict]:
        return json.loads(self.raw_leaderships)

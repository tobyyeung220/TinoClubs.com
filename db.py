import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import json


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
    class SocialMedia:
        def __init__(self, name: str, url: str, text: str):
            self.name = name
            self.url = url
            self.text = text

        @property
        def icon_url(self):
            return '/static/social_medias/' + self.name + '.png'

    __tablename__ = 'club'
    name = db.Column(db.String, primary_key=True, index=True, nullable=False)
    aka = db.Column(db.String, index=True)
    category = db.Column(db.Enum(ClubCategory), nullable=False, index=True)
    description = db.Column(db.Text)  # will be rendered as markdown
    meeting_time = db.Column(db.String, nullable=False)
    meeting_location = db.Column(db.String, nullable=False)
    raw_tags = db.Column(db.String, index=True)  # comma separated
    raw_social_medias = db.Column(db.String)  # JSON array; see admin.py for allowed values
    raw_leaderships = db.Column(db.String)  # JSON array; see admin.py for allowed values
    is_new = db.Column(db.Boolean, index=True)

    @property
    def tags(self) -> list[str]:
        return self.raw_tags.split()

    @property
    def social_medias(self) -> list[SocialMedia]:
        return [self.SocialMedia(**d) for d in json.loads(self.raw_social_medias or "[]")]

    @property
    def leaderships(self) -> list[dict]:
        return json.loads(self.raw_leaderships or "[]")

    @classmethod
    def create(cls, **kwargs):
        new_club = cls(**kwargs)
        db.session.merge(new_club)
        db.session.commit()


class GetClubNames:
    fulltext_matchable_fields = [Club.name, Club.aka, Club.category, Club.raw_tags]

    @staticmethod
    def reduce_to_scalar(func):
        def inner(*args, **kwargs):
            return [row[0] for row in func(*args, **kwargs)]
        return inner

    @classmethod
    @reduce_to_scalar
    def from_category(cls, category: ClubCategory, limit: int = None, offset=0) -> list[str]:
        if limit is not None:
            return Club.query.with_entities(Club.name).filter_by(category=category).limit(limit).offset(offset)
        return Club.query.with_entities(Club.name).filter_by(category=category)

    @classmethod
    @reduce_to_scalar
    def new_clubs(cls) -> list[str]:
        return Club.query.with_entities(Club.name).filter_by(is_new=True)

    @classmethod
    @reduce_to_scalar
    def from_search_query(cls, search_query: str) -> list[str]:
        return Club.query.with_entities(Club.name)\
            .filter(or_(*[field.like('%' + search_query + '%') for field in cls.fulltext_matchable_fields])).all()


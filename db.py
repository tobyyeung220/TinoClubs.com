import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func
import json
import markdown2


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
    description_in_markdown = db.Column(db.Text)
    meeting_time = db.Column(db.String, nullable=False)
    meeting_location = db.Column(db.String, nullable=False)
    tags_separated_by_comma = db.Column(db.String, index=True)
    social_medias_in_json = db.Column(db.String)  # visit /admin for acceptable data format
    leaderships_in_json = db.Column(db.String)  # visit /admin for acceptable data format
    is_new = db.Column(db.Boolean, index=True)

    @property
    def description(self) -> str:
        return markdown2.markdown(self.description_in_markdown)

    @property
    def tags(self) -> list[str]:
        return self.tags_separated_by_comma.split()

    @property
    def social_medias(self) -> list[SocialMedia]:
        return [self.SocialMedia(**d) for d in json.loads(self.social_medias_in_json or "[]")]

    @property
    def leaderships(self) -> list[dict]:
        return json.loads(self.leaderships_in_json or "[]")

    @classmethod
    def create(cls, **kwargs):
        new_club = cls(**kwargs)
        db.session.merge(new_club)
        db.session.commit()


class GetClubNames:
    fulltext_matchable_fields = [Club.name, Club.aka, Club.category, Club.tags_separated_by_comma]
    order_by_clauses = [Club.is_new.desc(), (func.length(Club.description_in_markdown) * func.length(Club.social_medias_in_json).desc())]

    @staticmethod
    def reduce_to_scalar(func):
        def inner(*args, **kwargs):
            return [row[0] for row in func(*args, **kwargs)]
        return inner

    @classmethod
    @reduce_to_scalar
    def from_category(cls, category: ClubCategory, limit: int = None, offset=0, exclude_name: str = None) -> list[str]:
        sql = Club.query.with_entities(Club.name).filter_by(category=category).order_by(*cls.order_by_clauses)
        if exclude_name:
            sql = sql.filter(Club.name != exclude_name)
        if limit is None:
            return sql
        return sql.limit(limit).offset(offset)

    @classmethod
    @reduce_to_scalar
    def new_clubs(cls) -> list[str]:
        return Club.query.with_entities(Club.name).filter_by(is_new=True)

    @classmethod
    @reduce_to_scalar
    def from_search_query(cls, search_query: str) -> list[str]:
        return Club.query.with_entities(Club.name) \
            .filter(or_(*[field.like('%' + search_query + '%') for field in cls.fulltext_matchable_fields]))\
            .order_by(*cls.order_by_clauses).all()

    @classmethod
    @reduce_to_scalar
    def random(cls, limit: int) -> list[str]:
        return Club.query.with_entities(Club.name).order_by(func.random()).limit(limit)

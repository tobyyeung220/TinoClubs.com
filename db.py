import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func
import json
import markdown2
from dataclasses import dataclass, asdict
from datetime import date
import calendar


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
            return '/static/social_medias/' + self.name + '.webp'

    __tablename__ = 'club'
    name = db.Column(db.String, primary_key=True, index=True, nullable=False)
    aka = db.Column(db.String, index=True)
    category = db.Column(db.Enum(ClubCategory), nullable=False, index=True)
    description_in_markdown = db.Column(db.Text)
    meeting_time = db.Column(db.String, nullable=False, index=True)
    meeting_location = db.Column(db.String, nullable=False)
    tags_separated_by_comma = db.Column(db.String, index=True)
    social_medias_in_json = db.Column(db.String)  # visit /admin for acceptable data format
    leaderships_in_json = db.Column(db.String)  # visit /admin for acceptable data format
    is_new = db.Column(db.Boolean, index=True)
    admin_password = db.Column(db.String, nullable=False)
    last_modified = db.Column(db.DateTime)

    @property
    def description(self) -> str:
        return markdown2.markdown(self.description_in_markdown or '')

    @property
    def tags(self) -> list[str]:
        return (self.tags_separated_by_comma or '').split()

    @property
    def social_medias(self) -> list[SocialMedia]:
        try:
            return [self.SocialMedia(**d) for d in json.loads(self.social_medias_in_json or "[]")]
        except json.JSONDecodeError:
            return []

    @property
    def leaderships(self) -> list[dict]:
        try:
            return json.loads(self.leaderships_in_json or "[]")
        except json.JSONDecodeError:
            return []

    @classmethod
    def create(cls, **kwargs):
        new_club = cls(**kwargs)
        db.session.merge(new_club)
        db.session.commit()


@dataclass
class ClubOverview:
    name: str
    category: ClubCategory
    aka: str
    meeting_location: str
    is_new: bool

    @property
    def hyphened_name(self):
        return self.name.replace(' ', '-')

    @property
    def thumb_url(self):
        return '/static/thumb/' + self.hyphened_name + '.jpg'

    @property
    def img_url(self):
        return '/static/club/' + self.hyphened_name + '.jpg'

    @property
    def page_url(self):
        return '/club/' + self.hyphened_name

    def dict(self):
        dict_data = asdict(self)
        dict_data['category'] = dict_data['category'].value
        return dict_data


class GetClubOverviews:
    fulltext_matchable_fields = [Club.name, Club.aka, Club.category, Club.tags_separated_by_comma]

    order_by_clauses = [Club.is_new.desc(), func.length(Club.description_in_markdown).desc()]

    @staticmethod
    def return_overviews(func):
        def inner(*args, **kwargs):
            return [ClubOverview(*row) for row in func(*args, **kwargs)]
        return inner

    @classmethod
    def sql_base(cls):
        return Club.query.with_entities(Club.name, Club.category, Club.aka, Club.meeting_location, Club.is_new)

    @classmethod
    @return_overviews
    def from_category(cls, category: ClubCategory, limit: int = None, offset=0, exclude_name: str = None):
        sql = cls.sql_base().filter_by(category=category).order_by(*cls.order_by_clauses)
        if exclude_name:
            sql = sql.filter(Club.name != exclude_name)
        if limit is None:
            return sql
        return sql.limit(limit).offset(offset)

    @classmethod
    @return_overviews
    def new_clubs(cls):
        return cls.sql_base().filter_by(is_new=True)

    @classmethod
    @return_overviews
    def meetings_today(cls):
        day_of_the_week = calendar.day_name[date.today().weekday()]
        return cls.sql_base().filter(Club.meeting_time.like('%every ' + day_of_the_week + '%')).order_by(*cls.order_by_clauses)

    @classmethod
    @return_overviews
    def meetings_today_or_next_week(cls):
        day_of_the_week = calendar.day_name[date.today().weekday()]
        return cls.sql_base().filter(
            Club.meeting_time.like('%' + day_of_the_week + '%') & Club.meeting_time.not_like('%every ' + day_of_the_week +'%')).order_by(*cls.order_by_clauses)

    @classmethod
    @return_overviews
    def from_search_query(cls, search_query: str):
        search_query = search_query.lower().strip()
        return cls.sql_base() \
            .filter(or_(*[field.like('%' + search_query + '%') for field in cls.fulltext_matchable_fields]))\
            .order_by(*cls.order_by_clauses).all()

    @classmethod
    @return_overviews
    def random(cls, limit: int):
        return cls.sql_base().order_by(func.random()).limit(limit)

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from db import Club


class ClubModelView(ModelView):
    column_display_pk = True
    column_editable_list = ['description', 'raw_tags', 'raw_social_medias']
    column_searchable_list = ['name', 'aka', 'description', 'meeting_time', 'meeting_location', 'raw_tags', 'raw_social_medias', 'raw_leaderships']
    column_filters = ['category', 'is_new']


def init_admin(app, db_session):
    tino_clubs_admin = Admin(app, name='Tino Clubs Admin', template_mode='bootstrap3')
    tino_clubs_admin.add_view(ClubModelView(Club, db_session, name="Manage Clubs"))

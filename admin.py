from flask_admin import Admin, expose, AdminIndexView
from flask import redirect
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from db import Club


class ClubModelView(ModelView):
    def __init__(self, model, *args, **kwargs):
        self.column_list = [c.key for c in model.__table__.columns]
        self.form_columns = self.column_list
        super(ClubModelView, self).__init__(model, *args, **kwargs)

    column_display_pk = True
    column_editable_list = ['description', 'raw_tags', 'raw_social_medias']
    column_searchable_list = ['name', 'aka', 'description', 'meeting_time', 'meeting_location', 'raw_tags', 'raw_social_medias', 'raw_leaderships']
    column_filters = ['category', 'is_new']
    column_descriptions = {
        'description': 'This will be rendered as markdown',
        'raw_tags': 'Please separate this field by comma with NO SPACE. Example: #Recruiting,#NewClub,#JoinNow',
        'raw_social_medias': 'Please follow a JSON array format of: [{"name": String, "url": String, "text": String}]'
                             '\nExample: [{"name": "instagram", "url": "https://instagram.com/iamjiamingliu", "text": "@iamjiamingliu"}, {"name": "email", "url": "mailto:jiamingliu888@gmail.com", "text": "jiamingliu888@gmail.com"}]'
                             '\n"name" can be: "instagram", "facebook", "discord", "email", "tiktok", "bereal", "linktree", "twitter", "youtube", "pinterest", "linkedin", "reddit", "twitch", "website"'
                             '\nIf "name" is "website", then the url should be the url of the club\' own website',
        'raw_leaderships': 'Please follow a JSON array format of: [{"name": String, "role": String}]'
                           '\nExample: [{"name": "Jiaming Liu", "role": "President"}]'
    }


class RedirectToClubDB(AdminIndexView):
    def is_visible(self):
        return False

    @expose('/')
    def index(self):
        return redirect('./club')


def init_admin(app, db_session):
    tino_clubs_admin = Admin(app, name='Tino Clubs Admin', template_mode='bootstrap3', index_view=RedirectToClubDB())
    tino_clubs_admin.add_view(ClubModelView(Club, db_session, name="Manage Clubs"))
    tino_clubs_admin.add_view(FileAdmin('./static/club', name='Manage Club Logos'))


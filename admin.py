from flask_admin import Admin, expose, AdminIndexView
from flask import redirect
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from db import Club
import os


class ClubModelView(ModelView):
    def __init__(self, model, *args, **kwargs):
        self.column_list = [c.key for c in model.__table__.columns]
        self.form_columns = self.column_list
        self.column_searchable_list = self.column_list
        self.column_filters = self.column_list
        super(ClubModelView, self).__init__(model, *args, **kwargs)

    can_export = True
    column_display_pk = True
    column_descriptions = {
        'name': 'Club name must NOT contain hyphen',
        'description_in_markdown': 'This will be rendered as markdown',
        'social_medias_in_json': 'Please follow a JSON array format of: [{"name": String, "url": String, "text": String}]'
                             '\nExample: [{"name": "instagram", "text": "@someclub"}, {"name": "discord", "text": "somediscordinvitelink"}]'
                             '\nname can be: instagram, discord, facebook, youtube, tiktok, twitter, linktree',
        'leaderships_in_json': 'Please follow a JSON array format of: [{"name": String, "role": String}]'
                           '\nExample: [{"name": "John Doe", "role": "President"}, {"name": "Billy Bob", "role": "Vice President"}]'
                               '\nrole can be: Advisor, President, Vice President, Secretary, Treasurer'
                               '\n2 advisors max, 2 presidents max, 3 vice presidents max, and 1 each for secretary and treasurer',
        'admin_password': 'Please let the club know that this is their admin password. They will need this to login and edit their own info.'
    }
    column_formatters = {'description_in_markdown': lambda v, c, m, p: m.description_in_markdown[:40] + ('...' if len(m.description_in_markdown) > 40 else '')
                        }


class RedirectToClubDB(AdminIndexView):
    def is_visible(self):
        return False

    @expose('/')
    def index(self):
        return redirect('./club')


class FileAdmin2(FileAdmin):
    ...


class FileAdmin3(FileAdmin):
    ...


def init_admin(app, db_session):
    tino_clubs_admin = Admin(app, name='Tino Clubs Admin', template_mode='bootstrap3', index_view=RedirectToClubDB())
    tino_clubs_admin.add_view(ClubModelView(Club, db_session, name="Manage Clubs"))
    tino_clubs_admin.add_view(FileAdmin('./static', name='Manage Static Assets'))


def assert_environ_are_valid():
    assert 'ADMIN_USERNAME' in os.environ, 'ADMIN_USERNAME not in environmental variables'
    assert 'ADMIN_PASSWORD' in os.environ, 'ADMIN_PASSWORD not in environmental variables'


def is_valid_admin_credentials(auth):
    return auth and auth.username == os.environ['ADMIN_USERNAME'] and auth.password == os.environ['ADMIN_PASSWORD']

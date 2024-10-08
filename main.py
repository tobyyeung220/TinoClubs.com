# To run development robustly, use:
# gunicorn -w 3 main:app --daemon
# And configure nginx to pass to 8000


from flask import Flask, render_template, request, session, redirect, flash, abort
from flask_bootstrap import Bootstrap5
import os
from datetime import date, datetime
import calendar
from db import db, ClubCategory, Club, GetClubOverviews, ClubOverview
from admin import init_admin, is_valid_admin_credentials, is_valid_club_credentials, assert_environ_are_valid
from forms import EditClubInfoForm


assert_environ_are_valid()

app = Flask(__name__)
app.secret_key = os.environ['ADMIN_PASSWORD']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['BOOTSTRAP_BTN_STYLE'] = 'warning'
Bootstrap5(app)

db.init_app(app)
with app.app_context():
    db.create_all()

init_admin(app)

HTTP_UNAUTHORIZED_RESPONSE = 'Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}


@app.before_request
def before_request():
    if request.path.startswith('/admin'):
        if not is_valid_admin_credentials(request.authorization):
            return HTTP_UNAUTHORIZED_RESPONSE
    if 'toggleDarkMode' in request.args:
        session['isDarkMode'] = not session.get('isDarkMode', False)
        return redirect(request.path)
    session.permanent = True


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e=e)


@app.route('/')
def home_page():
    total_clubs_cnt = Club.query.count()
    random_club_names = GetClubOverviews.random(10)  # for scrolling circular images
    recently_viewed = [ClubOverview(**d) for d in session.get('recently_viewed', [])]
    idx_of_today = date.today().weekday()
    if 0 <= datetime.now().hour <= 15:  # if today's school hasn't ended
        target_day_name = calendar.day_name[idx_of_today]
    else:  # today's school has ended, so show tomorrow's club meetings
        target_day_name = calendar.day_name[(idx_of_today + 1) % 7]
    return render_template('home.html', new_clubs=GetClubOverviews.new_clubs(), recently_viewed=recently_viewed,
                           total_clubs_cnt=total_clubs_cnt, random_club_names=random_club_names,
                           weekly_clubs_meeting=GetClubOverviews.weekly_meetings_on_the_day_of(target_day_name),
                           non_weekly_clubs_meeting=GetClubOverviews.non_weekly_meetings_on_the_day_of(target_day_name),
                           name_of_today=calendar.day_name[idx_of_today], target_day_name=target_day_name)


@app.route('/club/<hyphened_club_name>')
def club_page(hyphened_club_name: str):
    session.setdefault('recently_viewed', [])
    club_name = hyphened_club_name.replace('-', ' ')
    club = db.session.get(Club, club_name)
    if club is None:
        # removes it from recently viewed, in case this club was deleted recently
        session['recently_viewed'] = [history for history in session['recently_viewed'] if history['name'] != club_name]
        return abort(404, f"Sorry, \"{club_name}\" does not exist. Please check your spelling, or, the club might not exist at all.")
    current_overview = ClubOverview(club_name, club.category, club.aka, club.meeting_location, club.is_new)
    prev_overviews = [prev for prev in session['recently_viewed'] if prev['name'] != club_name]
    session['recently_viewed'] = [current_overview.dict()] + prev_overviews[:3]

    same_category_clubs = GetClubOverviews.from_category(club.category, limit=4, exclude_name=club_name)
    return render_template('club.html', club=club, overviews_of_same_category_clubs=same_category_clubs)


@app.route('/edit/<hyphened_club_name>', methods=['GET', 'POST'])
def edit_club_page(hyphened_club_name: str):
    club_name = hyphened_club_name.replace('-', ' ')
    club = db.get_or_404(Club, club_name,
                              description=f"Sorry, \"{club_name}\" does not exist. Please check your spelling, or, the club might not exist at all.")
    if not (is_valid_admin_credentials(request.authorization) or is_valid_club_credentials(request.authorization, club_name, club.admin_password)):
        return HTTP_UNAUTHORIZED_RESPONSE
    edit_form = EditClubInfoForm(obj=club)
    if edit_form.is_submitted():
        if edit_form.validate():
            for field_name, value in edit_form.data.items():
                if hasattr(club, field_name):
                    setattr(club, field_name, value)
            club.leaderships_in_json = edit_form.leaderships_in_json
            club.social_medias_in_json = edit_form.social_medias_in_json
            club.last_modified = datetime.now()
            db.session.commit()
            flash('Succesfully saved all changes', 'success')
            return redirect('/club/' + hyphened_club_name)
        else:
            flash('You have one or more errors. Please scroll down to see them.', 'danger')
    else:
        edit_form.register_leaderships(club.leaderships)
        edit_form.register_social_medias(club.social_medias)
    return render_template('edit.html', club=club, edit_form=edit_form)


@app.route('/explore')
def explore_page():
    clubs_of_category = {category: GetClubOverviews.from_category(category) for category in ClubCategory}
    return render_template('explore.html', ClubCategory=ClubCategory, clubs_of_category=clubs_of_category)


@app.route('/search', methods=['GET', 'POST'])
@app.route('/search/<search_query>')
def search_page(search_query: str = None):
    if request.method == 'POST':
        return redirect('/search/' + request.form.get('search_query'))
    return render_template('search.html', search_query=search_query,
                           matching_club_overviews=GetClubOverviews.from_search_query(search_query))


@app.route('/calendar')
def calendar_page():
    weekly_days = calendar.day_name[:5]
    clubs_meeting_on = {day: GetClubOverviews.all_meetings_on_the_day_of(day) for day in weekly_days}
    return render_template('calendar.html', weekly_days=weekly_days,
                           today=calendar.day_name[date.today().weekday()],
                           current_timestamp=datetime.now(),
                           clubs_meeting_on=clubs_meeting_on)


if __name__ == '__main__':
    app.run(debug=True, port=8000)

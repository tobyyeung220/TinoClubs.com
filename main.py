# To run development robustly, use:
# gunicorn -w 3 main:app --daemon
# And configure nginx to pass to 8000


from flask import Flask, render_template, request, session, redirect, flash, abort
from flask_bootstrap import Bootstrap5
import os
from datetime import date, datetime
import calendar
from db import db, ClubCategory, Club, GetClubOverviews, ClubOverview
from admin import init_admin, is_valid_admin_credentials, assert_environ_are_valid
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
    random_club_names = GetClubOverviews.random(10)
    recently_viewed = [ClubOverview(**d) for d in session.get('recently_viewed', [])]
    day_of_the_week = calendar.day_name[date.today().weekday()]
    return render_template('home.html', new_clubs=GetClubOverviews.new_clubs(), recently_viewed=recently_viewed,
                           total_clubs_cnt=total_clubs_cnt, random_club_names=random_club_names,
                           clubs_meeting_today=GetClubOverviews.meetings_today(), day_of_the_week=day_of_the_week,
                           clubs_meeting_today_or_next_week=GetClubOverviews.meetings_today_or_next_week())


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
    if not (request.authorization and request.authorization.username == club_name and request.authorization.password == club.admin_password):
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


if __name__ == '__main__':
    import smtplib
    import ssl
    from email.message import EmailMessage

    email_sender = 'tinoclubs@gmail.com'
    email_password = 'ozhuoxcurimddtve'

    subject = 'Introducing TinoClubs.com & Your Login Credentials'
    body = """Hi {club_name},

ASB has ditched the google spreadsheet on cupertinoasb.org/clubs. From now on and moving forward, your club will be featured on TinoClubs.com:
- A lot more information and features compared to the simple spreadsheet
- You can customize your club’s profile page on TinoClubs.com, anytime, anywhere

This is the link to your club’s profile page: {profile_link}
To edit your club’s profile page, click on the “Edit” yellow button, which should lead you to this page: {edit_link}

Your username is: {club_name}
Your password is: {edit_password} (if someday you forget or want to change your password, let us know)

Then the creativity is yours! A good profile page will help you attract more members and give you prioritized ranking on the website.

A few tips on making a good profile page:
1. Enrich the description section with bullet points, sub-headings, italics, and bold
2. FYI, the description uses a “markdown” syntax. If one of your officers took a CS class before, ask them. They have the knowledge to unlock the fullest potential for your description section.
3. Keep your social media and leadership info sections up-to-date

This is a new site, so we apologize in advance of any defects or bugs. If you have any feedback for TinoClubs.com, we’d love to hear!

Best Regards,
Clubs Commissioners
    """

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)

        with app.app_context():
            clubs = Club.query.all()
            for club in clubs:
                email_receiver = club.email
                em = EmailMessage()
                em['From'] = email_sender
                em['To'] = email_receiver
                em['Subject'] = subject
                em.set_content(body.format(club_name=club.name, profile_link='tinoclubs.com/club/' + club.name.replace(' ', '-'),
                                           edit_link='tinoclubs.com/edit/' + club.name.replace(' ', '-'),
                                           edit_password=club.admin_password))
                smtp.sendmail(email_sender, email_receiver, em.as_string())
                print(club.name)
    exit()
    app.run(debug=True, port=8000)

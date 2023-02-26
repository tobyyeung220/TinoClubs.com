from flask import Flask, render_template, request, session, redirect, url_for
import uuid
from db import db, ClubCategory, Club, GetClubNames
from admin import init_admin

app = Flask(__name__)
app.secret_key = uuid.uuid4().hex
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

init_admin(app, db.session)


@app.before_request
def before_request():
    if 'toggleDarkMode' in request.args:
        session['isDarkMode'] = not session.get('isDarkMode', False)
        return redirect(request.path)
    session.permanent = True


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e=e)


@app.route('/')
def home_page():
    return render_template('home.html', new_club_names=GetClubNames.new_clubs())


@app.route('/club/<hyphened_club_name>')
def club_page(hyphened_club_name: str):
    club_name = hyphened_club_name.replace('-', ' ')
    club_data = db.get_or_404(Club, club_name, description=f"Sorry, \"{club_name}\" does not exist. Please check your spelling, or, the club might not exist at all.")
    session.setdefault('recently_viewed', [])
    session['recently_viewed'] = [club_name] + [prev_club for prev_club in session['recently_viewed'] if
                                                prev_club != club_name][:7]
    return render_template('club.html', club=club_data,
                           names_of_same_category_clubs=GetClubNames.from_category(club_data.category, limit=4))


@app.route('/explore')
def explore_page():
    clubs_of_category = {category: GetClubNames.from_category(category) for category in ClubCategory}
    return render_template('explore.html', ClubCategory=ClubCategory, clubs_of_category=clubs_of_category)


@app.route('/search', methods=['GET', 'POST'])
@app.route('/search/<search_query>')
def search_page(search_query: str = None):
    if request.method == 'POST':
        return redirect('/search/' + request.form.get('search_query'))
    return render_template('search.html', search_query=search_query,
                           matching_club_names=GetClubNames.from_search_query(search_query))


if __name__ == '__main__':
    app.run(debug=True, port=8000)

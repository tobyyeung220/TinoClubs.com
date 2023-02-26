from flask import Flask, render_template, request, session, redirect
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


@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/club/<hyphened_club_name>')
def club_page(hyphened_club_name: str):
    club_name = hyphened_club_name.replace('-', ' ')
    session.setdefault('recently_viewed', [])
    session['recently_viewed'] = [club_name] + [prev_club for prev_club in session['recently_viewed'] if prev_club != club_name][:7]
    club_data = db.get_or_404(Club, club_name)
    return render_template('club.html', club=club_data,
                           names_of_same_category_clubs=GetClubNames.by_category(club_data.category, limit=4))


@app.route('/explore')
def explore_page():
    return render_template('explore.html', ClubCategory=ClubCategory)


@app.route('/search', methods=['GET', 'POST'])
@app.route('/search/<search_query>')
def search_page(search_query: str = None):
    return render_template('search.html')


if __name__ == '__main__':
    app.run(debug=True, port=8000)

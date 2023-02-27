from flask import Flask, render_template, request, session, redirect
import uuid
from db import db, ClubCategory, Club, GetClubOverviews, ClubOverview
from admin import init_admin, is_valid_admin_credentials, assert_environ_are_valid


assert_environ_are_valid()

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
    if request.path.startswith('/admin'):
        if not is_valid_admin_credentials(request.authorization):
            return 'Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}
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
    return render_template('home.html', new_clubs=GetClubOverviews.new_clubs(), recently_viewed=recently_viewed,
                           total_clubs_cnt=total_clubs_cnt, random_club_names=random_club_names)


@app.route('/club/<hyphened_club_name>')
def club_page(hyphened_club_name: str):
    club_name = hyphened_club_name.replace('-', ' ')
    club_data = db.get_or_404(Club, club_name,
                              description=f"Sorry, \"{club_name}\" does not exist. Please check your spelling, or, the club might not exist at all.")

    session.setdefault('recently_viewed', [])
    current_overview = ClubOverview(club_name, club_data.category, club_data.aka, club_data.is_new)
    prev_overviews = [prev for prev in session['recently_viewed'] if prev['name'] != club_name]
    session['recently_viewed'] = [current_overview.dict()] + prev_overviews[:7]

    same_category_clubs = GetClubOverviews.from_category(club_data.category, limit=4, exclude_name=club_name)
    return render_template('club.html', club=club_data, overviews_of_same_category_clubs=same_category_clubs)


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
    def minDistance(word1, word2):
        m = len(word1)
        n = len(word2)
        table = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            table[i][0] = i
        for j in range(n + 1):
            table[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if word1[i - 1] == word2[j - 1]:
                    table[i][j] = table[i - 1][j - 1]
                else:
                    table[i][j] = 1 + min(table[i - 1][j], table[i][j - 1], table[i - 1][j - 1])
        return table[-1][-1]

    import json
    from db import Club

    with app.app_context():
        all_club_names = [row[0] for row in Club.query.with_entities(Club.name).all()]

    for line in open('test.txt', 'r'):
        bracket_idx = line.index('[')
        wrong_club_name, leadership_list = line[:bracket_idx - 1], line[bracket_idx:]
        if wrong_club_name == 'Cupertino ASL Club':
            wrong_club_name = 'ASL'
        elif wrong_club_name == 'Tino Explore (STEAM Magazine) Club':
            wrong_club_name = 'Tino Explore'
        with app.app_context():
            acronyms_matchiin_clubs = Club.query.filter(Club.aka.like(f'%{wrong_club_name}%')).all()
        if wrong_club_name == 'Interact':
            actual_club_name = 'Cupertino Interact'
        elif acronyms_matchiin_clubs:
            actual_club_name = acronyms_matchiin_clubs[0].name
        else:
            actual_club_name = sorted(all_club_names, key=lambda n: minDistance(n, wrong_club_name))[0]
        # print(actual_club_name, wrong_club_name, json.loads(leadership_list))
        print(actual_club_name, wrong_club_name)
    exit()
    app.run(debug=True, port=8000)

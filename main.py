from flask import Flask, render_template, request, session

app = Flask(__name__)


@app.before_request
def before_request():
    if request.args.get('toggleDarkmode'):
        session.setdefault('isDarkmode', not session.get('isDarkmode', False))
    session.permanent = True


@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/club/<hyphened_club_name>')
def each_club_page(hyphened_club_name: str):
    return render_template('club.html')


@app.route('/categories')
def club_categories_page():
    return render_template('categories.html')


@app.route('/search', methods=['GET', 'POST'])
@app.route('/search/<search_query>')
def search_clubs_page(search_query: str = None):
    ...


if __name__ == '__main__':
    app.run(debug=True)

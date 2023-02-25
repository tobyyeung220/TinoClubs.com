from flask import Flask, render_template, request, session, redirect
import uuid
import enum

app = Flask(__name__)
app.secret_key = uuid.uuid4().hex


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
    return render_template('club.html')


@app.route('/categories')
def categories_page():
    return render_template('categories.html', ClubCategory=ClubCategory)


@app.route('/search', methods=['GET', 'POST'])
@app.route('/search/<search_query>')
def search_page(search_query: str = None):
    return render_template('search.html')


if __name__ == '__main__':
    app.run(debug=True, port=8000)

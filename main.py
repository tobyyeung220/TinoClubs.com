from flask import Flask, render_template, request, session, redirect
import uuid

app = Flask(__name__)
app.secret_key = uuid.uuid4().hex


@app.before_request
def before_request():
    if 'toggleDarkMode' in request.args:
        session['isDarkMode'] = not session.get('isDarkMode', False)
        return redirect(request.path)
    session.permanent = True


@app.route('/')
def home_page():
    return render_template('base.html')
    # return render_template('home.html')


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

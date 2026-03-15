from datetime import datetime
import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary', methods=['POST'])
def show_summary():
    club = next((club for club in clubs if club['email'] == request.form['email']), None)
    if not club:
        flash("Sorry, that email was not found.")
        return render_template('index.html'), 200
    return render_template('welcome.html', club=club, competitions=competitions, now=datetime.now())


@app.route('/book/<competition>/<club>')
def book(competition, club):
    found_club = next((c for c in clubs if c['name'] == club), None)
    found_competition = next((c for c in competitions if c['name'] == competition), None)

    if not found_club or not found_competition:
        flash("Something went wrong - please try again.")
        return render_template('index.html'), 200

    # Check date on competition
    competition_date = datetime.strptime(found_competition['date'], "%Y-%m-%d %H:%M:%S")
    if competition_date < datetime.now():
        flash("This competition has already taken place.")
        return render_template('welcome.html', club=found_club, competitions=competitions)

    return render_template('booking.html', club=found_club, competition=found_competition)


@app.route('/purchasePlaces', methods=['POST'])
def purchase_places():
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)

    if not competition or not club:
        flash('Something went wrong - please try again.')
        return render_template('welcome.html', club=club, competitions=competitions), 200

    points_before = int(club['points'])

    places_required = int(request.form['places'])

    if places_required > 12:
        flash("Cannot book more than 12 places.")
        return render_template(
            'booking.html',
            competition=competition,
            club=club
        ), 200

    if places_required > points_before:
        flash("Insufficient points.")
        return render_template(
            'booking.html',
            competition=competition,
            club=club
        ), 200

    available_places = int(competition['numberOfPlaces'])

    if places_required > available_places:
        flash("Not enough places available.")
        return render_template(
            'booking.html',
            competition=competition,
            club=club
        ), 200

    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - places_required

    club['points'] = str(
        int(club['points']) - places_required
    )

    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))

# Needs this to run app
if __name__ == '__main__':
    app.run(debug=True)
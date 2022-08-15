#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#from model import Venue, Shows, Artist
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(120), nullable=False)
    seeking_description = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean(), default=False)
    shows = db.relationship('Shows', backref='venue', lazy=True)

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(120), nullable=False
)
    looking_for_venues = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(), nullable=False)
    shows = db.relationship('Shows', backref='artist', lazy
=True)

class Shows(db.Model):
    __tablename__: 'Shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    response = db.session.query(Venue.city, Venue.state).order_by(Venue.city, Venue.state)
    data = []
    for res in response:
        results = Venue.query.filter(Venue.city == res.city).filter(Venue.state == res.state).all()
        
        venues = []
        for result in result:
            venues.append({
                'id': result.id,
                'name': result.name,
                'num_upcoming_shows': len(Show.query.filter(Show.start_time > datetime.now()).all())
            })

            data.append({
                'city': res.city,
                'state': res.state,
                'venues': venues
            })
    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    data = []

    for res in result:
        data.append({
            'id': res.id,
            'name': res.name,
            'num_upcoming_shows': len(Show.query.filter(Show.venue_id == res.id).filter(Show.start_time > datetime.now()).all())
            })

    response={
        'count': len(result),
        'data': data
        }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)

    if not venue:
        abort(404)

    past_shows = []
    past_shows_res = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()

    for show in past_shows_res:
        past_shows.append({
            'artist_id': show.artist_id,
            'artist_name': show.Artist._name,
            'artist_image_link': show.Artist.image_link,
            'start_time': show.start_time
            })
    upcoming_shows = []
    upcoming_shows_res = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()

    for show in upcoming_shows_res:
        upcoming_shows.append({
            'artist_id': show.artist_id,
            'artist_name': show.Artist.name,
            'artist_image_link': show.Artist.image_link,
            'start_time': show.start_time
            })

    data = {
            'id': venue.id,
            'name': venue.name,
            'genres': venue.genres,
            'address': venue.address,
            'city': venue.city,
            'state': venue.state,
            'phone': venue.phone,
            'website': venue.website,
            'facebook_link': venue.facebook_link,
            'image_link': venue.image_link,
            'past_shows': past_shows,
            'upcoming_shows': upcoming_shows,
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
            }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        venue = Venue(
            name = form.name.data,
            city = form.city.data,
            state = form.state.data,
            address = form.address.data,
            phone = form.phone.data,
            genres = form.genres.data,
            facebook_link = form.facebook_link.data,
            image_link = form.image_link.data,
            website_link = form.website_link.data,
            seeking_talent = form.seeking_talent.data,
            seeking_description = form.seeking_description.data
            )
        db.session.add(venue)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    if not error:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
        flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        abort(500)
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False

    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        abort(500)
    finally:
        db.session.close()
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  response = Artist.query.all()
  data = []

  for res in response:
      artist = {
              'id': res.id,
              'name': res.name
              }
      
      data.append(artist)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    result = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    data = []

    for res in result:
        data.append({
            'id': res.id,
            'name': res.name,
            'num_upcoming_shows': len(Show.query.filter(Show.artist_id == res.id).filter(Show.start_time > datetime.now()).all())
            })

    response = {
            'count': len(result),
            'data': data
            }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)

    if not artist:
        abort(404)

    past_shows = []
    past_shows_res = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()

    for show in past_shows_res:
        past_shows.append({
            'venue_id': show.venue_id,
            'venue_name': show.Venue.name,
            'venue_image_link': show.Venue.image_link,
            'start_time': show.start_time
            })

    upcoming_shows = []
    upcoming_shows_res = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()

    for show in upcoming_shows_res:
        upcoming_shows.append({
            'venue_id': show.venue_id,
            'venue_name': show.Venue.name,
            'venue_image_link': show.Venue.image_link,
            'start_time': show.start_time
            })
    data = {
            'id': artist.id,
            'name': artist.name,
            'genres': artist.genres,
            'city': artist.city,
            'state': artist.state,
            'phone': artist.phone,
            'website': artist.website,
            'facebook_link': artist.facebook_link,
            'seeking_venue': artist.seeking_venue,
            'seeking_description': artist.seeking_description,
            'image_link': artist.image_link,
            'past_shows': past_shows,
            'upcoming_shows': upcoming_shows,
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
            }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    if not artist:
        abort(404)

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    error = False

    try:
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.genres = form.genres.data
        artist.facebook_link = form.facebook_link.data
        artist.image_link = form.image_link.data
        artist.website_link = form.website_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        flash('Artist ' + form.name.data + 'updated successfully')
    else:
        flash('Oops an error occurred!')
        abort(500)

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    if not venue:
        abort(404)

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue.id)
    error = False

    try:
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.genres = form.genres.data
        venue.facebook_link = form.facebook_link.data
        venue.image_link = form.image_link.data
        venue.website_link = form.website_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        db.session.commit()
    except:
        error = False
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        flash('Venue ' + form.name.data + ' created successfully!')
    else:
        flash('Oops! an error occurred!')
        abort(500)

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    
    try:
        artist = Artist(
            name = form.name.data,
            city = form.city.data,
            state = form.state.data,
            genres = form.genres.data,
            facebook_link = form.facebook_link.data,
            image_link = form.image_link.data,
            website_link = form.website_link.data,
            seeking_venue = form.seeking_venue.data,
            seeking_description = form.seeking_description.data
            )
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
        flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        abort(500)
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    result = Show.query.join(Artist).join(Venue).all()
    data = []

    for res in result:
        data.append({
            'venue_id': res.venue_id,
            'venue_name': res.Venue.name,
            'artist_id': res.artist_id,
            'artist_name': res.Artist.name,
            'artist_image_link': res.Artist.image_link,
            'start_time': res.start_time
            })

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False

    try:
        show = Show(
                artist_id = form.artist_id.data,
                venue_id = form.venue_id.data,
                start_time = form.start_time.data
                )
        db.session.add(show)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()

    if error:
        flash('An error occurred. Show could not be listed!')
    else:
        flash('Show was successfully listed!')
        abort(500)
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(host='0.0.0.0')

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

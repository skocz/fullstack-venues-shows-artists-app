#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import *
from werkzeug.exceptions import abort
from datetime import datetime
from sqlalchemy.orm import relationship
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value
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
  locations = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data = []

  for location in locations:
    venue_in_location = Venue.query.filter_by(state=location.state, city=location.city).all()
    venues = []
    
    for venue in venue_in_location:
      upcoming_shows = Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).all()
      venues.append({
        "id": venue.id,
        "name": venue.name, 
        "num_upcoming_shows": len(upcoming_shows)
      })

    data.append({
      "city": location.city,
      "state": location.state, 
      "venues": venues
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  res= Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  resCount= len(res)
  response={
    "count" : resCount,
    "data" : []
  }
  if not res: 
    flash('Sorry try some different keywords') 

  for venue in res:
    num_upcoming_shows = db.session.query(func.count(Show.id)).filter(
      Show.venue_id == venue.id, Show.start_time > datetime.now()).scalar()
    response['data'].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows,
    })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  selected_venue = Venue.query.get_or_404(venue_id)
  # Get the shows for the selected venue and join with the Artist table
  shows = db.session.query(Show, Artist.name, Artist.image_link)\
    .join(Artist).filter(Show.venue_id == selected_venue.id)
  
  past_shows = []
  upcoming_shows = []

  for show, artist_name, artist_image_link in shows:
    temp_show = {
      'artist_id': show.artist_id,
      'artist_name': artist_name,
      'artist_image_link': artist_image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
      past_shows.append(temp_show)
    else:
      upcoming_shows.append(temp_show)

  # object class to dict
  data = vars(selected_venue)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # Set the FlaskForm
  form = VenueForm(request.form, meta={'csrf': False})
  # Validate all fields
  if form.validate():
    # Prepare for transaction
    try:
      venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone = form.phone.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        website = form.website_link.data,
        genres=form.genres.data,
        seeking_description = form.seeking_description.data,
        seeking_talent=form.seeking_talent.data,   
      )

      db.session.add(venue)
      db.session.commit()
    except ValueError as e:
      print(e)
      # If there is any error, roll back it
      db.session.rollback()
    finally:
      db.session.close()

    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  # If there is any invalid field
  else:
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    flash('Venue was successfully deleted!')
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artistLists = Artist.query.all()

  if not artistLists: 
    flash('no artists exists') 
  for artist in artistLists:
    data.append({
      "id": artist.id,
      "name": artist.name,
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  res= Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  resCount= len(res)
  response={
    "count" : resCount,
    "data" : []
  }

  if not res:
    flash('Sorry try some different keywords') 
  
  for item in res:
    upcoming_shows = db.session.query(Show).join(Artist).filter(Show.artist_id == item.id).filter(Show.start_time > datetime.now()).all()
    num_upcoming_shows = len(upcoming_shows)
    response['data'].append({
      "id": item.id,
      "name": item.name,
      "num_upcoming_shows": num_upcoming_shows,
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  selected_artist = Artist.query.get_or_404(artist_id)

  shows = db.session.query(Show, Venue.name, Venue.image_link)\
    .join(Venue).filter(Show.artist_id == artist_id)
  
  past_shows = []
  upcoming_shows = []

  for show, venue_name, venue_image_link in shows:
    temp_show = {
      "venue_id": show.venue_id,
      "venue_name": venue_name,
      "venue_image_link": venue_image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
      past_shows.append(temp_show)
    else:
      upcoming_shows.append(temp_show)

  # object class to dict
  data = vars(selected_artist)
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist = form.populate_obj(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  error = False
  try:
    venue = Venue.query.get(venue_id)
    venue = form.populate_obj(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form, meta={"csrf": False})
  if form.validate():
    try:
      artist = Artist(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          phone=form.phone.data,
          genres=form.genres.data,
          facebook_link=form.facebook_link.data,
          image_link=form.image_link.data,
          website=form.website_link.data,
          seeking_venue=form.seeking_venue.data,
          seeking_description=form.seeking_description.data
        )
      db.session.add(artist)
      db.session.commit()
    except ValueError as e:
      print(e)
      # If there is any error, roll back it
      db.session.rollback()
    finally:
      db.session.close()

    flash('Artist ' + form.name.data + ' was successfully listed!')
    return render_template('pages/home.html')
  # If there is any invalid field
  else:
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []

  shows = Show.query.all()
  if not shows: 
    flash('no shows exists')
  for show in shows:
    find_artist = Artist.query.filter(Artist.id==show.artist_id).first()
    find_venue = Venue.query.filter(Venue.id==show.venue_id).first()
    data.append({
      "venue_id": find_venue.id,
      "venue_name": find_venue.name,
      "artist_id": find_artist.id,
      "artist_name": find_artist.name,
      "artist_image_link": find_artist.image_link,
      "start_time": format_datetime(show.start_time, format='medium')
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  
  form = ShowForm(request.form, meta={"csrf": False})
  if form.validate():
    try:
      artist = Artist.query.get(form.artist_id.data)
      venue = Venue.query.get(form.venue_id.data)
      if not artist:
        flash('Artist not found')
        return render_template('forms/new_show.html', form=form)
      if not venue:
        flash('Venue not found')
        return render_template('forms/new_show.html', form=form)
      
      show = Show(
          artist_id=form.artist_id.data,
          venue_id=form.venue_id.data,
          start_time=form.start_time.data
      )
      db.session.add(show)
      db.session.commit()
    except ValueError as e:
      print('e',e)
      db.session.rollback()
    finally:
      db.session.close()

    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  else:
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = VenueForm()
    return render_template('pages/shows.html', form=form)

# result = db.session.query(Show).join(Artist).filter(Show.artist_id == item.id).filter(Show.start_time > datetime.now()).all()

@app.route('/shows/search', methods=['POST'])
def search_shows():
  search_term = request.form.get('search_term', '')
  shows = db.session.query(
    Venue.name,
    Artist.name,
    Artist.image_link,
    Show.start_time,
    Show.artist_id,
    Show.venue_id
  ).join(
    Show, Venue.id == Show.venue_id
  ).join(
    Artist, Artist.id == Show.artist_id
  ).filter(
    Artist.name.ilike('%'+search_term+'%') | Venue.name.ilike('%'+search_term+'%')
  ).all()

  results = []
  for venue_name, artist_name, artist_image_link, start_time, artist_id, venue_id in shows:
    results.append({
      "artist_id": artist_id,
      "artist_name": artist_name,
      "artist_image_link": artist_image_link,
      "venue_id": venue_id,
      "venue_name": venue_name,
      "start_time": format_datetime(start_time, format='medium')
    })

  response = {
    "count": len(results),
    "data": results
  }
 
  return render_template('pages/show.html', results=response, search_term=request.form.get('search_term', ''))


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
  app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
'''

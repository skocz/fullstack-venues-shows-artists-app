#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
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
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    seeking_description = db.Column(db.String, nullable=False)
    seeking_talent = db.Column(db.Boolean,nullable=False, default=False)
    shows = db.relationship('Show', backref='venue', lazy=True)
    
    def __repr__(self):
      return f'<Venue ID: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, website: {self.website}, genres: {self.genres}, seeking_description: {self.seeking_description}, seeking_talent: {self.seeking_talent}, shows: {self.shows}>'


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,  nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120), nullable=False)
    seeking_venue = db.Column(db.Boolean,nullable=False, default=False)
    seeking_description = db.Column(db.String, nullable=False)
    shows = db.relationship('Show', backref='showlist', lazy=True)
    
    def __repr__(self):
      return f'<Artist ID: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, website: {self.website}, seeking_venue: {self.seeking_venue}, seeking_description: {self.seeking_description}, shows: {self.shows}>'


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id =  db.Column(db.Integer, db.ForeignKey('venue.id'),nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'),nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False )
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False )

    def __repr__(self):
      return f'<Show ID: {self.id}, venue_id: {self.venue_id}, artist_id: {self.artist_id}, start_time: {self.start_time}'

#locations = db.Table('locations',
#     db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True),
#     db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
# )
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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  dummy_data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]

  locations = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data = []

  for location in locations:
    venue_in_location = Venue.query.filter_by(state=location.state, city=location.city).all()
    venues = []
    
    for venue in venue_in_location:
      venues.append({
        "id": venue.id,
        "name": venue.name, 
        "num_upcoming_shows": 0
        # TODO: len(db.session.query(Show).filter(Show.venue_id==1).filter(Show.start_time>datetime.now()).all())
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
  # print(resCount)
  response={
    "count" : resCount,
    "data" : []
  }
  if not res: 
    flash('Sorry try some different keywords') 
  
  for item in res:
    response['data'].append({
      "id": item.id,
      "name": item.name,
      "num_upcoming_shows": 0,
    })

  # print(item.name, 'row')
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  temptResponse={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  selected_venue = Venue.query.get(venue_id)

  if not selected_venue:
    selected_venue = {}
  
  arrayGenres= []
  lines = selected_venue.genres.replace("}","").replace("{","").split(',')

  for x in lines:
    st = x.strip()
    arrayGenres.append(st)
  
  data = {
    "id": selected_venue.id,
    "name": selected_venue.name,
    "genres": arrayGenres,
    "address": selected_venue.address,
    "city": selected_venue.city,
    "state": selected_venue.state,
    "phone": selected_venue.phone,
    "website": selected_venue.website,
    "facebook_link": selected_venue.facebook_link,
    "seeking_talent": selected_venue.seeking_talent,
    "seeking_description": selected_venue.seeking_description,
    "image_link": selected_venue.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }

  all_upcoming_shows = Show.query.join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  # print(all_upcoming_shows, 'all_upcoming_shows')
  upcoming_shows_list = []
  if all_upcoming_shows:
    for upcomming_show in all_upcoming_shows:
      upcoming_shows_list.append({
        "venue_id": upcomming_show.venue_id,
        "venue_name": upcomming_show.venue.name,
        "venue_image_link": upcomming_show.venue.image_link,
        "start_time": format_datetime(str(upcomming_show.start_time))
      })

  data['upcoming_shows'] = upcoming_shows_list
  data['upcoming_shows_count'] = len(upcoming_shows_list)

  all_past_shows = Show.query.join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  past_shows_list = []
  for past_show in all_past_shows:
    past_shows_list.append({
      "venue_id": past_show.venue_id,
      "venue_name": past_show.venue.name,
      "venue_image_link": past_show.venue.image_link,
      "start_time": format_datetime(str(past_show.start_time))
    })

  data['past_shows'] = past_shows_list
  data['past_shows_count'] = len(past_shows_list)

  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  # print(request.form.getlist('genres'))
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website_link']
    genres = request.form.getlist('genres')
    seeking_description = request.form['seeking_description']
    seeking_talent = True if 'seeking_talent' in request.form else False

    new_venue = Venue( name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, seeking_talent=seeking_talent, website=website, seeking_description=seeking_description)
    db.session.add(new_venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.' , 'error')
    abort(500)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

# https://stackoverflow.com/questions/33785415/deleting-a-file-on-server-by-delete-form-method
@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  # print(venue_id,' delete venue_id')
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
    return render_template('pages/home.html')
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  fakedata=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  data = []
  artistLists = Artist.query.all()
  # print('list Artist: ', artistLists)

  if not artistLists: 
    flash('no artists exists') 
    # return render_template('pages/artists.html')
  for artist in artistLists:
    data.append({
      "id": artist.id,
      "name": artist.name,
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  res= Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  resCount= len(res)
  # print(resCount)
  response={
    "count" : resCount,
    "data" : []
  }

  if not res:
    flash('Sorry try some different keywords') 
  
  for item in res:
    response['data'].append({
      "id": item.id,
      "name": item.name,
      "num_upcoming_shows": 0,
    })
  

  # print(item.name, 'row')
  tempResponse={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artistLists = Artist.query.all()
  selected_artist = Artist.query.get(artist_id)
  # print(selected_artist, 'active_artist')
  if not selected_artist:
    selected_artist = {}
  
  arrayGenres= []
  lines = selected_artist.genres.replace("}","").replace("{","").split(',')
  for x in lines:
    st = x.strip()
    arrayGenres.append(st)

  data = {
    "id": selected_artist.id,
    "name": selected_artist.name,
    "genres": arrayGenres,
    "city": selected_artist.city,
    "state": selected_artist.state,
    "phone": selected_artist.phone,
    "website": selected_artist.website,
    "facebook_link": selected_artist.facebook_link,
    "seeking_venue": selected_artist.seeking_venue,
    "seeking_description":selected_artist.seeking_description,
    "image_link": selected_artist.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  all_upcoming_shows = Show.query.join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows_list = []
  if all_upcoming_shows:
    for upcomming_show in all_upcoming_shows:
      upcoming_shows_list.append({
        "venue_id": upcomming_show.venue_id,
        "venue_name": upcomming_show.venue.name,
        "venue_image_link": upcomming_show.venue.image_link,
        "start_time": format_datetime(str(upcomming_show.start_time))
        
      })

  data['upcoming_shows'] = upcoming_shows_list
  data['upcoming_shows_count'] = len(upcoming_shows_list)

  all_past_shows = Show.query.join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
  past_shows_list = []
  for past_show in all_past_shows:
    past_shows_list.append({
      "venue_id": past_show.venue_id,
      "venue_name": past_show.venue.name,
      "venue_image_link": past_show.venue.image_link,
      "start_time": format_datetime(str(past_show.start_time))
    })

  data['past_shows'] = past_shows_list
  data['past_shows_count'] = len(past_shows_list)

  data1={
    "id": 1,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
   
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
 
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  all_upcoming_shows = Show.query.join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows_list = []
  if all_upcoming_shows:
    for upcomming_show in all_upcoming_shows:
      upcoming_shows_list.append({
        "venue_id": upcomming_show.venue_id,
        "venue_name": upcomming_show.venue.name,
        "venue_image_link": upcomming_show.venue.image_link,
        "start_time": format_datetime(str(upcomming_show.start_time))
        
      })

  data['upcoming_shows'] = upcoming_shows_list
  data['upcoming_shows_count'] = len(upcoming_shows_list)

  all_past_shows = Show.query.join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
  past_shows_list = []
  for past_show in all_past_shows:
    past_shows_list.append({
      "venue_id": past_show.venue_id,
      "venue_name": past_show.venue.name,
      "venue_image_link": past_show.venue.image_link,
      "start_time": format_datetime(str(past_show.start_time))
    })

  data['past_shows'] = past_shows_list
  data['past_shows_count'] = len(past_shows_list)
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  arrayGenres= []
  lines = artist.genres.replace("}","").replace("{","").split(",")

  for x in lines:
    st = x.strip()
    arrayGenres.append(st.replace('"',''))
     

  artist.genres = arrayGenres
  # print(artist)
  tempartist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  form = ArtistForm(obj=artist)
  # form = ArtistForm(request.form, obj=artist)
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
  
  arrayGenres= []
  lines = venue.genres.replace("}","").replace("{","").split(",")

  for x in lines:
    st = x.strip()
    arrayGenres.append(st.replace('"',''))
     

  venue.genres = arrayGenres
  # print(type(venue.genres), 'new')
  form = VenueForm(obj=venue)
  tempvenue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  error = False
  try:
    venue = Venue.query.get(venue_id)
    venue = form.populate_obj(venue)
  
    # print(venue, 'venue')
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
    error = False
    try:
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      facebook_link = request.form['facebook_link']
      image_link = request.form['image_link']
      website = request.form['website_link']
      seeking_venue = False
      seeking_description = request.form['seeking_description']

      new_artist = Artist( name=name, city=city,state=state, phone=phone, genres=genres,
        facebook_link=facebook_link,image_link=image_link,seeking_venue=seeking_venue,website=website,seeking_description=seeking_description)
      db.session.add(new_artist)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      # print(sys.exc_info())
    finally:
      db.session.close()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      redirect(url_for('index'))
    if error:
      abort(500)
      flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.', 'error')
    else:
      return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  fakedata=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  data = []
  
  shows = Show.query.all()
  # print(shows, 'shows')
  if not shows: 
    flash('no shows exists')
  for show in shows:
  #  active_artist = Artist.query.get(artist_id)
    findArtist = db.session.query(Artist).filter_by(id=show.artist_id).first()
    findVenue = db.session.query(Venue).filter_by(id=show.venue_id).first()
    # print(findVenue, 'show')
    data.append({
     "venue_id": show.venue_id,
     "venue_name": findVenue.name,
     "artist_id": show.artist_id,
     "artist_name": findArtist.name,
     "artist_image_link": findArtist.image_link,
     "start_time": str(show.start_time)
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
  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']
  
  findArtist = db.session.query(Artist).filter_by(id=artist_id).first()
  findVenue = db.session.query(Venue).filter_by(id=venue_id).first()
  # print(findArtist,'name', findVenue,'city')
  form = ShowForm(request.form)

  if not findArtist:
    flash("The artist ID doesn't exists")
    return render_template('pages/new_show.html', form=form)
  if not findVenue: 
    flash("The vanue ID doesn't exists")
    return render_template('pages/new_show.html', form=form)

  try:
    new_show = Show( artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(new_show)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    # print(sys.exc_info())
  finally:
    db.session.close()
    flash('Show was successfully listed!')
  if error:
    abort(500)
    flash('An error occurred. Show could not be listed.')
  else:
    return render_template('pages/shows.html')

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

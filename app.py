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
from models import *
import re
from werkzeug.exceptions import abort


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
      upcoming_shows = Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).all()
      venues.append({
        "id": venue.id,
        "name": venue.name, 
        "num_upcoming_shows": len(upcoming_shows)
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
  # temptResponse={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
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
  selected_venue = Venue.query.filter_by(id=venue_id).first()

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
    seeking_talent = 'seeking_talent' in request.form
    # Check phone number
    if not re.match(r'^\d{3}-\d{3}-\d{4}$', phone):
      raise ValueError('Invalid phone number')
    
    new_venue = Venue(
      name=name,
      city=city,
      state=state,
      address=address,
      phone=phone,
      genres=genres,
      facebook_link=facebook_link,
      image_link=image_link,
      seeking_talent=seeking_talent,
      website=website,
      seeking_description=seeking_description
    )
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return redirect('/')
  except ValueError as e:
    error = True
    db.session.rollback()
    flash(str(e), 'error')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.', 'error')
  finally:
    db.session.close()
  
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.' , 'error')
    abort(500)
  else:
    return render_template('pages/home.html')

# https://stackoverflow.com/questions/33785415/deleting-a-file-on-server-by-delete-form-method
@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    shows = Show.query.filter_by(venue_id=venue_id).all()
    for show in shows:
      db.session.delete(show)
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
  # return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
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

  # tempResponse={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # artistLists = Artist.query.all()
  selected_artist = Artist.query.get(artist_id)
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
    seeking_venue = 'seeking_venue' in request.form
    seeking_description = request.form['seeking_description']
    # Check phone number
    if not re.match(r'^\d{3}-\d{3}-\d{4}$', phone):
      raise ValueError('Invalid phone number')
    
    new_artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres,
      facebook_link=facebook_link, image_link=image_link,
      seeking_venue=seeking_venue, website=website,
      seeking_description=seeking_description
    )
    db.session.add(new_artist)
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    error = True
    print(e)
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.', 'error')
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('index'))


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
  error = False
  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']
  
  findArtist = db.session.query(Artist).filter_by(id=artist_id).first()
  findVenue = db.session.query(Venue).filter_by(id=venue_id).first()
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

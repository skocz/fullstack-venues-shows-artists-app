from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from sqlalchemy import CheckConstraint
from datetime import date
# from app import db
db = SQLAlchemy()

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
class Venue(db.Model):
  __tablename__ = 'venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False) # fix this - add some constrains
  image_link = db.Column(db.String(500), nullable=False)
  facebook_link = db.Column(db.String(120), nullable=False)
  website = db.Column(db.String(120), nullable=False)
  genres = db.Column(db.ARRAY(db.String), nullable=False)
  seeking_description = db.Column(db.String, nullable=False)
  seeking_talent = db.Column(db.Boolean,nullable=False, default=False)
  shows = db.relationship('Show', backref='venue', lazy="joined", cascade="all, delete")

  def __repr__(self):
    return f'<Venue ID: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, website: {self.website}, genres: {self.genres}, seeking_description: {self.seeking_description}, seeking_talent: {self.seeking_talent}, shows: {self.shows}>'


class Artist(db.Model):
  __tablename__ = 'artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String,  nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False) #add some constrains 
  genres = db.Column(db.ARRAY(db.String), nullable=False)
  image_link = db.Column(db.String(500), nullable=False)
  facebook_link = db.Column(db.String(120), nullable=False)
  website = db.Column(db.String(120), nullable=False)
  seeking_venue = db.Column(db.Boolean,nullable=False, default=False)
  seeking_description = db.Column(db.String, nullable=False)
  shows = db.relationship('Show', backref='showlist', lazy="joined", cascade="all, delete")
  
  def __repr__(self):
    return f'<Artist ID: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, website: {self.website}, seeking_venue: {self.seeking_venue}, seeking_description: {self.seeking_description}, shows: {self.shows}>'

class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id =  db.Column(db.Integer, db.ForeignKey('venue.id'),nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'),nullable=False)
  start_time = db.Column(db.DateTime, nullable=False, default=date.today())

  def __repr__(self):
    return f'<Show ID: {self.id}, venue_id: {self.venue_id}, artist_id: {self.artist_id}, start_time: {self.start_time}'

# locations = db.Table('locations',
#     db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True),
#     db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
# )
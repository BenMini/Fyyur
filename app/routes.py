import babel
from flask import render_template, request, flash, redirect, \
    url_for, abort, jsonify
from app import app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import dateutil.parser
from app.forms import ArtistForm, ShowForm, VenueForm
from app.models import Artist, Venue, Show
import sys


# ----------------------------------------------------------------
# Filters
# ----------------------------------------------------------------


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

# Index Route
# ----------------------------------------------------------------
@app.route('/')
def index():
    return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------

# Artist Index
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    '''shows list of artists in database'''
    artists = Artist.query.all()
    return render_template('pages/artists.html', artists=artists)


# Artist Search
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
    '''search artists table using partial matches to strings'''
    # get search term from form
    search_term = request.form.get('search_term', '')
    # use ilike to match names
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(artists),
        "data": []
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))

# Artist New
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    '''shows new artist form'''
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

# Artist Create
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    '''create new artist'''
    form = ArtistForm()
    error = False
    try:
        name = form.name.data
        city = form.city.data
        state = form.state.data
        phone = form.phone.data
        genres = form.genres.data
        facebook_link = form.facebook_link.data
        image_link = form.image_link.data
        website = form.website.data
        seeking_venue = True if form.seeking_venue.data == 'Yes' else False
        seeking_description = form.seeking_description.data
        newArtist = Artist(name=name, city=city, state=state,
                           phone=phone, genres=genres,
                           facebook_link=facebook_link,
                           website=website, image_link=image_link,
                           seeking_venue=seeking_venue,
                           seeking_description=seeking_description)
        db.session.add(newArtist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + name + ' could not be listed.')
        abort(500)
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')

# Artist Show
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    '''shows artists page with all information'''
    # query artist by id
    artist = Artist.query.filter_by(id=artist_id).first()
    # query shows matching artist id
    shows = Show.query.filter_by(artist_id=artist_id).all()

    def upcoming_shows():
        # TODO: refactor this to a higher scope function
        upcoming = []

        for show in shows:
            if show.start_time > datetime.now():
                upcoming.append({
                    "venue_id": show.venue_id,
                    "venue_name": Venue.query.filter_by(
                        id=show.venue_id).first().name,
                    "venue_image_link": Venue.query.filter_by(
                        id=show.venue_id).first().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
        return upcoming

    def past_shows():
        past = []

        for show in shows:
            if show.start_time < datetime.now():
                past.append({
                    "venue_id": show.venue_id,
                    "venue_name": Venue.query.filter_by(
                        id=show.venue_id).first().name,
                    "venue_image_link": Venue.query.filter_by(
                        id=show.venue_id).first().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
        return past

    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website,
        'facebook_link': artist.facebook_link,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,
        'past_shows': past_shows(),
        'upcoming_shows': upcoming_shows(),
        'past_shows_count': len(past_shows()),
        'upcoming_shows_count': len(upcoming_shows())
    }

    return render_template('pages/show_artist.html', artist=data)

# Artist Edit
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    '''pulls artist form and populates with current artist data'''
    form = ArtistForm()
    # query artist
    artist = Artist.query.filter_by(id=artist_id).first()
    # populate form with artist data
    artist = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
    }

    return render_template('forms/edit_artist.html', form=form, artist=artist)

# Artist Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    '''posts updates to artist information'''
    error = False
    form = ArtistForm()
    try:
        # post to artist with matchin id and update any changes
        artist = Artist.query.filter_by(id=artist_id).first()
        artist.name = form.name.data
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.facebook_link = form.facebook_link.data
        artist.image_link = form.image_link.data
        artist.website = form.website.data
        artist.seeking_venue = True if form.seeking_venue.data == 'Yes' else False
        artist.seeking_description = form.seeking_description.data
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist: ' +
              request.form['name'] + ' could not be updated')
        abort(500)
    else:
        flash('Artist was successfully Updated.')
        return redirect(url_for('show_artist', artist_id=artist_id))

# Artist Delete
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    '''Delete artist'''
    error = False
    try:
        artist = Artist.query.filter_by(id=artist_id).first()
        db.session.delete(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occured, Artist ' + artist.name +
              ' could not be deleted.')
    else:
        flash('Artist was successfully deleted.')
        return jsonify({'success': True})

#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------

# Venue Index
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
    '''Index of all venues'''
    # query all venues
    data = Venue.query.distinct('state', 'city').order_by('state').all()
    # for each place filter by state then city
    for place in data:
        place.venues = Venue.query.filter_by(
            state=place.state, city=place.city)
    return render_template('pages/venues.html', areas=data)

# Venue Search
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
    '''Search venues, using partial strings'''
    # get term from form

    # query venues against search
    venues = Venue.query.filter(Venue.name.ilike(f'%{search}%')).all()

    response = {
        # count number of venues
        "count": len(venues),
        # store info in data variable
        "data": []
    }

    # find shows for current venue
    for venue in venues:
        num_upcoming_shows = 0
        shows = Show.query.filter_by(venue_id=venue.id).all()

    # increment num_upcoming_shows by 1 for each upcoming
        for show in shows:
            if show.start_time > datetime.now():
                num_upcoming_shows += 1

    # add response to data
            response['data'].append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": num_upcoming_shows,
            })

    return render_template('pages/search_venues.html',
                           results=response,
                           search=request.form.get('search_term', ""))


# Venue New
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    '''pulls form for creating venue'''
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

# Venue Create
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    '''formats data for form entry'''
    error = False
    form = VenueForm()
    try:
        name = form.name.data
        genres = request.form.getlist('genres'),
        address = form.address.data
        city = form.city.data
        state = form.state.data
        phone = form.address.data
        website = form.website.data
        facebook_link = form.facebook_link.data
        seeking_talent = True if form.seeking_talent.data == 'Yes' else False
        seeking_description = form.seeking_description.data
        image_link = form.image_link.data

        newVenue = Venue(name=name, city=city, state=state, address=address,
                         phone=phone, genres=genres,
                         facebook_link=facebook_link,
                         website=website, image_link=image_link,
                         seeking_talent=seeking_talent,
                         seeking_description=seeking_description)

        db.session.add(newVenue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print('error:' + sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + name + ' could not be listed.')
        abort(500)
    else:
        flash('Venue ' + request.form['name'] +
              ' was successfully listed!')
        return render_template('pages/home.html')

# Venue Show
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    '''shows the venue page with the given venue_id'''
    # query first venue by id
    venue = Venue.query.filter_by(id=venue_id).first()
    # query all shows with relationship to venue
    shows = Show.query.filter_by(venue_id=venue_id).all()

    def upcoming_shows():
        # find all upcoming shows
        upcoming = []

        for show in shows:
            # iterate through shows and find all starting after current time
            if show.start_time > datetime.now():
                # add shows to upcoming array
                upcoming.append({
                    "artist_id": show.artist_id,
                    "artist_name": Artist.query.filter_by(
                        id=show.artist_id).first().name,
                    "artist_image_link": Artist.query.filter_by(
                        id=show.artist_id).first().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
        return upcoming

    def past_shows():
        # find all previous shows
        # append artist_id, artist_name, image, and start time
        past = []

        # iterate through shows and find all shows before now
        for show in shows:
            # append results to past array
            if show.start_time < datetime.now():
                past.append({
                    "artist_id": show.artist_id,
                    "artist_name": Artist.query.filter_by(
                        id=show.artist_id).first().name,
                    "artist_image_link": Artist.query.filter_by(
                        id=show.artist_id).first().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
        return past

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
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': past_shows(),
        'upcoming_shows': upcoming_shows(),
        'past_shows_count': len(past_shows()),
        'upcoming_shows_count': len(upcoming_shows())
    }

    return render_template('pages/show_venue.html', venue=data)

# Venue Edit
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    '''populates venue form with matching ID'''
    form = VenueForm()
    # query venue by id
    venue = Venue.query.filter_by(id=venue_id).first()
    # populate with venue data
    venue = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }

    return render_template('forms/edit_venue.html', form=form, venue=venue)

# Venue Update
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    '''take values from the venue form submitted, and update existing'''
    error = False
    form = VenueForm()
    try:
        venue = Venue.query.filter_by(id=venue_id).first()
        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.facebook_link = form.facebook_link.data
        venue.website = form.website.data
        venue.image_link = form.image_link.data
        venue.seeking_talent = True if form.seeking_talent.data == 'Yes' else False
        venue.seeking_description = form.seeking_description.data
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        sys(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred, Venue: ' + request.form['name'] +
              'could not be listed')
    else:
        flash('Venue: ' + request.form['name'] + 'was updated.')
        return redirect(url_for('show_venue', venue_id=venue_id))

# Venue Delete
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    '''deletes venue from database'''
    error = False
    try:
        # query venue that matches id
        venue = Venue.query.filter_by(Venue.id == venue_id).first()
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' +
              venue.name + ' could not be deleted')
        abort(500)
    else:
        flash('Venure was successfully deleted.')
        return jsonify({'success': True})

#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

# Shows Index
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
    '''displays list of shows at /shows'''
    shows = Show.query.all()
    data = []

    for show in shows:
        data.append({
            'venue_id': show.venue_id,
            'venue_name': Venue.query.filter_by(id=show.venue_id).first().name,
            'aritst_id': show.artist_id,
            'artist_name': Artist.query.filter_by(
                id=show.aritst_id).first().name,
            'aritst_image_link': Artist.query.filter_by(
                id=show.artist_id).first().image_link,
            'start_time': format_datetime(str(show.start_time))
        })
    return render_template('pages/shows.html', shows=shows)

# Shows New
#  ----------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
    '''renders show form.'''
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

# Shows Create
#  ----------------------------------------------------------------
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    '''submits show form to database'''
    error = False
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']
        newShow = Show(artist_id=artist_id, venue_id=venue_id,
                       start_time=start_time)
        db.session.add(newShow)
    except:
        error = True
        db.session.rollback()
        print('error' + str(sys.exc_info()))
    finally:
        db.session.close
    if error:
        flash('Show could not be listed.')
    else:
        flash('Show was successfully listed!')
        return render_template('pages/home.html')

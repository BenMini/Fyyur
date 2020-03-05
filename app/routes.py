import babel
from flask import render_template, request, flash, redirect, \
    url_for, abort, jsonify
from app import app, db
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

# Artist Create
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET', 'POST'])
def create_artist():
    '''create new artist'''
    form = ArtistForm()
    if form.validate_on_submit():
        artist = Artist(
            name=form.name.data,
            genres=form.genres.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            website=form.website.data,
            facebook_link=form.facebook_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data,
            image_link=form.image_link.data
        )
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + artist.name +
              ' was successfully listed!')
        return redirect(url_for('artists'))
    return render_template('forms/new_artist.html', form=form)

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
@app.route('/artists/<int:artist_id>/edit', methods=['GET', 'POST'])
def edit_artist(artist_id):
    '''pulls artist form and populates with current artist data'''
    form = ArtistForm()
    # query artist
    artist = Artist.query.filter_by(id=artist_id).first_or_404()
    # populate form with artist data
    if form.validate_on_submit():
        artist.name = form.name.data
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.website = form.website.data
        artist.facebook_link = form.facebook_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        artist.image_link = form.image_link.data
        db.session.add(artist)
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_artist'))
    elif request.method == 'GET':
        form.name.data = artist.name
        form.genres.data = artist.genres
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.website.data = artist.website
        form.facebook_link.data = artist.facebook_link
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description
        form.image_link.data = artist.image_link
    return render_template('forms/edit_artist.html', form=form, artist=artist)


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
    search = request.form.get('search_term')
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

# TODO Combine into one


# Venue Create
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET', 'POST'])
def create_venue():
    '''create new venue'''
    form = VenueForm()
    if form.validate_on_submit():
        venue = Venue(
            name=form.name.data,
            genres=form.genres.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            website=form.website.data,
            facebook_link=form.facebook_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data,
            image_link=form.image_link.data
        )
        db.session.add(venue)
        db.session.commit()
        flash('venue ' + venue.name +
              ' was successfully listed!')
        return redirect(url_for('venues'))
    return render_template('forms/new_venue.html', form=form)

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
    '''pulls venue form and populates with current artist data'''
    form = VenueForm()
    # query artist
    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    # populate form with artist data
    if form.validate_on_submit():
        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.address = form.address.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.website = form.website.data
        venue.facebook_link = form.facebook_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        venue.image_link = form.image_link.data
        db.session.add(venue)
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_venue'))
    elif request.method == 'GET':
        form.name.data = venue.name
        form.genres.data = venue.genres
        form.address.data = venue.address
        form.city.data = venue.city
        form.state.data = venue.state
        form.phone.data = venue.phone
        form.website.data = venue.website
        form.facebook_link.data = venue.facebook_link
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description
        form.image_link.data = venue.image_link
    return render_template('forms/edit_venue.html', form=form, venue=venue)


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
                id=show.artist_id).first().name,
            'aritst_image_link': Artist.query.filter_by(
                id=show.artist_id).first().image_link,
            'start_time': format_datetime(show.start_time)
        })
    return render_template('pages/shows.html', shows=data)

# TODO Combine into one

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

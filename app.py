# import
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext import automap
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# database setup ORM
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Reference the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# create flask app
app = Flask(__name__)

# define what to do when user hits the index route
# list all routes that are available
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available Route:<br/>"
        f"🌧 <a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><p>"
        f"📡 <a href='/api/v1.0/stations'>/api/v1.0/stations</a><p>"
        f"🌡️ <a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><p>"
        f"📅 <a href='/api/v1.0/temp/yyyy-mm-dd'>/api/v1.0/temp/yyyy-mm-dd</a><p>"
        f"📅 <a href='/api/v1.0/temp/yyyy-mm-dd/yyyy-mm-dd'>/api/v1.0/temp/yyyy-mm-dd/yyyy-mm-dd</a>"
    )

#/api/v1.0/precipitation
#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary

@app.route("/api/v1.0/precipitation")
def precipation():
    session= Session(engine)
    # Query Measurement
    results = (session.query(Measurement.date, Measurement.tobs)
                      .order_by(Measurement.date))
    # Create a dictionary
    precipitation_date_tobs = []
    for each_row in results:
        dt_dict = {}
        dt_dict["date"] = each_row.date
        dt_dict["tobs"] = each_row.tobs
        precipitation_date_tobs.append(dt_dict)
    # Disconnect from database
    session.close()
    return jsonify(precipitation_date_tobs)


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session= Session(engine)
    # Query Stations
    results = session.query(Station.name).all()
    # Convert list of tuples into normal list
    stations_list = list(np.ravel(results))
    # Disconnect from database
    session.close()
    return jsonify(stations_list)


#passof the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session= Session(engine)
    # Query TOBS
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query the primary station for all tobs from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    # Return the results
    session.close()
    return jsonify(temps=temps)


#/api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/temp/<startdate>")
@app.route("/api/v1.0/temp/<startdate>/<enddate>")
def stats(startdate=None, enddate=None):
    session= Session(engine)
    # Return TMIN, TAVG, TMAX
    # Select statement
    sql = [func.min(Measurement.tobs), func.avg(
        Measurement.tobs), func.max(Measurement.tobs)]

    if enddate:
        results = session.query(*sql).\
        filter(Measurement.date >= startdate).\
        filter(Measurement.date <= enddate).all()
        # Calculate TMIN, TAVG, TMAX for dates greater than start
    else:    
        results = session.query(*sql).\
        filter(Measurement.date >= startdate).all()
    
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    # Results
    session.close()
    return jsonify(temps=temps)




if __name__ == '__main__':
    # set to false if deploying to a live website server (such as Google Cloud, Heroku, or AWS Elastic Beanstaulk)
    app.run(debug=True)
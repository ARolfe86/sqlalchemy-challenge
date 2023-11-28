# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from sqlalchemy.sql import and_

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"        
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Get the most recent date
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year = int(recent_date.date[:4])
    month = int(recent_date.date[5:7])
    day = int(recent_date.date[8:])
    most_recent_date = dt.datetime(year, month, day)

    # Calculate the date one year from the last date in data set.
    filter_date = most_recent_date - dt.timedelta(days=366)

    # Perform a query to retrieve the data and precipitation scores
    result = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > filter_date).\
        order_by(Measurement.date).all() 
    
    session.close()

    all_precipitation = []
    for date, precipitation in result:
        dict = {}
        dict[date] = precipitation
        all_precipitation.append(dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query all stations
    results = session.query(Station.station).all()
    
    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Get the most recent date
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year = int(recent_date.date[:4])
    month = int(recent_date.date[5:7])
    day = int(recent_date.date[8:])
    most_recent_date = dt.datetime(year, month, day)

    # Calculate the date one year from the last date in data set.
    filter_date = most_recent_date - dt.timedelta(days=366)

    most_active_station = session.query(Measurement.station, func.count(Measurement.tobs).label("observations")).\
    group_by(Measurement.station).\
    order_by(desc("observations")).\
    all()

    most_active_station_id = most_active_station[0].station
    

    temperatures = session.query(Measurement.date, Measurement.tobs).\
    where(Measurement.station == most_active_station_id).all()

    session.close()

    all_tobs = []
    for date, tob in temperatures:
        dict = {}
        dict[date] = tob
        all_tobs.append(dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def calculated_temps(start):

    year = int(start[:4])
    month = int(start[5:7])
    day = int(start[8:])
    start_date = dt.datetime(year, month, day)

    temperatures = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    where(Measurement.date >= start_date).all()

    session.close()

    return jsonify(list(np.ravel(temperatures)))


@app.route("/api/v1.0/<start>/<end>")
def temp_ranges(start, end):
    
    year = int(start[:4])
    month = int(start[5:7])
    day = int(start[8:])
    start_date = dt.datetime(year, month, day)  


    year = int(end[:4])
    month = int(end[5:7])
    day = int(end[8:])
    end_date = dt.datetime(year, month, day) + dt.timedelta(days=1)

    temperatures = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    where(and_(Measurement.date >= start_date, Measurement.date < end_date)).all()

    return jsonify(list(np.ravel(temperatures)))



if __name__ == '__main__':
    app.run(debug=True)
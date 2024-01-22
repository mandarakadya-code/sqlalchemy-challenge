# Import the dependencies.
import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify
from datetime import datetime

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# List all available API routes to users in the home page
@app.route("/")
def homePage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<\start_date\><br/>"
        f"/api/v1.0/<\start_date\>/<\end_date\><br/>"
    )

# API route that returns json object of precipitation data for the last one year
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    for row in session.query(measurement.date).order_by(measurement.date.desc()).first():
        recent_date = row
    recent_date = datetime.fromisoformat(recent_date)
    year_ago = recent_date - dt.timedelta(days=365)
    scores = session.query(measurement.date, measurement.prcp).filter(measurement.date > year_ago).all()
    session.close()
    prcp_list = []
    for score in scores:
        prcp_dict = {}
        prcp_dict[score[0]] = score[1]
        prcp_list.append(prcp_dict)
    
    return jsonify(prcp_list)

# API route that returns list of all distinct stations ids with names
@app.route("/api/v1.0/stations")
def stations():
    station_list = []
    session = Session(engine)
    station_result = session.query(station.name, measurement.station).filter(station.station == measurement.station).distinct().all()
    session.close()
    for result in station_result:
        station_dict = {}
        station_dict[result[1]] = result[0]
        station_list.append(station_dict)
    return jsonify(station_list)

# API route that returns tobs data for the most active station for the last one year
@app.route("/api/v1.0/tobs")
def tobs():
    tobs_list = []
    session = Session(engine)
    for row in session.query(measurement.date).order_by(measurement.date.desc()).first():
        recent_date = row
    recent_date = datetime.fromisoformat(recent_date)
    year_ago = recent_date - dt.timedelta(days=365)
    results = session.query(measurement.station, func.count(measurement.id).label("count")).filter(measurement.date > year_ago).group_by(measurement.station).order_by(desc("count"))
    max_station = results[0].station
    results_tobs = session.query(measurement.date, measurement.tobs).filter(measurement.station == max_station).filter(measurement.date > year_ago)
    session.close()
    for result in results_tobs:
        tobs_dict = {}
        tobs_dict[result.date] = [result.tobs]
        tobs_list.append(tobs_dict)
    print(len(tobs_list))
    return jsonify(tobs_list)

# API route that returns minimum, maximum and average temperature for a given start date by the user
@app.route("/api/v1.0/<start>")
def temparatureRange(start):
    temp_list = []
    session = Session(engine)
    temp_results = session.query(func.min(measurement.tobs).label('temp_min'), func.max(measurement.tobs).label('temp_max'), func.avg(measurement.tobs).label('temp_avg')).filter(measurement.date > start).all()
    session.close()
    for temp in temp_results:
        temp_dict = {}
        temp_dict["Minimum Temperature"] = [temp.temp_min]
        temp_dict["Maximum Temperature"] = [temp.temp_max]
        temp_dict["Average Temperature"] = [temp.temp_avg]
        temp_list.append(temp_dict)
    
    return jsonify(temp_list)

# API route that returns minimum, maximum and average temperature for a given start date and end date by the user
@app.route("/api/v1.0/<start>/<end>")
def temparatureRangeStartEnd(start, end):
    temp_list = []
    session = Session(engine)
    temp_results = session.query(func.min(measurement.tobs).label('temp_min'), func.max(measurement.tobs).label('temp_max'), func.avg(measurement.tobs).label('temp_avg')).filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()
    for temp in temp_results:
        temp_dict = {}
        temp_dict["Minimum Temperature"] = [temp.temp_min]
        temp_dict["Maximum Temperature"] = [temp.temp_max]
        temp_dict["Average Temperature"] = [temp.temp_avg]
        temp_list.append(temp_dict)
    
    return jsonify(temp_list)


if __name__ == '__main__':
    app.run(debug=True)

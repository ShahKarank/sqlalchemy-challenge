#Import the necessary modules
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#Engine Creation and Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)


# Flask Setup
app = Flask(__name__)

@app.route("/")
def home():
	return (
		f"Available Routes:<br/>"
        f"/<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;</br>"
	)

@app.route("/api/v1.0/precipitation")
def precipitation():
	results = session.query(measurement).all()
	session.close()


	prcp = []
	for result in results:
		prcp = {}
		prcp["date"] = result.date
		prcp["prcp"] = result.prcp
		prcp.append(prcp)
	
	return jsonify(prcp)

@app.route("/api/v1.0/stations")
def stations_json():
    # Return a JSON list of stations
    session = Session(engine)
    stations_data = session.query(station.station).all()
    session.close()
    stations_list = list(stations_data)
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def temperature():
	  # Returns JSONified data of temperature observations from the previous year 
    session = Session(engine)
    last_row = session.query(measurement).order_by(measurement.date.desc()).first()
    last_date = last_row.date
    first_date = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    tobs_data = session.query(measurement.date, measurement.tobs).\
            filter(measurement.station == 'USC00519281').\
            filter(measurement.date > first_date).all()
    session.close()
    tobs_df = pd.DataFrame(tobs_data)
    tobs_dict = dict(zip(tobs_df['date'],tobs_df['tobs']))
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def single_date(start):
	Start_Date = dt.datetime.strptime(start,"%Y-%m-%d")

	summary_stats = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.round(func.avg(measurement.tobs))).\
	filter(measurement.date >= Start_Date).all()
	session.close() 
	
	summary = list(np.ravel(summary_stats))

	return jsonify(summary)


@app.route("/api/v1.0/<start>/<end>")
def trip_dates(end):
	Start_Date = dt.datetime.strptime("%Y-%m-%d")
	End_Date = dt.datetime.strptime(end,"%Y-%m-%d")
	summary_stats = session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.round(func.max(measurement.tobs))).\
	filter(measurement.date.between(Start_Date,End_Date)).all()
	
	session.close()    

	summary = list(np.ravel(summary_stats))

	return jsonify(summary)

	if __name__ == "__main__":
		app.run(debug=True)

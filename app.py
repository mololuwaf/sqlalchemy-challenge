# IMPORT FLASK 
from flask import Flask, jsonify 

import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


# DATABASE SETUP

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
session = Session(engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# FLASK SETUP
app = Flask(__name__)

# FLASK ROUTES
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return "Welcome to my 'Home' page*"

#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    pcp_1 = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > '2016-08-22').\
    order_by(Measurement.date).all()
    session.close()
    pcp_1_dict = {Date:Prcp for Date,Prcp in pcp_1}
    answer = jsonify(pcp_1_dict)
    return answer

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stations_1 = session.query(Station.station).all()
    session.close()
    stations_1_list = list(np.ravel(stations_1))  
    answer_2 = jsonify(stations_1_list)
    return answer_2

#Query the dates and temperature observations of the most-active station for the previous year of data.
#Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
# Query the last year of temperature observation data for the most active station
    start_date = '2016-08-23'
    sel = [Measurement.date, 
        Measurement.tobs]
    temperature_data_USC00519281 = session.query(*sel).\
            filter(Measurement.date >= start_date, Measurement.station == 'USC00519281').\
            group_by(Measurement.date).\
            order_by(Measurement.date).all()

    session.close()

    # Dictionary with the date as key and the daily temperature observation as value
    date_1 = []
    temp_observation_1 = []

    for date, observation in temperature_data_USC00519281:
        date_1.append(date)
        temp_observation_1.append(observation)
    
    tobs_dict = dict(zip(date_1, temp_observation_1))

    return jsonify(tobs_dict)

#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
@app.route("/api/v1.0/<start>")
def DYNAMIC1(start):
    session = Session(engine)
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    tobs_stat = []
    for min,avg,max in query_result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_stat.append(tobs_dict)

    return jsonify(tobs_stat)

#JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route('/api/v1.0/<start>/<end>')
def get_t_start_stop(start,end):
    session = Session(engine)
    query_result_2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    tobs_stat = []
    for min,avg,max in query_result_2:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_stat.append(tobs_dict)

    return jsonify(tobs_stat)
if __name__ == '__main__':
    app.run(debug=True)


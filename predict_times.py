import pandas as pd
import numpy as np
import requests
import xmltodict
from datetime import datetime, timedelta
from sklearn.externals import joblib
import oci_file_read as ofr

# import modules.readingbusesapi as busWrapper
#
# busAPI = busWrapper.ReadingBusesAPI("hvOtkiqAwK")

def predict_times(busAPI, stop_name):
    model = joblib.load("model.pkl")
    print("predict 1")
    csv_file = ofr.read_csv("avg_time_from_prev_stop.csv")
    print("predict 2")
    avg_times = pd.read_csv(csv_file, index_col=0)
    print("predict 3")
    stops = pd.DataFrame(busAPI.RequestAllStops())
    print("predict 4")
    stop_code = stops[stops.description == stop_name].location_code.item()
    print("predict 5")

    #get list of buses coming to the stop
    url = "https://rtl2.ods-live.co.uk//api/siri/sm?key=hvOtkiqAwK&location=" + stop_code
    response = requests.get(url)
    stop_predict = xmltodict.parse(response.content)
    print("predict 5.5")
    df_temp = pd.DataFrame(i['MonitoredVehicleJourney'] for i in stop_predict['Siri']
                                                                 ['ServiceDelivery']['StopMonitoringDelivery'][
                                                                     'MonitoredStopVisit'][:5])
    monitored_call_df = pd.DataFrame(i for i in df_temp.MonitoredCall)
    stop_predict_df = pd.DataFrame({'LineRef': df_temp.LineRef,
                                    'VehicleRef': [s[4:] if not isinstance(s, float) else 0 for s in
                                                   df_temp.VehicleRef]})
    stop_predict_df = stop_predict_df.join(monitored_call_df)
    stop_predict_df = stop_predict_df[stop_predict_df.ExpectedArrivalTime != 'cancelled']
    print("predict 5.6")
    #get the last stop that each bus passed through and the delay at that stop
    today = datetime.today().strftime('%Y-%m-%d')
    track_history = [busAPI.Call("TrackingHistory", {"date": today, "vehicle": vehicle})
                     if vehicle != 0 else None for vehicle in stop_predict_df.VehicleRef]
    # stop_predict_df['last_stop'] = [getLastStop(vehicle, today, bus_api)
    # #                                 hist[-1]['LocationName'] if type(hist) is list else "Not known"
    # #                                 for hist in [bus_api.Call("TrackingHistory", {"date": today, "vehicle": vehicle})
    #                                if vehicle != 0 else "Not Known" for vehicle in stop_predict_df.VehicleRef]#]
    print("predict 5.7")
    stop_predict_df['last_stop'] = [hist[-1]['LocationName'] if type(hist) is list else "Not known"
                                    for hist in track_history]
    stop_predict_df['last_stop_delay'] = [(pd.to_datetime(hist[-1]['DepartureTime']) -
                                           pd.to_datetime(hist[-1]['ScheduledDepartureTime'])).total_seconds()
                                          if hist is not None else 0
                                          for hist in track_history]

    print("predict 6")
    #get the next stop that each bus will go to
    stop_predict_df['route'] = [pd.DataFrame(busAPI.Call("Route", {"service": bus}))
                                for bus in stop_predict_df.LineRef]
    print(stop_predict_df.route)
    stop_predict_df['next_stop'] = [r.location_name[(r[r.location_name == stop_predict_df.last_stop[i]].index + 1) % len(r)].values[0]
                                    if stop_predict_df.last_stop[i] != 'Not known' else 'Not known'
                                    for i, r in enumerate(stop_predict_df.route)]

    #get features for the stop
    features = [predict_to_end(model, avg_times[avg_times.route_code == route], stop_name, next_stop, last_stop_delay, route)
                if vehicle_code != 0 else None
                for next_stop, last_stop_delay, route, vehicle_code in
                zip(stop_predict_df.next_stop, stop_predict_df.last_stop_delay, stop_predict_df.route,
                    stop_predict_df.VehicleRef)]

    predicted_delay = pd.to_timedelta(model.predict(features), unit='s')
    aimed_time = pd.to_datetime(stop_predict_df.AimedArrivalTime)
    print(type((aimed_time+predicted_delay).dt.time))

    predicted_buses_time = {}
    for i, (bus_code, time) in enumerate(zip(stop_predict_df.LineRef, (aimed_time + predicted_delay).dt.time)):
        predicted_buses_time[i] = (bus_code, time.strftime("%H:%M"))

    return predicted_buses_time


def predict_to_end(model, avg_times, end_stop, next_stop, last_delay, route):
    # print('--------------------------------------')
    delay = last_delay
    while (next_stop != end_stop):
        # print(delay)
        # check for the route also when finding the average time
        avg_time = avg_times[avg_times.location_name == next_stop].avg_time_from_prev.values[0]
        # print(avg_time)
        delay = model.predict(np.array([delay, avg_time]).reshape(1, -1))[0]

        # print(delay)
        # get next stop from route?
        next_stop = route.location_name[(route[route.location_name == next_stop].index + 1) % len(route)].values[0]
        # print(next_stop)
    avg_time = avg_times[avg_times.location_name == next_stop].avg_time_from_prev.values[0]
    return delay, avg_time

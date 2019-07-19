import pandas as pd
import numpy as np
import requests, re
import xmltodict
from datetime import datetime, timedelta
from sklearn.externals import joblib
import oci_file_read as ofr

# import modules.readingbusesapi as busWrapper
#
# busAPI = busWrapper.ReadingBusesAPI("hvOtkiqAwK")

def predict_times(busAPI, stop_code):
    print("predict 1")
    csv_file = ofr.read_csv("avg_time_from_prev_stop.csv")
    print("predict 2")
    avg_times = pd.read_csv(csv_file, dtype={'location_code': str})
    print("predict 3")
    stops = pd.DataFrame(busAPI.RequestAllStops())
    print("predict 4")
    # stop_code = stops[stops.description == stop_name].location_code.iloc[0]
    print("predict 5")

    #get list of buses coming to the stop
    url = "https://rtl2.ods-live.co.uk//api/siri/sm?key=hvOtkiqAwK&location=" + stop_code
    response = requests.get(url)
    stop_predict = xmltodict.parse(response.content)
    print(type(stop_predict['Siri']['ServiceDelivery']['StopMonitoringDelivery']))
    if 'MonitoredStopVisit' in stop_predict['Siri']['ServiceDelivery']['StopMonitoringDelivery'].keys() and len(
            stop_predict['Siri']['ServiceDelivery']['StopMonitoringDelivery']) > 1:
        df_temp = pd.DataFrame(i['MonitoredVehicleJourney'] for i in stop_predict['Siri']
                                                                     ['ServiceDelivery']['StopMonitoringDelivery'][
                                                                         'MonitoredStopVisit'][:5])
    else:
        df_temp = pd.DataFrame()
        return {0: (0,0)}

    monitored_call_df = pd.DataFrame(i for i in df_temp.MonitoredCall)

    stop_predict_df = pd.DataFrame({'LineRef': df_temp.LineRef,
                                    'VehicleRef': [re.findall('\d+', str(s)) if s != 'NaN' else None for s in
                                                   df_temp.VehicleRef],
                                    'Direction': ['0' if direction == 'outbound' else '1' for direction in
                                                  df_temp.DirectionRef]})
    stop_predict_df['VehicleRef'] = [ref[0] if len(ref) > 0 else None for ref in stop_predict_df.VehicleRef]
    stop_predict_df = stop_predict_df.loc[stop_predict_df.VehicleRef.notnull()]

    stop_predict_df = stop_predict_df.join(monitored_call_df)
    stop_predict_df = stop_predict_df[stop_predict_df.ExpectedArrivalTime != 'cancelled']
    if 'ArrivalStatus' in stop_predict_df.columns:
        stop_predict_df = stop_predict_df[stop_predict_df.ArrivalStatus != 'cancelled']

    print("predict 5.6")
    #get the last stop that each bus passed through and the delay at that stop
    last_stop_info = [get_last_stop_info(vehicle_no, route_no, busAPI) for route_no, vehicle_no
                      in zip(stop_predict_df.LineRef, stop_predict_df.VehicleRef)]


    print("predict 5.7")
    stop_predict_df['last_stop'] = [stop_info['Location'] for stop_info in last_stop_info]
    stop_predict_df['last_stop_delay'] = [(pd.to_datetime(stop_info['DepartureTime']) -
                                           pd.to_datetime(stop_info['ScheduledDepartureTime'])).total_seconds()
                                          for stop_info in last_stop_info]
    stop_predict_df = stop_predict_df.reset_index()

    print("predict 6")
    #get the next stop that each bus will go to
    stop_predict_df['route'] = [pd.DataFrame(busAPI.Call("Route", {"service": bus}))
                                for bus in stop_predict_df.LineRef]
    #print(stop_predict_df.route)
    stop_predict_df['next_stop'] = [r.location_code[(r[r.location_code == stop_predict_df.last_stop[i]].index + 1) % len(r)].values[0]
                                if (stop_predict_df.last_stop[i] != None and len(r.location_code[(r[r.location_code == stop_predict_df.last_stop[i]].index + 1) % len(r)]) != 0)
                                else None
                                for i, r in enumerate(stop_predict_df.route)]
    stop_predict_df = stop_predict_df.fillna(0)

    # print(stop_predict_df.next_stop)

    #get the models that are needed
    models = []
    for r in stop_predict_df.LineRef:
        try:
            m = ofr.read_model('model-' + r + '.pkl')
            models.append(joblib.load(m))
        except IOError:
            m = ofr.read_model('model-17.pkl')
            models.append(joblib.load(m))

    # print(stop_predict_df.VehicleRef)
    # print(stop_predict_df.next_stop)

    #get features for the stop
    features = [predict_to_end(model, avg_times, stop_code, next_stop, last_stop_delay, route, line_code)
                if (vehicle_code != 0 and next_stop != 'Not known')
                else (0, avg_times[avg_times.route_code == line_code][avg_times.location_code == stop_code].avg_time_from_prev)
                for next_stop, last_stop_delay, route, vehicle_code, line_code, model in
                zip(stop_predict_df.next_stop, stop_predict_df.last_stop_delay, stop_predict_df.route,
                    stop_predict_df.VehicleRef, stop_predict_df.LineRef, models)]

    predicted_delay = []
    for i, model in enumerate(models):
        print(features[i], type(features[i]))
        val = model.predict(np.array(features[i]).reshape(1, -1))[0]
        print(type(val))
        predicted_delay.append(val)

    # predicted_delay = [d[0] for d in predicted_delay]
    predicted_delay = pd.to_timedelta(predicted_delay, unit='s')

    aimed_time = pd.to_datetime(stop_predict_df.AimedArrivalTime)
    #print(type((aimed_time+predicted_delay).dt.time))

    predicted_buses_time = {}
    for i, (bus_code, time) in enumerate(zip(stop_predict_df.LineRef, (aimed_time + predicted_delay).dt.time)):
        predicted_buses_time[i] = (bus_code, time.strftime("%H:%M"))

    return predicted_buses_time

def get_last_stop_info(vehicle_code, route_no, api):
    hist = api.Call("LiveJourney", {"vehicle": vehicle_code, "route": route_no})
    next_stop_id = 0
    if type(hist) is list:
        visits = hist[0]['visits']
    else:
        visits = hist['visits']
    for visit in visits:
#         display(visit)
        if visit['DepartureStatus'] == 'E':
            next_stop_id = visits.index(visit)
#             display(next_stop_id)
            break
    if next_stop_id == 0:
        return visits[0]
    else:
        return visits[next_stop_id - 1]

def predict_to_end(model, avg_times, end_stop, next_stop, last_delay, route, route_code):
    # print('--------------------------------------')
    delay = last_delay
    while (next_stop != end_stop):
        # print(delay)
        # check for the route also when finding the average time
        avg_time = avg_times[avg_times.route_code == route_code][avg_times.location_code == next_stop].avg_time_from_prev
        # print(avg_time)
        delay = model.predict(np.array([delay, avg_time]).reshape(1, -1))[0]

        # print(delay)
        # get next stop from route?
        next_stop = route.location_code[(route[route.location_code == next_stop].index + 1) % len(route)].values[0]
        # print(next_stop)
    avg_time = avg_times[avg_times.route_code == route_code][avg_times.location_code == next_stop].avg_time_from_prev
    return delay, avg_time

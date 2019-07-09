# Importing Modules
import requests

# Modules importing Finished
# Bus Stops, Vehicle Position, Services, Line Patterns (Route)

# Stop Predictions, Timetabled Journeys, Tracking History, Vehicle Position History




# The Stop prediction returns an xml file, WHAT?
#

class ReadingBusesAPI:
    apis = {
        "Stops" : {
            "url" : "https://rtl2.ods-live.co.uk//api/busstops",
            "args": ["key"],
        },
        "Buses" : {
            "url" : "https://rtl2.ods-live.co.uk//api/vehiclePositions",
            "args": ["key"],
        },
        "LiveJourney" : {
            "url" : "https://rtl2.ods-live.co.uk//api/liveJourneys",
            "args": ["key", "vehicle", "route"],
        },
        "Route" : {
            "url" : "https://rtl2.ods-live.co.uk//api/linePatterns",
            "args": ["key", "service"],
        },
        "Services" : {
            "url" : "https://rtl2.ods-live.co.uk//api/services",
            "args": ["key"],
        },
        "Timetable" : {
            "url" : "https://rtl2.ods-live.co.uk/api/scheduledJourneys",
            "args": ["key", "service", "date", "location"],
        },
        "TrackingHistory" : {
            "url" :"https://rtl2.ods-live.co.uk/api/trackingHistory",
            "args": ["key", "vehicle", "date", "location"],
        },
        "BusesHistory" : {
            "url" : "https://rtl2.ods-live.co.uk/api/vehiclePositionHistory",
            "args": ["key", "date", "vehicle", "from", "to"]
        }
    }

    def __init__(self, apiKey):
        self.key = apiKey

    def Call(self, apiType, data):
        if apiType in self.apis:

            PARAMS = {}

            for key in self.apis[apiType]["args"]:
                if key in data:
                    if key == "key":
                        PARAMS[key] = self.key
                    else:
                        PARAMS[key] = data[key]

            # sending get request and saving the response as response object
            r = requests.get(url = self.apis[apiType]["url"], params = PARAMS)

            # extracting data in json format
            data = r.json()
            return data
        else:
            print("Seems like this is not a valid API Call")
            return False

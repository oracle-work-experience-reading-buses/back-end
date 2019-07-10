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

    def RequestTimeTable(self, service, date, busStop):
        # Service should be sent in like 702, not sure how that relates to number on the bus
        # Service seems to match for example 2A = 2a so just string upper stuff?

        # The date needs to be in yyyy-mm-dd if it is not in this format we will need to convert it
        busStops = self.RequestAllStops()
        busStopNatMap = False

        for i in busStops:
            if i["description"] == busStop:
                busStopNatMap = i["location_code"]
        if busStopNatMap:
            return self.Call("Timetable", {"location": busStopNatMap, "date": date, "service": service })
        else:
            return self.Call("Timetable", {"date": date, "service": service })

    def RequestAllStops(self):
        # Possibily cache this?
        return self.Call("Stops", {})

    def RequestBusPositions(self, service = False):
        busArray = self.Call("Buses", {})
        if service:
            busArrayTwo = []
            for bus in busArray:
                if bus["service"] == service:
                    busArrayTwo.append(bus)
            return busArrayTwo
        else:
            return busArray


busAPI = ReadingBusesAPI("apiKey")
data = busAPI.RequestBusPositions("2")
f = open("buslist2.txt", "w")
f.write(str(data))
f.close()

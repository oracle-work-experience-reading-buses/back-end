import modules.readingbusesapi as busWrapper

busAPI = busWrapper.ReadingBusesAPI("apiKey")

def RequestTimeTable(service, date, busStop):
    # Service should be sent in like 702, not sure how that relates to number on the bus
    # Service seems to match for example 2A = 2a so just string upper stuff?

    # The date needs to be in yyyy-mm-dd if it is not in this format we will need to convert it

    busStops = RequestAllStops()
    busStopNatMap = False

    for i in busStops:
        if i["description"] == busStop:
            busStopNatMap = i["location_code"]
    if busStopNatMap:
        return busAPI.Call("Timetable", {"location": busStopNatMap, "date": date, "service": service })
    else:
        return busAPI.Call("Timetable", {"date": date, "service": service })

def RequestAllStops():
    # Possibily cache this?
    return busAPI.Call("Stops", {})

def RequestBusPositions(service = False):
    busArray = busAPI.Call("Buses", {})
    if service:
        busArrayTwo = []
        for bus in busArray:
            if bus["service"] == service:
                busArrayTwo.append(bus)
        return busArrayTwo
    else:
        return busArray

data = RequestBusPositions("2a")
f = open("buslist.txt", "w")
f.write(str(data))
f.close()

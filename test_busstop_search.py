import modules.readingbusesapi as busWrapper
import WazeRouteCalculator

busAPI = busWrapper.ReadingBusesAPI("OHYrhd9WoJ")

date = "2019-07-10"
service = "2"



data = busAPI.FetchBusStop("Mary")

if data:
    f = open("mary.txt", "w")
    f.write(str(data))
    f.close()
else:
    print("DAM IT")

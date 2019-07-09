import sys
import modules.readingbusesapi as busWrapper

busAPI = busWrapper.ReadingBusesAPI("apiKey")
data = busAPI.Call("Stops", {'key': busAPI.key,})
f = open("data.txt", "w")
f.write(str(data))
f.close()

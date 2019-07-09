# Importing Modules
import requests

# Modules importing Finished

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
    }
    def __init__(self, apiKey):
        self.key = apiKey

    def Call(self, apiType, data):
        if apiType in self.apis:
            
            PARAMS = {}

            for key in self.apis[apiType]["args"]:
                if key in data:
                    PARAMS[key] = data[key]
  
            # sending get request and saving the response as response object 
            r = requests.get(url = self.apis[apiType]["url"], params = PARAMS) 

            # extracting data in json format 
            data = r.json()
            return data
            #return urllib.request.urlopen(self.apis[apiType] + self.key).read()
        else:
            print("Seems like this is not a valid API Call")
            return False

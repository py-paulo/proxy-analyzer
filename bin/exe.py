import json
import urllib.request

URI = 'http://paulo-pc:8001'

newConditions = {"con1": 40, "con2": 20, "con3": 99, "con4": 40, "password": "1234"}
params = json.dumps(newConditions).encode('utf8')

req = urllib.request.Request(URI, data=params,
                             headers={'content-type': 'application/json'})
response = urllib.request.urlopen(req)
print(response.read())

import requests, json
data= {'outer': { 'inner': 'value'}}
url="http://localhost:10080"
res=requests.post(url,data=json.dumps(data))

print(res.json())

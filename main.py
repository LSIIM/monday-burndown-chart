import http.client
import json
from definitions import TOKEN

conn = http.client.HTTPSConnection("api.monday.com")

payload = "{\"query\":\"{\\n  boards(limit: 1, ids: [6968247635]) {\\n    name\\n    id\\n    items_page {\\n      items {\\n        name\\n        column_values {\\n          value\\n          text\\n          type\\n          column {\\n            title\\n          }\\n        }\\n      }\\n    }\\n  }\\n}\"}"

headers = {
    'Content-Type': "application/json",
    'Authorization': TOKEN
    }

conn.request("POST", "/v2", payload, headers)

res = conn.getresponse()
data = res.read()

print(json.loads(data.decode("utf-8")))
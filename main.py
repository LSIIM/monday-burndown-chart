import http.client
import json
from definitions import TOKEN

conn = http.client.HTTPSConnection("api.monday.com")

payload = "{\"query\":\"{\\n  boards(limit: 1, ids: [6968247635]) {\\n    name\\n    id\\n    items_page {\\ncursor\\n      items {\\n        name\\n        column_values {\\n          value\\n          text\\n          type\\n          column {\\n            title\\n          }\\n        }\\n      }\\n    }\\n  }\\n}\"}"

headers = {
    'Content-Type': "application/json",
    'Authorization': TOKEN
    }

conn.request("POST", "/v2", payload, headers)

res = conn.getresponse()
data = res.read()

resp = json.loads(data.decode("utf-8"))["data"]

cursor = resp["boards"][0]["items_page"]["cursor"]
itens = []
itens.extend(resp["boards"][0]["items_page"]["items"])
while cursor != "null" and cursor != None and cursor != "" and cursor != " " and cursor!="None":
    payload = "{\"query\":\"{\\n  boards(limit: 1, ids: [6968247635]) {\\n    name\\n    id\\n    items_page(cursor: \\\""+cursor+"\\\") {\\ncursor\\n      items {\\n        name\\n        column_values {\\n          value\\n          text\\n          type\\n          column {\\n            title\\n          }\\n        }\\n      }\\n    }\\n  }\\n}\"}"
    conn.request("POST", "/v2", payload, headers)
    res = conn.getresponse()
    data = res.read()
    resp = json.loads(data.decode("utf-8"))["data"]
    cursor = resp["boards"][0]["items_page"]["cursor"]
    print(cursor)
    itens.extend(resp["boards"][0]["items_page"]["items"])

print(len(itens))

print()

# desenhar o grafico com plotly (x: data, y1: dificuldade dado pelo "Prazo", y2: dificuldade dado pelo "Done Date")

# data, dificuldade
prazo_dificuldade = []
done_date_dificuldade = []

for item in itens:
    prazo = ""
    dificuldade = 0
    done_date = ""
    if item["column_values"][1]["value"] != '' and not (item["column_values"][3]["text"] == '' or item["column_values"][3]["text"] == None or item["column_values"][3]["text"] == 'null' or item["column_values"][3]["text"] == '0'):
        prazo = item["column_values"][1]["text"]
        dificuldade = float(item["column_values"][3]["text"])
        if item["column_values"][5]["value"] is not None:
                done_date = item["column_values"][5]["text"]
        else:
            done_date = prazo
        prazo_dificuldade.append((prazo, dificuldade))
        done_date_dificuldade.append((done_date, dificuldade))
    

# agrega por dada (soma)

prazo_dificuldade_agregado = []
for i in prazo_dificuldade:
    if i[0] not in [j[0] for j in prazo_dificuldade_agregado]:
        prazo_dificuldade_agregado.append((i[0],sum([j[1] for j in prazo_dificuldade if j[0] == i[0]])))
done_date_dificuldade_agregado = []
for i in done_date_dificuldade:
    if i[0] not in [j[0] for j in done_date_dificuldade_agregado]:
        done_date_dificuldade_agregado.append((i[0], sum([j[1] for j in done_date_dificuldade if j[0] == i[0]])))




# grafico
import plotly.express as px

prazo_dificuldade_agregado = sorted(prazo_dificuldade_agregado, key=lambda x: x[0])
done_date_dificuldade_agregado = sorted(done_date_dificuldade_agregado, key=lambda x: x[0])

print(prazo_dificuldade_agregado)
print(done_date_dificuldade_agregado)

# grafico cumuliativo

prazo_dificuldade_agregado_cum = []
done_date_dificuldade_agregado_cum = []

for i in range(len(prazo_dificuldade_agregado)):
    prazo_dificuldade_agregado_cum.append((prazo_dificuldade_agregado[i][0], sum([j[1] for j in prazo_dificuldade_agregado[:i]])))

for i in range(len(done_date_dificuldade_agregado)):
    done_date_dificuldade_agregado_cum.append((done_date_dificuldade_agregado[i][0], sum([j[1] for j in done_date_dificuldade_agregado[:i]])))

prazo_dificuldade_agregado_cum = sorted(prazo_dificuldade_agregado_cum, key=lambda x: x[0])
done_date_dificuldade_agregado_cum = sorted(done_date_dificuldade_agregado_cum, key=lambda x: x[0])

fig = px.line(title="Burndown Chart AgroSmart",
              labels={"x":"Data", "y":"Dificuldade (Horas)"}, template="plotly_dark")

fig.add_scatter(x=[i[0] for i in prazo_dificuldade_agregado_cum], y=[i[1] for i in prazo_dificuldade_agregado_cum], mode='lines', name="Dificuldade Prevista (Acumulada)")

fig.add_scatter(x=[i[0] for i in done_date_dificuldade_agregado_cum], y=[i[1] for i in done_date_dificuldade_agregado_cum], mode='lines', name="Dificuldade Realizada (Acumulada)")


# salva como png em /burndown/burndown_TODAY_DATE.png

import os
import datetime

today = datetime.datetime.now().strftime("%Y-%m-%d")
if not os.path.exists("burndown"):
    os.makedirs("burndown")
# imagem em png com resolução de height=1000 e width=2000
fig.write_image("burndown/burndown_"+today+".png", height=1000, width=2000)
print("burndown/burndown_"+today+".png")



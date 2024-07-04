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
# exemplo de item
# "items": [
#     {
#         "name": "MAYBE Verificar com o ASSETS os arquivos geojson para verificar se mostra ou não os botões de Layer de Detecção WebODM",
#         "column_values": [
#             {
#                 "value": null,
#                 "text": "",
#                 "type": "text",
#                 "column": {
#                     "title": "Responsável"
#                 }
#             },
#             {
#                 "value": "{\"date\":\"2024-07-18\",\"changed_at\":\"2024-07-04T20:20:23.776Z\"}",
#                 "text": "2024-07-18",
#                 "type": "date",
#                 "column": {
#                     "title": "Prazo"
#                 }
#             },
#             {
#                 "value": "{\"index\":0,\"post_id\":null}",
#                 "text": "Em andamento",
#                 "type": "status",
#                 "column": {
#                     "title": "Status"
#                 }
#             },
#             {
#                 "value": "\"2\"",
#                 "text": "2",
#                 "type": "numbers",
#                 "column": {
#                     "title": "Dificuldade (Horas)"
#                 }
#             },
#             {
#                 "value": "\"Thigz Zero, Fábio\"",
#                 "text": "Thigz Zero, Fábio",
#                 "type": "text",
#                 "column": {
#                     "title": "Resp_temp"
#                 }
#             },
#             {
#                 "value": null,
#                 "text": "",
#                 "type": "date",
#                 "column": {
#                     "title": "Done date"
#                 }
#             },
#             {
#                 "value": "{\"tag_ids\":[23361983]}",
#                 "text": "Plataforma-AgroSmart",
#                 "type": "tags",
#                 "column": {
#                     "title": "Área"
#                 }
#             }
#         ]
#     },
# ]

# data, dificuldade
prazo_dificuldade = []
done_date_dificuldade = []

for item in itens:
    prazo = ""
    dificuldade = 0
    done_date = ""
    if item["column_values"][1]["value"] is not None and (item["column_values"][3]["text"] != ''):
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


print(prazo_dificuldade_agregado)
print(done_date_dificuldade_agregado)

# grafico
import plotly.express as px

prazo_dificuldade_agregado = sorted(prazo_dificuldade_agregado, key=lambda x: x[0])
done_date_dificuldade_agregado = sorted(done_date_dificuldade_agregado, key=lambda x: x[0])

# linha de prazo
fig = px.line(x=[i[0] for i in prazo_dificuldade_agregado], y=[i[1] for i in prazo_dificuldade_agregado], title='Dificuldade por prazo', labels={'x':'Data', 'y':'Dificuldade'})
fig.add_scatter(x=[i[0] for i in done_date_dificuldade_agregado], y=[i[1] for i in done_date_dificuldade_agregado], mode='lines', name='Done date')

fig.show()

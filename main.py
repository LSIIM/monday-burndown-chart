import requests

# Defina o URL da API GraphQL
url = 'https://your-graphql-api-endpoint.com/graphql'

# Defina o token de autorização
token = 'seu_token_aqui'

# Defina o payload do corpo da requisição
query = """
{
  boards(limit: 1, ids: [6968247635]) {
    name
    id
    items_page {
      items {
        name
        column_values {
          value
          text
          type
          column {
            title
          }
        }
      }
    }
  }
}
"""

# Configurar os headers
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
}

# Fazer a requisição POST
response = requests.post(url, json={'query': query}, headers=headers)

# Verificar a resposta
if response.status_code == 200:
    print('Requisição bem-sucedida!')
    print('Resposta:', response.json())
else:
    print(f'Falha na requisição. Status code: {response.status_code}')
    print('Detalhes:', response.text)

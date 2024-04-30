import requests

def run_linear_graphql_query(query, api_key):
    url = "https://api.linear.app/graphql"
    headers = {
      "Content-Type": "application/json",
      "Authorization": api_key
    }
    data = {
      "query": query
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
      return response.json()
    else:
      print(f"Failed to run GraphQL query. Status code: {response.status_code}")
      return None
    
def run_linear_graphql_mutation(mutation, api_key):
    url = "https://api.linear.app/graphql"
    headers = {
      "Content-Type": "application/json",
      "Authorization": api_key
    }
    data = {
      "query": "mutation " + mutation
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
      return response.json()
    else:
      print(f"Failed to run GraphQL mutation. Status code: {response.status_code}")
      return None

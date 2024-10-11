import requests

# URL you want to fetch
url = 'https://affiliate.p.finance/en/statistics/detailed?uid=85615441'

# Sending a GET request
response = requests.get(url)

# Retrieving headers
headers = response.headers
print("Headers:", headers)

# # Retrieving body
# body = response.text
# print("Body:", body)

import json
total = 0
with open('data.json', 'r') as f:
  data = json.load(f)

print(data["700374484955299900"]['variables'])
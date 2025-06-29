import ast
import json
with open('foo.json', 'r') as f:
    data = ast.literal_eval(f.read())
with open('foo.json', 'w') as f:
    json.dump(data, f, indent=2)
  


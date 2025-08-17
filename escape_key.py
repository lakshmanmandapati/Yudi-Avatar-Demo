import json

# Path to your raw service account JSON
path = "yudi-avatar-82e734eb3f06.json"

with open(path, "r") as f:
    creds = json.load(f)

# Escape the private_key properly
creds["private_key"] = creds["private_key"].replace("\n", "\\n")

# Print the escaped JSON (copy this into your .env)
print(json.dumps(creds, indent=2))

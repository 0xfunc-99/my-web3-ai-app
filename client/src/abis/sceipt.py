import json
import os

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))

# Path to the UserDataStorage.json file
filepath = os.path.join(project_root, 'build', 'contracts', 'UserDataStorage.json')

print(f"Looking for contract at: {filepath}")

# Load the JSON file
with open(filepath, "r") as file:
    data = json.load(file)

# Extract the ABI
abi = data.get("abi", [])

# Save the ABI to a new file
output_path = os.path.join(current_dir, "UserDataStorage.json")
with open(output_path, "w") as abi_file:
    json.dump(abi, abi_file, indent=2)

print(f"ABI extracted and saved to: {output_path}")
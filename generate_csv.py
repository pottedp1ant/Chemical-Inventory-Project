import requests
import csv

# PubChem API query function to get SDS information based on CAS number
def query_sds(cas):
    base_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cas/{cas}/property/HazardousSubstance/JSON"
    
    try:
        # Send a GET request to the PubChem API
        response = requests.get(base_url)
        response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx, 5xx)
        
        # Check if the response contains valid data
        data = response.json()
        
        # Debug: print the raw response to check data format
        print(f"Response for CAS {cas}: {data}")
        
        if 'PropertyTable' in data and 'Properties' in data['PropertyTable']:
            # Extract hazardous properties from PubChem
            properties = data['PropertyTable']['Properties'][0]
            hazards = {
                'flammable': 'Flammable' in properties.get('HazardousSubstance', ''),
                'corrosive': 'Corrosive' in properties.get('HazardousSubstance', ''),
                'toxic': 'Toxic' in properties.get('HazardousSubstance', ''),
                'pyrophoric': 'Pyrophoric' in properties.get('HazardousSubstance', '')
            }
            return hazards
        else:
            print(f"No hazard data found for CAS {cas}.")  # Debug: print when no data is found
            return {}  # Return an empty dictionary if no hazard info is found
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {cas}: {e}")
        return {}

# Function to load CAS numbers from a file
def load_cas_numbers(file_path):
    try:
        with open(file_path, 'r') as file:
            cas_numbers = [line.strip() for line in file.readlines()]
        return cas_numbers
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []

# Load CAS numbers from the file
cas_numbers = load_cas_numbers('cas_numbers.txt')

# Debug: print the loaded CAS numbers
print(f"Loaded CAS numbers: {cas_numbers}")

# Hazard categories
hazard_categories = {
    "flammable": [],
    "corrosive": [],
    "toxic": [],
    "pyrophoric": [],
    "unclassified": []
}

# Process each CAS number
for cas in cas_numbers:
    print(f"Processing CAS {cas}...")  # Debug: print the CAS being processed
    hazards = query_sds(cas)
    if not hazards:
        hazard_categories["unclassified"].append(cas)
    else:
        for category in hazard_categories.keys():
            if category in hazards and hazards[category]:
                hazard_categories[category].append(cas)

# Debug: print the hazard categories to see what was classified
print("Hazard Categories:", hazard_categories)

# Write each category to a CSV file
for category, cas_list in hazard_categories.items():
    filename = f"{category}_chemicals.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["CAS Number", "Hazard Type"])  # Writing header
        for cas in cas_list:
            writer.writerow([cas, category])  # Writing CAS and hazard type

print("CSV files created for each hazard category.")
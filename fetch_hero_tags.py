import requests
import json
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

STRATZ_API_URL = "https://api.stratz.com/graphql"
OUTPUT_PATH = "data/hero_tags.json"

# Load token from environment
API_TOKEN = os.getenv("STRATZ_API_TOKEN")
if not API_TOKEN:
    raise ValueError("Missing STRATZ_API_TOKEN in environment or .env file.")

HEADERS = {
    "User-Agent": "STRATZ_API",
    "Authorization": f"Bearer {API_TOKEN}"
}

QUERY = """
{
  constants {
    heroRoleType {
      id
      name
    }
  }
  heroStats {
    id
    shortName
    roles
  }
}
"""

def fetch_hero_tags():
    print("Fetching hero tag data from Stratz...")
    response = requests.post(STRATZ_API_URL, json={'query': QUERY}, headers=HEADERS)
    response.raise_for_status()
    
    data = response.json().get('data')
    if not data:
        raise ValueError("No data received from Stratz API")

    role_lookup = {role['id']: role['name'] for role in data['constants']['heroRoleType']}
    hero_tags = {}

    for hero in data['heroStats']:
        short_name = hero['shortName']
        if not short_name:
            continue  # skip unnamed heroes

        stratz_tags = [role_lookup.get(role_id, f"Unknown({role_id})") for role_id in hero['roles']]
        hero_tags[short_name] = {
            "stratz_tags": stratz_tags,
            "custom_tags": []
        }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(hero_tags, f, indent=2)
    print(f"Saved {len(hero_tags)} heroes to {OUTPUT_PATH}")

if __name__ == "__main__":
    fetch_hero_tags()


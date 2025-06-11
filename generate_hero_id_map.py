import os
import json
import requests
from dotenv import load_dotenv

# Load API token
load_dotenv()
token = os.getenv("STRATZ_API_TOKEN")

if not token:
    raise Exception("Missing STRATZ_API_TOKEN in .env")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

query = """
{
  constants {
    heroes {
      id
      displayName
      shortName
    }
  }
}
"""

def main():
    print("Fetching hero constants from Stratz...")
    res = requests.post("https://api.stratz.com/graphql", headers=headers, json={"query": query})
    res.raise_for_status()
    heroes = res.json()["data"]["constants"]["heroes"]

    # Build mapping: { "Axe": 2, "Beastmaster": 38, ... }
    hero_map = {hero["displayName"]: hero["id"] for hero in heroes}

    os.makedirs("data", exist_ok=True)
    with open("data/hero_name_to_id.json", "w") as f:
        json.dump(hero_map, f, indent=2)

    print(f"✅ Saved {len(hero_map)} heroes to data/hero_name_to_id.json")

if __name__ == "__main__":
    main()

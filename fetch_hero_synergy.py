import os
import json
import time
import requests
from dotenv import load_dotenv
import pprint

# Load .env API token
load_dotenv()
token = os.getenv("STRATZ_API_TOKEN")
if not token:
    raise Exception("Missing STRATZ_API_TOKEN in .env")

HEADERS = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

# Load hero pool and ID maps
with open("config/hero_pool.json") as f:
    hero_pool = json.load(f)

with open("data/hero_name_to_id.json") as f:
    name_to_id = json.load(f)
    id_to_name = {v: k for k, v in name_to_id.items()}

def fetch_hero_vs_data(hero_id):
    query = f"""
    {{
      heroStats {{
        heroVsHeroMatchup(heroId: {hero_id}) {{
          advantage {{
            with {{
              heroId2
              synergy
            }}
            vs {{
              heroId2
              synergy
            }}
          }}
          disadvantage {{
            with {{
              heroId2
              synergy
            }}
            vs {{
              heroId2
              synergy
            }}
          }}
        }}
      }}
    }}
    """
    response = requests.post("https://api.stratz.com/graphql", headers=HEADERS, json={"query": query})
    response.raise_for_status()
    data = response.json()

    try:
        # ✅ FIX: heroStats is a dict, not a list
        return data["data"]["heroStats"]["heroVsHeroMatchup"]
    except Exception as e:
        print("💥 Response shape unexpected:")
        pprint.pprint(data)
        raise e

def main():
    output = {}
    for hero_name in hero_pool:
        hero_id = name_to_id.get(hero_name)
        if not hero_id:
            print(f"⚠️  Skipping unknown hero: {hero_name}")
            continue

        print(f"🔍 Fetching synergy/matchups for {hero_name} (ID: {hero_id})")
        try:
            data = fetch_hero_vs_data(hero_id)

            # ✅ THESE NEED [0] BECAUSE THEY ARE LISTS
            advantage = data["advantage"][0]
            disadvantage = data["disadvantage"][0]

            synergy = {}
            for entry in advantage["with"]:
                name = id_to_name.get(entry["heroId2"])
                if name:
                    synergy[name] = round(entry["synergy"], 1)

            counters = {}
            for entry in advantage["vs"]:
                name = id_to_name.get(entry["heroId2"])
                if name:
                    counters[name] = round(entry["synergy"], 1)

            countered_by = {}
            for entry in disadvantage["vs"]:
                name = id_to_name.get(entry["heroId2"])
                if name:
                    countered_by[name] = round(entry["synergy"], 1)

            worst_synergy = {}
            for entry in disadvantage["with"]:
                name = id_to_name.get(entry["heroId2"])
                if name:
                    worst_synergy[name] = round(entry["synergy"], 1)

            output[hero_name] = {
                "synergy": synergy,
                "counters": counters,
                "countered_by": countered_by,
                "worst_synergy": worst_synergy
            }

        except Exception as e:
            print(f"❌ Error for {hero_name}: {e}")

        time.sleep(1)  # Respect rate limit

    os.makedirs("data", exist_ok=True)
    with open("data/hero_synergy_matchups.json", "w") as f:
        json.dump(output, f, indent=2)

    print("✅ Done! Saved to data/hero_synergy_matchups.json")

if __name__ == "__main__":
    main()

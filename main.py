import json
from typing import List, Dict

# Load hero tags (augmented manually or partially from OpenDota roles)
with open("data/hero_tags.json") as f:
    HERO_TAGS = json.load(f)

# Load user's hero pool and comfort levels
with open("config/hero_pool.json") as f:
    HERO_POOL = json.load(f)

def input_hero_list(prompt: str) -> List[str]:
    print(prompt)
    return [h.strip() for h in input("Comma-separated heroes: ").split(",")]

def get_missing_roles(team_picks: List[str]) -> List[str]:
    role_counts = {}
    for hero in team_picks:
        for tag in HERO_TAGS.get(hero, []):
            role_counts[tag] = role_counts.get(tag, 0) + 1

    desired_roles = ["Frontliner", "Disabler", "Initiator", "Tower Push", "Wave Clear"]
    missing_roles = [role for role in desired_roles if role_counts.get(role, 0) == 0]
    return missing_roles

def get_heroes_fulfilling_roles(roles: List[str], all_picked: set) -> Dict[str, List[str]]:
    result = {}
    for hero in HERO_POOL:
        if hero in all_picked:
            continue
        tags = HERO_TAGS.get(hero, [])
        matched = [r for r in roles if r in tags]
        if matched:
            result[hero] = matched
    return result

def get_attack_type(hero: str) -> str:
    tags = HERO_TAGS.get(hero, [])
    if "Melee" in tags:
        return "Melee"
    elif "Ranged" in tags:
        return "Ranged"
    return "Unknown"

def score_hero(hero: str, team_picks: List[str], enemy_picks: List[str]) -> float:
    tags = HERO_TAGS.get(hero, [])
    comfort = HERO_POOL.get(hero, "ok")

    role_score = 0
    synergy_score = 0

    missing_roles = get_missing_roles(team_picks)
    for role in tags:
        if role in missing_roles:
            role_score += 1

    comfort_mod = {"very_comfortable": 1.2, "comfortable": 1.1, "ok": 1.0, "learning": 0.8}
    base_score = (2 * role_score + synergy_score) * comfort_mod.get(comfort, 1.0)
    final_score = base_score

    return round(final_score, 2)

def suggest_heroes(team_picks: List[str], enemy_picks: List[str], missing_roles: List[str]) -> List[str]:
    all_picked = set(team_picks + enemy_picks)
    scores = {}
    details = {}
    for hero in HERO_POOL:
        if hero in all_picked:
            continue
        tags = HERO_TAGS.get(hero, [])
        score = score_hero(hero, team_picks, enemy_picks)
        scores[hero] = score
        fulfilled = [tag for tag in tags if tag in missing_roles]
        details[hero] = {
            "score": score,
            "tags": fulfilled,
            "atk": get_attack_type(hero)
        }
    sorted_heroes = sorted(details.items(), key=lambda x: x[1]["score"], reverse=True)
    return sorted_heroes

def count_attack_types(picks: List[str]) -> Dict[str, int]:
    counts = {"Melee": 0, "Ranged": 0}
    for hero in picks:
        atk = get_attack_type(hero)
        if atk in counts:
            counts[atk] += 1
    return counts

def summarize_roles(picks: List[str]) -> Dict[str, int]:
    role_counts = {}
    for hero in picks:
        for tag in HERO_TAGS.get(hero, []):
            role_counts[tag] = role_counts.get(tag, 0) + 1
    return role_counts

def print_role_summary(role_counts: Dict[str, int], title: str):
    print(f"\n{title} tags:")
    for role, count in sorted(role_counts.items(), key=lambda x: (-x[1], x[0])):
        if role not in ("Melee", "Ranged") and count > 0:
            print(f"{role.ljust(15)} {'+' * count}")

if __name__ == "__main__":
    print("Welcome to the Offlane Hero Picker!")
    team = input_hero_list("Enter your team's picks (excluding yourself):")
    enemy = input_hero_list("Enter enemy team's known picks:")

    print("\nAnalyzing team composition...")
    missing = get_missing_roles(team)
    print("\nTags to fulfill:")
    for r in missing:
        print(f"- {r}")

    atk_counts = count_attack_types(team)
    print("\nCurrent team attack type:")
    print(f"🗡️ {atk_counts['Melee']}  🏹 {atk_counts['Ranged']}")

    print_role_summary(summarize_roles(team), "Team")
    print_role_summary(summarize_roles(enemy), "Enemy")

    all_picked = set(team + enemy)
    heroes_that_fill = get_heroes_fulfilling_roles(missing, all_picked)
    print("\nHeroes that fill missing roles:")
    for hero, roles in heroes_that_fill.items():
        atk_icon = "🗡️" if get_attack_type(hero) == "Melee" else "🏹"
        print(f"{hero} {atk_icon}: {', '.join(roles)}")

    suggestions = suggest_heroes(team, enemy, missing)
    print("\nTop Hero Suggestions:")
    for hero, info in suggestions[:5]:
        atk_icon = "🗡️" if info['atk'] == "Melee" else "🏹"
        print(f"{hero} {atk_icon}: {info['score']} [{', '.join(info['tags'])}]")


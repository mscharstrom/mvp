import json
from typing import List, Dict

DEFAULT_DESIRED_ROLES = ["Frontliner", "Disabler", "Initiator", "Tower Push", "Wave Clear"]

# Load hero tags (augmented manually or partially from OpenDota roles)
with open("data/hero_tags.json") as f:
    HERO_TAGS = json.load(f)

# Load user's hero pool and comfort levels
with open("config/hero_pool.json") as f:
    HERO_POOL = json.load(f)

with open("data/hero_synergy_matchups.json") as f:
    HERO_MATCHUPS = json.load(f)

def input_hero_list(prompt: str) -> List[str]:
    print(prompt)
    return [h.strip() for h in input("Comma-separated heroes: ").split(",")]

def get_missing_roles(team_picks: List[str], desired_roles: List[str]) -> List[str]:
    role_counts = {}
    for hero in team_picks:
        for tag in HERO_TAGS.get(hero, []):
            role_counts[tag] = role_counts.get(tag, 0) + 1

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


def score_hero(hero: str, team_picks: List[str], enemy_picks: List[str], desired_roles: List[str]) -> float:
    tags = HERO_TAGS.get(hero, [])
    comfort = HERO_POOL.get(hero, "ok")
    matchups = HERO_MATCHUPS.get(hero, {})

    # Role score: 1 point if role is missing, 0.5 if already present
    missing_roles = get_missing_roles(team_picks, desired_roles)
    role_score = 0
    for role in tags:
        if role in desired_roles:
            if role in missing_roles:
                role_score += 1.0
            else:
                role_score += 0.5

    # Synergy: sum synergy with teammates
    synergy_score = 0
    for mate in team_picks:
        synergy_score += matchups.get("synergy", {}).get(mate, 0)

    # Counter score: how well we counter enemies
    counter_score = 0
    for enemy in enemy_picks:
        val = matchups.get("counters", {}).get(enemy, 0)
        if val > 0:
            counter_score += val

    # Countered-by score: how badly they counter us (expecting negative values)
    countered_score = 0
    for enemy in enemy_picks:
        val = matchups.get("countered_by", {}).get(enemy, 0)
        if val < 0:
            countered_score += val

    # Weighted total
    comfort_mod = {"very_comfortable": 1.3, "comfortable": 1.2, "ok": 1.1, "learning": 1.0}
    score = (
        1.0 * role_score +
        1.2 * synergy_score +
        1.5 * counter_score +
        1.0 * countered_score
    ) * comfort_mod.get(comfort, 1.0)

    return round(score, 2), {
        "role": round(role_score, 1),
        "synergy": round(synergy_score, 1),
        "counter": round(counter_score, 1),
        "countered_by": round(countered_score, 1),
        "comfort": round(comfort_mod.get(comfort, 1.0), 1)
    }

def suggest_heroes(team_picks: List[str], enemy_picks: List[str], missing_roles: List[str], desired_roles: List[str]) -> List[str]:
    all_picked = set(team_picks + enemy_picks)
    scores = {}
    details = {}
    for hero in HERO_POOL:
        if hero in all_picked:
            continue
        tags = HERO_TAGS.get(hero, [])
        score = score_hero(hero, team_picks, enemy_picks, desired_roles)
        scores[hero] = score
        fulfilled = [tag for tag in tags if tag in missing_roles]
        details[hero] = {
            "score": score,
            "tags": tags,
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
    for role in DEFAULT_DESIRED_ROLES:
        count = role_counts.get(role, 0)
        if count > 0:
            bar = "+" * count
            status = " (already covered)" if count > 1 else ""
            print(f"{role.ljust(15)} {bar}{status}")

if __name__ == "__main__":
    print("Welcome to the MVP - Most Valuable Pick!")
    team = input_hero_list("Enter your team's picks (excluding yourself):")
    enemy = input_hero_list("Enter enemy team's known picks:")

    print("\nAnalyzing team composition...")
    missing = get_missing_roles(team, DEFAULT_DESIRED_ROLES)
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

    suggestions = suggest_heroes(team, enemy, missing, DEFAULT_DESIRED_ROLES)
    print("\nTop Hero Suggestions (with synergy & counters):")
    for hero, info in suggestions[:5]:
        atk_icon = "🗡️" if info['atk'] == "Melee" else "🏹"
        matchups = HERO_MATCHUPS.get(hero, {})
        synergy_partners = matchups.get("synergy", {})
        counter_targets = matchups.get("counters", {})
        countered_by = matchups.get("countered_by", {})
        bad_synergies = matchups.get("worst_synergy", {})

        good_synergies = [(mate, synergy_partners[mate]) for mate in team if synergy_partners.get(mate, 0) > 0]
        bad_fits = [(mate, bad_synergies[mate]) for mate in team if bad_synergies.get(mate, 0) < 0]
        strong_counters = [(enemy_hero, counter_targets[enemy_hero]) for enemy_hero in enemy if counter_targets.get(enemy_hero, 0) > 0]
        weak_against = [(enemy_hero, countered_by[enemy_hero]) for enemy_hero in enemy if countered_by.get(enemy_hero, 0) < 0]

        print(f"\n{hero} {atk_icon}: {info['score']} [{', '.join(info['tags'])}]")

        if good_synergies:
            formatted = ', '.join(f"{name} (+{val})" for name, val in good_synergies)
            print(f"  🤝 Synergizes with: {formatted}")
        if bad_fits:
            formatted = ', '.join(f"{name} ({val})" for name, val in bad_fits)
            print(f"  🚫 Poor synergy with: {formatted}")
        if strong_counters:
            formatted = ', '.join(f"{name} (+{val})" for name, val in strong_counters)
            print(f"  🔥 Counters: {formatted}")
        if weak_against:
            formatted = ', '.join(f"{name} ({val})" for name, val in weak_against)
            print(f"  ⚠️ Countered by: {formatted}")

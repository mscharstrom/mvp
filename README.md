# 🧠 MVP – Most Valuable Pick

MVP is a Dota 2 hero suggestion tool that helps you draft the best possible hero based on:
- Team synergy
- Countering enemy picks
- Filling missing team roles
- Your personal hero comfort levels

It fetches synergy and matchup data from [Stratz's GraphQL API](https://stratz.com/) and enhances it with your custom preferences.

---

## 📁 Project Structure

```
.
├── config/
│   └── hero_pool.json             # Your personal hero pool + comfort levels
├── data/
│   ├── hero_tags.json             # Hero roles (Initiator, Frontliner, Ranged, etc.)
│   ├── hero_name_to_id.json       # Hero name ↔ ID map
│   └── hero_synergy_matchups.json # Matchup/synergy data (fetched via API)
├── main.py                        # Run this to get hero suggestions
├── fetch_hero_matchups.py         # Updates synergy/matchup data from Stratz
├── .env                           # Holds your STRATZ_API_TOKEN
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/mscharstrom/mvp.git
cd mvp
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Add Your STRATZ API Token

1. Go to https://stratz.com
2. Find your API token under your profile
3. Create a file called `.env` in the root folder and add:

```env
STRATZ_API_TOKEN=your_token_here
```

---

## 🧠 Setup: Customize Your Hero Preferences

### 1. `config/hero_pool.json`

List your hero pool and comfort levels:
```json
{
  "Axe": "very_comfortable",
  "Mars": "ok",
  "Slardar": "comfortable",
  "Dark Seer": "learning"
}
```

Accepted comfort levels:  
`very_comfortable`, `comfortable`, `ok`, `learning`

---

### 2. `data/hero_tags.json`

Tag each hero with their roles. Example:
```json
{
  "Axe": ["Frontliner", "Initiator", "Wave Clear", "Melee"],
  "Dazzle": ["Support", "Save", "Ranged"]
}
```

These tags are used to identify missing roles in your team and boost score accordingly. Add your own touch!

---

### 3. `data/hero_name_to_id.json`

This file should map hero names to their STRATZ hero IDs. It’s usually static, and you'll only need to update it when new heroes are added:
```json
{
  "Axe": 2,
  "Mars": 108,
  "Slardar": 28
}
```

Generate the file by running:

```bash
python map_hero_id.py
```

---

## 🔄 Fetch Synergy & Matchup Data

Run this script **before using the picker** to update local synergy/matchup data:

```bash
python fetch_hero_matchups.py
```

It queries STRATZ and saves the results to `data/hero_synergy_matchups.json` based on your hero pool.

---

## 🎮 Use the MVP Picker

```bash
python main.py
```

You’ll be prompted to:
- Enter your teammates (excluding yourself)
- Enter known enemy picks

MVP will then:
- Show missing roles in your team
- Suggest heroes from your pool that fit the team and counter the enemy
- Rank them based on synergy, counters, and your comfort level

---

## ✅ Example Output

```
Top Hero Suggestions (with synergy & counters):

Mars 🗡️: 8.7 [Frontliner, Initiator]
  🤝 Synergizes with: Lion
  🚫 Poor synergy with: Techies
  🔥 Counters: Phantom Assassin
  ⚠️ Countered by: Outworld Destroyer
```

---

## 🛠️ Optional Improvements

- Expand `hero_tags.json` with more/cleaner role tags
- Adjust scoring logic in `main.py` to suit your playstyle

---

## 💡 Why MVP?

You can use MVP whether you play offlane, mid, support, or carry. It’s **role-agnostic** and designed to help you make a confident, data-driven pick that fits your team and punishes the enemy.

---

## 📌 TODO

- Web interface/GUI for hero suggestion
- Improve scoring
- Improve hero tags
- Import live draft from Dota client
- Add synergy weight configuration
- Automatic STRATZ ID sync

---

## 🧠 Credits

- [STRATZ GraphQL API](https://docs.stratz.com)

---

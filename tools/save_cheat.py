import json
import sys

def modify_save(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    stats = data.get("save_data", {}).get("player_stats", {})
    stats["max_health"] = 999999
    stats["health"] = 999999
    stats["max_energy"] = 999999
    stats["energy"] = 999999
    stats["max_block"] = 999999
    stats["block"] = 0
    stats["break_damage"] = 999999.0
    stats["break_damage_modifier"] = 999999.0
    stats["on_beat_extra_damage"] = 999999.0
    stats["on_beat_extra_damage_modifier"] = 999999.0

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "autosave.gamesave"
    modify_save(target)

"""
stats.py - demo stats and badge tracker for Smart Waste.

Put this file in the project root, next to the badges/ and guides/ folders.

Every time something is scanned, call tracker.record_scan(bin_name). It:
  1. updates the counters (scanned / recycled / composted / garbage),
  2. saves them to stats.json so they survive a restart,
  3. works out which badges are earned,
  4. calls on_change(json_text), which should emit the backend's statsChanged
     signal. Main.qml's applyStats() already handles that text.

The badge ids and goals below must match badgeDefs in Main.qml.
"""
import json
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATS_FILE = HERE / "stats.json"

# (badge id, stat it counts, goal) - same as badgeDefs in Main.qml
BADGE_RULES = [
    ("badge1", "scanned", 1),
    ("badge2", "scanned", 5),
    ("badge3", "scanned", 25),
    ("badge4", "recycled", 1),
    ("badge5", "recycled", 10),
    ("badge6", "composted", 1),
    ("badge7", "days", 1),
    ("badge8", "days", 7),
]


def bin_key(name):
    """Same mapping as binKey() in Main.qml: food, recyclable, paper or garbage."""
    n = str(name).lower()
    if "food" in n or "compost" in n or "organic" in n:
        return "food"
    if "paper" in n or "cardboard" in n:
        return "paper"
    if "recycl" in n or "container" in n:
        return "recyclable"
    return "garbage"


class StatsTracker:
    def __init__(self, path=STATS_FILE, on_change=None):
        self.path = Path(path)
        self.on_change = on_change      # called with the JSON text after every change
        self.data = self._load()

    # ---------- storage ----------
    @staticmethod
    def _fresh():
        return {
            "scanned": 0,
            "recycled": 0,
            "composted": 0,
            "garbage": 0,
            "first_run": date.today().isoformat(),
        }

    def _load(self):
        data = self._fresh()
        try:
            saved = json.loads(self.path.read_text())
            for key in data:
                if key in saved:
                    data[key] = saved[key]
        except (OSError, ValueError, TypeError):
            pass                         # no file yet, or it is damaged: start fresh
        return data

    def _save(self):
        try:
            self.path.write_text(json.dumps(self.data, indent=2))
        except OSError as e:
            print("stats: could not save", self.path, e)

    # ---------- reading ----------
    @property
    def days(self):
        try:
            start = date.fromisoformat(self.data["first_run"])
        except (ValueError, TypeError):
            start = date.today()
        return max(0, (date.today() - start).days)

    def snapshot(self):
        d = self.data
        s = {
            "scanned": d["scanned"],
            "recycled": d["recycled"],
            "composted": d["composted"],
            "garbage": d["garbage"],
            "days": self.days,
        }
        s["earned"] = [bid for bid, stat, goal in BADGE_RULES if s[stat] >= goal]
        return s

    def to_json(self):
        """The text Main.qml's applyStats() parses."""
        return json.dumps(self.snapshot())

    # ---------- changing ----------
    def _changed(self):
        self._save()
        if self.on_change:
            self.on_change(self.to_json())

    def record_scan(self, bin_name):
        """Call once per finished scan, with whatever bin string the model returned."""
        key = bin_key(bin_name)
        self.data["scanned"] += 1
        if key == "food":
            self.data["composted"] += 1
        elif key in ("recyclable", "paper"):
            self.data["recycled"] += 1
        else:
            self.data["garbage"] += 1
        self._changed()
        return self.snapshot()

    def reset(self):
        """For the 'Reset progress' link in the Stats popup."""
        self.data = self._fresh()
        self._changed()

    def skip_days(self, n):
        """Demo helper: pretend the app has been online n more days (unlocks badge7/badge8)."""
        start = date.fromisoformat(self.data["first_run"]) - timedelta(days=n)
        self.data["first_run"] = start.isoformat()
        self._changed()

    def set_days(self, n):
        """Demo helper: make 'days online' exactly n (0 = start counting again from today)."""
        start = date.today() - timedelta(days=max(0, int(n)))
        self.data["first_run"] = start.isoformat()
        self._changed()
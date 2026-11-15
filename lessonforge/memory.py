"""Persistent memory: lets the system get better across runs.

What is stored (memory/memory.json):
  runs          - one summary per run
  fail_counts   - how often each rubric check has failed, across all runs
  recent_reasons- the last few failure reasons per check
  rules         - one short rule per failing check, injected into the generator prompt next run
  feedback      - free-text notes from a human reviewer, also injected next run

Self-evolution: a check that fails PROMOTE_AFTER times is "promoted":
  - its rule is shown to the generator as MUST
  - its recent failure reasons are shown to the judge as "known failure patterns to look for"
"""
import json
import time
from pathlib import Path

from .rubric import BY_ID

PROMOTE_AFTER = 3
MAX_HINTS = 8


class Memory:
    def __init__(self, path):
        self.path = Path(path)
        self.data = {"runs": [], "fail_counts": {}, "recent_reasons": {}, "rules": {}, "feedback": []}
        if self.path.exists():
            self.data.update(json.loads(self.path.read_text(encoding="utf-8")))

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---- what the next run reads ----
    def hints(self):
        rules = sorted(self.data["rules"].items(), key=lambda kv: -kv[1]["fails"])[:MAX_HINTS]
        out = [("MUST " if v["fails"] >= PROMOTE_AFTER else "") + f"[{k}] {v['rule']}" for k, v in rules]
        out += [f"Human feedback: {f}" for f in self.data["feedback"][-5:]]
        return out

    def judge_notes(self):
        return {k: self.data["recent_reasons"].get(k, [])[-3:]
                for k, n in self.data["fail_counts"].items() if n >= PROMOTE_AFTER}

    # ---- what a finished run writes ----
    def record_run(self, topic, attempts, shipped, total_attempts=None, distill=None):
        """attempts: list of result-lists (one per attempt) that the system should learn from."""
        failed_ids = []
        for results in attempts:
            for r in results:
                if not r.passed:
                    c = self.data["fail_counts"]
                    c[r.id] = c.get(r.id, 0) + 1
                    rr = self.data["recent_reasons"].setdefault(r.id, [])
                    rr.append(r.reason)
                    del rr[:-5]
                    if r.id not in failed_ids:
                        failed_ids.append(r.id)
        for cid in failed_ids:
            rule = BY_ID[cid].hint
            if distill and self.data["fail_counts"][cid] >= 2:
                try:
                    rule = distill(cid, self.data["recent_reasons"][cid]) or rule
                except Exception:
                    pass
            self.data["rules"][cid] = {"rule": rule, "fails": self.data["fail_counts"][cid]}
        self.data["runs"].append({"time": time.strftime("%Y-%m-%d %H:%M:%S"), "topic": topic,
                                  "attempts": total_attempts or len(attempts), "shipped": shipped, "failed_checks": failed_ids})
        self.save()

    def add_feedback(self, text):
        self.data["feedback"].append(text)
        self.save()

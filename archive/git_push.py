#!/usr/bin/env python3
import subprocess, sys
cmds = [
    ["git", "add", "rcagents_saas_core/frontend/templates/dashboard.html", "rcagents_saas_core/frontend/templates/dashboard_base.html"],
    ["git", "commit", "-m", "[HOTFIX] Add mock data via window globals in dashboard_base.html (fixes text leak)"],
    ["git", "push"]
]
for c in cmds:
    print(f"Running: {' '.join(c)}")
    r = subprocess.run(c, cwd=r"C:\Users\Micro-Tech\.openclaw\workspace")
    if r.returncode != 0:
        print(f"ERROR: {r.returncode}")
        sys.exit(1)
print("Done!")

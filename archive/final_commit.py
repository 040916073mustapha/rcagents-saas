#!/usr/bin/env python3
import subprocess, sys
cmds = [
    ["git", "add", "--all", "."],
    ["git", "commit", "-m", "[CLEANUP] Codebase restructure - officialize rcagents_saas_core/ as project root"],
    ["git", "push"]
]
for c in cmds:
    print("Run: " + " ".join(c))
    r = subprocess.run(c, cwd=r"C:\Users\Micro-Tech\.openclaw\workspace")
    if r.returncode != 0:
        print("Exit: " + str(r.returncode))
        sys.exit(1)
print("Done!")

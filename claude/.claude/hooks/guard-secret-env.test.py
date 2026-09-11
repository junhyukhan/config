import json, subprocess, os, sys

HOOK = os.path.join(
    os.path.expanduser("~"), "workdir/repos/config/claude/.claude/hooks/guard-secret-env.py"
)

def run(cmd):
    r = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}}),
        capture_output=True, text=True,
    )
    return r.returncode == 2

# (command, should_be_blocked)
CASES = [
    # --- must BLOCK: these print values to a console ---
    ("infisical export --env=prod --format=dotenv", True),
    ("infisical export", True),
    ("infisical secrets", True),
    ("infisical secrets get OPENAI_API_KEY --env=prod", True),
    ("infisical run --env=prod -- env", True),
    ("infisical run --env=prod -- printenv", True),
    ("cd duri-v3 && infisical export --env=dev", True),
    ("infisical export --env=prod | grep OPENAI", True),

    # --- must NOT block: safe, and blocking them would break the workflow ---
    ("infisical export --env=prod --format=dotenv --output-file=/tmp/x", False),
    ("infisical export --output-file /tmp/x --env=prod", False),
    ("infisical secrets set --file=/tmp/dev.env --env=dev", False),
    ("infisical secrets delete DEV_ALLOWED_ORIGINS --env=prod --type=shared", False),
    ("infisical run --env=dev -- pnpm dev", False),
    ("infisical run --env=prod -- node scripts/run-prod.mjs build", False),
    ("infisical login", False),
    ("infisical init", False),
    ("infisical --version", False),
    # The real push script must still work — it exports to a file.
    ("scripts/push-duri-env.sh --dry-run", False),

    # --- .env.public is declared non-secret; near-misses are NOT ---
    ("cat .env.public", False),
    ("grep NEXT_PUBLIC_SUPABASE_URL .env.public", False),
    ("cat duri-v3/.env.public", False),
    ("cat .env.production", True),      # prefix-match would wrongly allow this
    ("cat .env.public.local", True),    # only the exact name is exempt
    ("cat .env.publickey", True),

    # --- the pre-existing file rules must still hold ---
    ("cat .env.hosted", True),
    ("cp .env.local /tmp/x", False),
]

fails = 0
for cmd, want in CASES:
    got = run(cmd)
    status = "ok " if got == want else "FAIL"
    if got != want:
        fails += 1
    verb = "BLOCK" if want else "allow"
    print(f"  [{status}] {verb:5} : {cmd}")

print(f"\n{len(CASES) - fails}/{len(CASES)} cases correct")
sys.exit(1 if fails else 0)

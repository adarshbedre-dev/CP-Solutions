import re
import ast
import json
import time
import shutil
import random
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime

# ================= CONFIGURATION =================
REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "raw_codes"
CF_DIR = REPO_ROOT / "codeforces"
README_FILE = REPO_ROOT / "README.md"
CACHE_FILE = REPO_ROOT / "scripts" / "cf_cache.json"
CACHE_TTL = 86400  # Cache Codeforces API problemset for 24 hours
# =================================================

def run_git(args):
    result = subprocess.run(["git"] + args, cwd=REPO_ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Git error ({' '.join(args)}): {result.stderr.strip()}")
    return result.stdout.strip()

def sanitize_filename(name: str) -> str:
    """Removes characters that are invalid in Windows/Linux filenames."""
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()

def fetch_cf_problemset():
    """Fetches official problem names and ratings from Codeforces API."""
    if CACHE_FILE.exists() and (time.time() - CACHE_FILE.stat().st_mtime) < CACHE_TTL:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    print("Fetching official problem ratings & names from Codeforces API...")
    req = urllib.request.urlopen("https://codeforces.com/api/problemset.problems", timeout=15)
    data = json.loads(req.read().decode("utf-8"))
    if data["status"] != "OK":
        raise RuntimeError("Failed to fetch Codeforces problemset from API.")

    problems = {}
    for p in data["result"]["problems"]:
        if "contestId" in p and "index" in p:
            pid = f"{p['contestId']}{p['index']}".upper()
            problems[pid] = {
                "name": p.get("name", pid),
                "rating": p.get("rating", "Unrated")
            }

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(problems, f)
    return problems

def get_already_pushed_pids() -> set:
    """Scans ./codeforces/ folder to see which problem IDs are already in the repo."""
    pushed = set()
    if not CF_DIR.exists():
        return pushed
    for f in CF_DIR.rglob("*"):
        if f.is_file():
            # Matches "6C - Alice, Bob and Chocolate.py" or "6C.py"
            m = re.match(r"^(\d+[A-Za-z]\d*)\b", f.stem)
            if m:
                pushed.add(m.group(1).upper())
    return pushed

def is_code_valid(filepath: Path) -> tuple[bool, str]:
    """Checks if a code file is complete, syntactically valid, and has actual I/O logic."""
    content = filepath.read_text(encoding="utf-8", errors="ignore").strip()
    if len(content) < 20:
        return False, "File too short or empty"

    if re.search(r"\b(TODO|FIXME|INCOMPLETE|WIP)\b", content, re.IGNORECASE):
        return False, "Contains TODO/incomplete marker"

    ext = filepath.suffix.lower()
    if ext == ".py":
        try:
            ast.parse(content)
        except SyntaxError as e:
            return False, f"Python SyntaxError on line {e.lineno}"
        if content.endswith("pass") or content.endswith("..."):
            return False, "Ends with unfinished stub (pass/...)"
        if not any(k in content for k in ("input", "stdin", "print", "stdout")):
            return False, "Missing input/output statements"

    elif ext in (".cpp", ".c", ".cc"):
        if "main" not in content:
            return False, "Missing main() function"
        if content.count("{") != content.count("}") or content.count("{") == 0:
            return False, "Unbalanced curly braces"
        if not any(k in content for k in ("cin", "cout", "scanf", "printf")):
            return False, "Missing input/output statements"

    return True, "Valid"

def update_readme():
    """Updates README.md counts, Codeforces rating table, and date just like SolveBase."""
    if not README_FILE.exists():
        return

    text = README_FILE.read_text(encoding="utf-8")

    # Count actual solutions inside ./codeforces/<rating>/
    rating_counts = {}
    cf_total = 0
    if CF_DIR.exists():
        for rating_dir in CF_DIR.iterdir():
            if rating_dir.is_dir():
                count = sum(
                    1 for f in rating_dir.iterdir()
                    if f.is_file() and not f.name.startswith(".") and f.name.lower() != "readme.md"
                )
                if count > 0:
                    rating_counts[rating_dir.name] = count
                    cf_total += count

    # Sort rating rows numerically (800, 900, 1000, 1200...)
    def sort_key(r):
        return (0, int(r)) if r.isdigit() else (1, r)

    sorted_ratings = sorted(rating_counts.keys(), key=sort_key)
    if sorted_ratings:
        table_rows = "\n".join(f"| [{r}](./codeforces/{r}) | {rating_counts[r]} |" for r in sorted_ratings)
    else:
        table_rows = "| — | 0 |"

    # Replace Codeforces section count and table
    cf_pattern = re.compile(
        r"(## Codeforces\s+Solutions by \[.*?\]\(.*?\), organized by difficulty rating\.\s+\*\*Solved:\s*)\d+(\*\*\s+\| Difficulty \| Solved \|\s+\| --- \| --- \|\s+)(.*?)(\n\s*\n## LeetCode)",
        re.DOTALL
    )
    text = cf_pattern.sub(rf"\g<1>{cf_total}\g<2>{table_rows}\g<4>", text)

    # Calculate Total solved across all sections (Codeforces + LeetCode + CSES + CodeChef + GFG)
    other_counts = [int(m) for m in re.findall(r"## (?!Codeforces)\w+.*?\*\*Solved:\s*(\d+)\*\*", text, re.DOTALL)]
    grand_total = cf_total + sum(other_counts)

    text = re.sub(r"\*\*Total solved:\s*\d+\*\*", f"**Total solved: {grand_total}**", text)
    today_str = datetime.now().strftime("%Y-%m-%d")
    text = re.sub(r"_Last updated:\s*[\d-]+_", f"_Last updated: {today_str}_", text)

    README_FILE.write_text(text, encoding="utf-8")

def main():
    print("1. Pulling latest updates from GitHub (SolveBase sync)...")
    run_git(["pull", "--rebase", "origin", "main"])

    problems_db = fetch_cf_problemset()
    already_pushed = get_already_pushed_pids()

    # 2. Scan raw_codes for valid unpushed solutions
    valid_by_rating = {}
    pid_pattern = re.compile(r"^(\d+[A-Za-z]\d*)")

    for filepath in RAW_DIR.rglob("*"):
        if not filepath.is_file() or filepath.suffix.lower() not in (".py", ".cpp", ".c", ".java"):
            continue

        m = pid_pattern.match(filepath.stem.strip())
        if not m:
            continue
        pid = m.group(1).upper()

        # If already in ./codeforces/, remove duplicate from raw_codes
        if pid in already_pushed:
            print(f"[DUPLICATE] {pid} is already in repo. Removing from raw_codes.")
            filepath.unlink()
            continue

        if pid not in problems_db:
            print(f"[SKIP] {pid}: Not found in official Codeforces problemset.")
            continue

        valid, reason = is_code_valid(filepath)
        if not valid:
            print(f"[INVALID] {filepath.name}: {reason}")
            continue

        true_rating = str(problems_db[pid]["rating"])
        official_name = problems_db[pid]["name"]

        local_folder = filepath.parent.name
        if local_folder.isdigit() and local_folder != true_rating:
            print(f"[RATING CORRECTED] {pid} was in '{local_folder}/', actual CF rating is {true_rating}.")

        valid_by_rating.setdefault(true_rating, []).append({
            "pid": pid,
            "name": official_name,
            "rating": true_rating,
            "path": filepath
        })

    # 3. Pick 2 random solutions across different rating buckets
    available_ratings = list(valid_by_rating.keys())
    if not available_ratings:
        print("No valid unpushed solutions found in raw_codes!")
        return

    selected = []
    if len(available_ratings) >= 2:
        chosen_tiers = random.sample(available_ratings, 2)
        for tier in chosen_tiers:
            selected.append(random.choice(valid_by_rating[tier]))
    else:
        pool = valid_by_rating[available_ratings[0]]
        selected = random.sample(pool, min(2, len(pool)))

    # 4. Move each file to ./codeforces/<rating>/<PID> - <Name>.<ext>, update README, and commit
    pushed_summary = []
    for item in selected:
        target_dir = CF_DIR / item["rating"]
        target_dir.mkdir(parents=True, exist_ok=True)

        safe_name = sanitize_filename(item["name"])
        target_filename = f"{item['pid']} - {safe_name}{item['path'].suffix}"
        target_path = target_dir / target_filename

        shutil.copy2(item["path"], target_path)
        item["path"].unlink()  # Remove from raw_codes after moving

        # Update README.md and create a SolveBase-identical commit
        update_readme()
        run_git(["add", str(target_path.relative_to(REPO_ROOT)), "README.md"])
        commit_msg = f"Add {item['name']} ({item['rating']})"
        run_git(["commit", "-m", commit_msg])

        pushed_summary.append(f"{target_filename} (Rated {item['rating']})")

    # 5. Push to GitHub
    print("Pushing commits to GitHub...")
    run_git(["push", "origin", "main"])

    print("\nSUCCESS! Pushed 2 solutions in SolveBase format:")
    for s in pushed_summary:
        print(f" -> {s}")

if __name__ == "__main__":
    main()
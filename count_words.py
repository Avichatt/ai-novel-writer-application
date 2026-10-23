import glob, os

files = sorted(glob.glob("manuscript/*.md"))
total = 0

print("=== WORD COUNT BREAKDOWN ===")
for f in files:
    words = len(open(f, encoding="utf-8").read().split())
    total += words
    print(f"{os.path.basename(f)}: {words:,} words")

print("----------------------------")
print(f"TOTAL MANUSCRIPT WORD COUNT: {total:,} words")

# Verification Command Patterns

> The reviewer runs these independently after each batch's self-check report.
> Don't just read the report — command-driven re-checking is the most
> effective way to find the executor's blind spots.
>
> Each pattern comes in **bash** (macOS/Linux) and **PowerShell** (Windows).
> Pick what fits the task; you don't need all of them.

## Principles

1. **Never trust the numbers in a report** — run the command yourself.
2. **Highest-yield verification**: count checks + integrity checks — one line
   finds N problems.
3. **Paste command output into the review verdict** appended to the
   self-check report.

---

## 1. Count checks

Verify "declared count = actual count" — applies anywhere inputs map to
outputs.

```bash
# files in a tree
find "<path>" -type f | wc -l

# by extension
find "<path>" -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn

# per subdirectory (compare against the progress table)
for d in "<path>"/*/; do echo "$(basename "$d"): $(find "$d" -maxdepth 1 -type f | wc -l)"; done

# records: CSV lines / JSON array length / DB rows
wc -l < input.csv && wc -l < output.csv
jq length < input.json && jq length < output.json
sqlite3 db.db "SELECT COUNT(*) FROM table_name;"
```

```powershell
(Get-ChildItem "<path>" -File -Recurse).Count

Get-ChildItem "<path>" -File -Recurse |
  Group-Object Extension | Select-Object Name, Count

Get-ChildItem "<path>" -Directory | ForEach-Object {
    [PSCustomObject]@{ Dir = $_.Name; Count = (Get-ChildItem $_.FullName -File).Count }
} | Format-Table -AutoSize
```

## 2. Integrity & deduplication

```bash
# duplicate content by hash (highest-yield single line)
find "<dir>" -type f -exec md5 -q {} + | sort | uniq -d          # macOS
find "<dir>" -type f -exec md5sum {} + | sort | awk '{print $1}' | uniq -d  # Linux

# source untouched (evidence for the "don't damage sources" constraint)
before=<recorded-count>
after=$(find "<source>" -type f | wc -l)
echo "before=$before after=$after diff=$((after - before))"   # expect diff=0
```

```powershell
Get-ChildItem "<dir>" -File -Recurse |
  ForEach-Object { Get-FileHash $_.FullName -Algorithm MD5 } |
  Group-Object Hash | Where-Object { $_.Count -gt 1 } |
  ForEach-Object { [PSCustomObject]@{ Hash=$_.Name; Count=$_.Count; Files=($_.Group.Path -join "; ") } }
```

## 3. Constraint-leak scans

```bash
# forbidden extensions in the output — expect no output
find "<target>" -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.psd" \)

# directories deeper than N levels — expect no output
find "<target>" -mindepth <N+1> -type d
```

```powershell
$forbidden = @("*.mp4","*.mov","*.psd")
Get-ChildItem "<target>" -Recurse -File -Include $forbidden | Select-Object FullName
```

## 4. Naming / format checks

```bash
# naming-pattern sampling
ls "<dir>" | head -20 | while read f; do
  echo "$f: $(echo "$f" | grep -qE '<regex>' && echo match || echo NO-MATCH)"
done

# heading structure vs expected outline (docs/content work)
diff <(grep -E '^#{1,3} ' expected.md) <(grep -E '^#{1,3} ' actual.md)
```

## 5. Code / test verification (refactoring work)

```bash
npm test / pytest / go test ./... / cargo test        # tests green
eslint . / mypy . / go vet ./... / cargo clippy       # lint clean

# change surface matches the declared scope
git diff --name-only HEAD~<N>
```

## 6. Governance artifacts

```bash
# README/index presence per directory
for d in "<root>"/*/; do
  echo "$(basename "$d"): $(test -f "$d/README.md" && echo yes || echo NO)"
done

# internal links resolve (markdown work)
grep -oE '\[\[.*?\]\]' <file.md> | sort -u
```

```powershell
Get-ChildItem "<root>" -Directory | ForEach-Object {
    [PSCustomObject]@{ Dir=$_.Name; HasREADME=(Test-Path (Join-Path $_.FullName "README.md")) }
} | Format-Table -AutoSize
```

## 7. Diffing

```bash
diff -rq <dirA> <dirB> | head -50
du -sh <dirA> <dirB>
```

```powershell
Compare-Object (Get-ChildItem "<dirA>" -Recurse -File).Name (Get-ChildItem "<dirB>" -Recurse -File).Name
```

---

## Minimum verification by task type

| Scenario | Floor |
|---|---|
| Any task | count check (§1) + one integrity check (§2) |
| File operations | §1 + §2 + §3 |
| Code refactoring | §5 (tests + lint + change surface) |
| Docs / content | §4 + §6 |
| Data processing | §1 records + §2 |

> The report is the executor's self-attestation; the command is the
> reviewer's independent falsification.

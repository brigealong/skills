# 验证命令模式库

> 审核方在每批自检报告提交后，独立运行以下验证。
> 不要只读报告——命令式复核是发现执行方盲区的最有效手段。
>
> 每个模式提供 **PowerShell**（Windows）和 **bash**（macOS/Linux）双版本。
> 根据任务类型和平台选取适用的命令。不必全部运行——选与当前任务相关的。

---

## 通用原则

1. **不要信任报告中的数字**——自己跑一遍
2. **最高性价比验证**：计数校验 + 完整性检查，一行命令发现 N 个问题
3. **验证命令输出应写入审核结论**——附在自检报告末尾的"最终验收结论"中

---

## 1. 计数校验

验证"声明数量 = 实际数量"。适用于任何有"输入数 vs 输出数"的场景。

### 1.1 目录文件计数

```powershell
# PowerShell
(Get-ChildItem "<路径>" -File -Recurse).Count
```

```bash
# bash
find "<路径>" -type f | wc -l
```

### 1.2 按类型/扩展名计数

```powershell
# PowerShell
Get-ChildItem "<路径>" -File -Recurse |
  Group-Object Extension | Select-Object Name, Count
```

```bash
# bash
find "<路径>" -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn
```

### 1.3 每子目录计数（对比进度表声明值）

```powershell
# PowerShell
Get-ChildItem "<路径>" -Directory | ForEach-Object {
    $count = (Get-ChildItem $_.FullName -File).Count
    [PSCustomObject]@{ Dir = $_.Name; Count = $count }
} | Format-Table -AutoSize
```

```bash
# bash
for d in "<路径>"/*/; do echo "$(basename "$d"): $(find "$d" -maxdepth 1 -type f | wc -l)"; done
```

### 1.4 记录计数（数据处理场景）

```bash
# CSV 行数
wc -l < input.csv
wc -l < output.csv

# JSON 数组长度
jq length < input.json
jq length < output.json

# 数据库记录数
sqlite3 db.db "SELECT COUNT(*) FROM table_name;"
```

---

## 2. 完整性与去重

### 2.1 hash 唯一性检查（性价比最高的验证）

一行命令发现重复内容。

```powershell
# PowerShell
Get-ChildItem "<目录>" -File -Recurse |
  ForEach-Object { Get-FileHash $_.FullName -Algorithm MD5 } |
  Group-Object Hash | Where-Object { $_.Count -gt 1 } |
  ForEach-Object {
      [PSCustomObject]@{
          Hash = $_.Name
          Count = $_.Count
          Files = ($_.Group.Path -join "; ")
      }
  }
```

```bash
# macOS
find "<目录>" -type f -exec md5 -q {} + | sort | uniq -d

# Linux
find "<目录>" -type f -exec md5sum {} + | sort | awk '{print $1}' | uniq -d
```

### 2.2 源/输入完好性检查

验证源未被意外修改（"不破坏源"硬约束的证据）。

```powershell
# PowerShell
$before = <迁移前记录的数量>
$after = (Get-ChildItem "<源路径>" -File -Recurse).Count
"before=$before after=$after diff=$($after - $before)"
# 预期：diff = 0
```

```bash
# bash
before=<之前记录的数量>
after=$(find "<源路径>" -type f | wc -l)
echo "before=$before after=$after diff=$((after - before))"
```

---

## 3. 约束泄漏扫描

### 3.1 禁止项扫描

检查输出中是否存在不应出现的内容（文件类型、目录、数据记录等）。

```powershell
# PowerShell — 禁止扩展名
$forbidden = @("*.mp4","*.mov","*.psd")  # 按任务实际填写
Get-ChildItem "<目标目录>" -Recurse -File -Include $forbidden |
  Select-Object FullName
# 预期：空（0 条结果）
```

```bash
# bash — 禁止扩展名
find "<目标目录>" -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.psd" \)
# 预期：无输出
```

### 3.2 结构/层级验证

检查输出结构是否符合约束。

```powershell
# PowerShell — 最大深度
Get-ChildItem "<目标目录>" -Recurse -Directory |
  Where-Object { ($_.FullName.Replace($target,'').Trim('\').Split('\').Count) -gt <最大深度> } |
  Select-Object FullName
```

```bash
# bash — 超过 N 层的目录
find "<目标目录>" -mindepth <N+1> -type d
```

---

## 4. 命名/格式校验

### 4.1 命名模式抽样

```powershell
# PowerShell
Get-ChildItem "<目录>" -File | Select-Object -First 20 |
  ForEach-Object {
      [PSCustomObject]@{
          Name = $_.Name
          Matches = ($_.Name -match '<正则模式>')
      }
  } | Format-Table -AutoSize
```

```bash
# bash
ls "<目录>" | head -20 | while read f; do
  echo "$f: $(echo "$f" | grep -qE '<正则模式>' && echo 'match' || echo 'no-match')"
done
```

### 4.2 结构一致性检查（文档/内容场景）

验证输出文档结构是否符合预期大纲。

```bash
# 对比实际标题与预期大纲
grep -E '^#{1,3} ' <输出文件> | head -30

# 对比两个文件的标题结构
diff <(grep -E '^#{1,3} ' expected.md) <(grep -E '^#{1,3} ' actual.md)
```

---

## 5. 代码/测试验证（代码重构场景）

### 5.1 测试通过

```bash
# 根据项目类型选取
npm test          # Node.js
pytest            # Python
go test ./...     # Go
cargo test        # Rust
```

### 5.2 Lint / 类型检查

```bash
# 根据项目类型选取
eslint .                    # JS/TS
mypy .                      # Python
go vet ./...                # Go
clippy                      # Rust
```

### 5.3 变更范围验证

确认只修改了预期范围内的文件。

```bash
# 查看变更文件列表
git diff --name-only HEAD~<N>
# 对比预期变更清单
```

---

## 6. 文档/治理产物检查

### 6.1 README / 索引存在性

```powershell
# PowerShell
Get-ChildItem "<目标根目录>" -Directory | ForEach-Object {
    $readme = Join-Path $_.FullName "README.md"
    [PSCustomObject]@{ Dir = $_.Name; HasREADME = (Test-Path $readme) }
} | Format-Table -AutoSize
```

```bash
# bash
for d in "<目标根目录>"/*/; do
  echo "$(basename "$d"): $(test -f "$d/README.md" && echo 'yes' || echo 'NO')"
done
```

### 6.2 链接有效性（Markdown 文档场景）

```bash
# 提取并检查内部链接
grep -oE '\[\[.*?\]\]' <文件.md> | sort -u
# 手动或脚本验证每个链接目标是否存在
```

---

## 7. 差异对比

### 7.1 变更摘要

```bash
# 两目录差异
diff -rq <目录A> <目录B> | head -50

# 磁盘用量变化
du -sh <目录A> <目录B>
```

```powershell
# PowerShell
Compare-Object (Get-ChildItem "<目录A>" -Recurse -File).Name (Get-ChildItem "<目录B>" -Recurse -File).Name
```

---

## 使用建议

| 场景 | 推荐最低验证 |
|------|-------------|
| 任何任务 | 计数校验（§1）+ 至少一项完整性检查（§2） |
| 文件操作 | §1 + §2 + §3（约束泄漏） |
| 代码重构 | §5（测试 + lint + 变更范围） |
| 文档/内容 | §4（结构校验）+ §6（治理产物） |
| 数据处理 | §1.4（记录计数）+ §2（完整性） |

---

> **核心提醒**：审核方不要只读报告中的数字，自己跑一遍验证命令。
> 报告是执行方自证；命令是审核方独立证伪。

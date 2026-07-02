---
name: making-contract
description: >-
  Use when a user-facing goal, brainstormed design, existing design doc, implementation plan,
  or multi-agent workflow needs an explicit contract before planning, implementation, or
  orchestration. This skill turns human intent into a minimal verifiable contract: Intent,
  Scope, Acceptance, Examples, and Evaluation. It runs downstream of brainstorming, does its
  own narrow contract-gap clarification (not a second brainstorm), gates before writing-plans,
  and is the upstream contract for task-orchestration.
---

# Making Contract

把“用户想要的结果”固定成 Agent 能执行、Evaluator 能验收、Trace 能追责的最小契约。

## 核心定位

`making-contract` 不是 brainstorming、不是 design doc、不是 implementation plan、不是 task orchestration。

它只回答五个问题：

1. **Intent**：为什么做？用户真正要完成什么？
2. **Scope**：做什么，不做什么？
3. **Acceptance**：怎样算通过？
4. **Examples**：什么样算好，什么样算坏？
5. **Evaluation**：怎么判断 PASS / CONDITIONAL PASS / FAIL？

## 何时使用

是否需要本 skill，由 **复杂度 × 影响面 × 主观性 × 不可逆性** 决定，不由"是否交给 Agent"单独决定。满足任一条件时应产出 contract：

- brainstorming 已形成设计，下一步准备写 implementation plan。
- 已有 design doc / plan，但缺少用户可验收的 contract。
- 任务会进入 `task-orchestration` 的 Tier 2 全编排。
- 任务有主观质量标准，例如内容、审美、研究质量、资料筛选、交付体验。
- 任务有不可逆或高风险副作用，例如写入 Zotero、批量改文件、发布内容、覆盖数据。
- 用户问“什么算好”“怎样验收”“不要跑偏”“先定标准”。

"交给 executor / worker / Orca / Hermes / 其他 Agent 执行"本身**不是**强制条件——轻、低风险、自明的派发（`task-orchestration` Tier 0/1）在派发 prompt 里内嵌最小契约即可，不必跑完整 making-contract；只有 Tier 2 才需要独立 contract。

不用于：

- 一次性低风险小修，且用户已明确给出唯一可判断结果。
- 纯探索聊天，尚未进入设计或执行准备阶段。
- 只需要拷问术语、领域模型或架构决策的文档；这种先用 `grill-with-docs` 或相当的文档拷问流程。

## 与其他 skill 的关系

### Brainstorming → Making Contract（单向，不是循环）

`brainstorming` 负责探索需求、方案和设计（发散），它是完整工作流：提方案 → 出设计 → 用户认可。

`making-contract` 负责把“设计看起来可以”收敛成“怎样才算验收通过”（收敛）。

**关系是单向交接，不是"调用后返回"的循环。** 这一点很关键——`brainstorming` 的终态是它自己的下游（design 认可后转 writing-plans），它**不是**一个"补一个缺口就返回调用者"的可重入子程序。所以 `making-contract` **不 invoke brainstorming**。

正确链路：

```text
brainstorming（发散、出设计）
   → making-contract（收敛、定契约）   ← 需要用户可验收契约时进入
      → writing-plans / task-orchestration
```

这条链路是双方约定的：`brainstorming` 的 Checklist step 9 已改为——design 经用户认可后，若任务需要用户可验收契约（主观质量 / 不可逆高风险 / Tier 2 编排；单纯"交给 executor"不算触发），**主动交接进本 skill**，再由本 skill 路由到 writing-plans 或 task-orchestration；否则直连 writing-plans。所以是 `brainstorming → making-contract` 的单向交接，不是本 skill 反向 invoke brainstorming。

分工与防重叠：

- `making-contract` 内部**只做窄口径的"契约缺口澄清"**：一次一个问题、优先选择题、只问阻塞契约成立的缺口。这**不是**第二个 brainstorm——它不探索方案、不比较架构、不产设计文档。
- 只有当缺口的根因是**真正的设计分歧**（方案本身未决、需要重新探索）时，才**单向**把任务整段交回 `brainstorming`，而不是在 making-contract 内硬聊设计。见 [缺口根因路由](#step-3-跑-readiness-gate缺口按根因路由)。
- 判定“材料够不够写 contract”见 [Readiness Gate](#readiness-gate)。

### Existing Doc → Optional Grill → Making Contract

如果输入是一份已有 design doc 或 plan：

1. 先检查文档是否存在模糊术语、隐藏假设、架构取舍不清、领域边界不清。
2. 如果存在，先运行 `grill-with-docs` 或等价的文档拷问流程。
3. 不要把模糊词直接锁进 contract。
4. 当术语和边界足够清楚后，再写 contract。

### Making Contract → Writing Plans

`writing-plans` 的输入应是：

- 上游 design / spec；
- 本 skill 产出的 contract。

计划文档必须引用 contract，并把关键任务映射到 contract 条款。实现步骤不能改写 contract 的目标、范围和验收标准。

### Making Contract → Task Orchestration

`task-orchestration` 的 execution contract 不能替代本 skill 的 user-facing contract。

进入 Tier 2 编排前必须检查是否已有 contract。若没有，先运行本 skill。

执行说明应包含：

```markdown
## 上游契约

本执行说明必须遵守：

- `<path-to-contract.md>`

契约的权威是**有范围的**：
- 用户已确认的 Intent / Scope / Acceptance 对下游**目标**有约束力，冲突时以 contract 为准。
- 技术事实、系统约束、已验证的设计结论以经验证的 design / spec 为准——contract 不能覆盖它们。
- 若 contract 与技术事实冲突（尤其 contract 是 agent 推断或尚未确认时），**停止并协调修订，禁止静默选边**。
- 若 contract 不足以判断执行方向，必须升级，不得自行补全用户目的。
```

## 输出位置

优先与任务材料放在同一项目或任务目录内：

```text
docs/contracts/<topic>-contract-YYYY-MM-DD.md
```

若当前仓库没有 `docs/contracts/`，可放：

```text
<task-dir>/contract.md
```

不要把 contract 混进 design doc 或 implementation plan。Contract 是上游验收标准，应独立存在，便于 evaluator 和 worker 引用。

## 最小 Contract 模板

Contract 文件必须只包含这五个主模块。不要默认扩成 10+ 模块。

```markdown
# Contract: <Task Name>

## 1. Intent

这个任务要服务的真实用户目的是什么？

## 2. Scope

### In Scope
- ...

### Out of Scope
- ...

## 3. Acceptance

### Must
- ...

### Should
- ...

### Pass Line
- ...

## 4. Examples

### Good Sample
Given ...
When ...
Then ...

### Bad Sample
Given ...
When ...
Then ...

## 5. Evaluation

### Deterministic Checks
- ...

### Judgment Checks
- ...

### Result States
- PASS:
- CONDITIONAL PASS:
- FAIL:
```

## 写作规则

### 1. Intent 不写成方案

错误：

```markdown
这个任务是实现一个 Playwright + Zotero 的 Web Discovery CLI。
```

正确：

```markdown
这个任务是为小红书 / Zotero 资料工作流提供一个可追溯、可审核、可复用的网页来源发现入口。
```

Intent 应写用户目的，不写技术实现。

### 2. Scope 必须同时写 In Scope 和 Out of Scope

只写做什么不够。必须写不做什么，防止 Agent 自行扩展范围。

### 3. Acceptance 只写可判断标准

Must 必须能被确定性检查、人类检查或 LLM judge 检查。不要写“体验要好”“尽量完整”这种不可验收句子。

如果必须写主观标准，必须在 Evaluation 的 Judgment Checks 里给出评分方式。

### 4. Examples 是 contract 的锚点

每份 contract 至少要有：

- 1 个 Good Sample；
- 1 个 Bad Sample。

样例可以用 Given / When / Then 写，也可以用输入 / 输出 / 为什么通过 的形式写。

### 5. Evaluation 必须能给三态结果

每份 contract 必须定义：

- PASS；
- CONDITIONAL PASS；
- FAIL。

不要只写“检查一下”。Evaluator 必须知道什么情况通过、什么情况要返工、什么情况要回到用户重新确认。

## 样例来源优先级

写 Examples 时按以下优先级找样例：

1. 用户明确提供的好 / 坏样例。
2. 项目历史中用户认可或否定过的产物。
3. 当前 design doc、spec、测试用例、既有报告中的示例。
4. 公开网络上的 reference sample。
5. Agent 生成候选样例，请用户确认。

重要区分：

- **Reference Sample**：可来自网络，用于启发。
- **Acceptance Sample**：必须由用户确认，或来自用户明确认可的历史产物，才能作为验收依据。

如果样例不足，必须在 contract 中写出 Sample Coverage 风险，不要假装标准已经稳定。

```markdown
### Sample Coverage

| 维度 | 是否有样例 | 来源 | 风险 |
|---|---:|---|---|
| Good Sample | 有 | 用户提供 | 低 |
| Bad Sample | 无 | - | 中：Evaluator 可能过宽 |
| Boundary Sample | 无 | - | 高：Agent 可能自决边界 |
```

`Sample Coverage` 不是第六个主模块；如需使用，放在 `## 4. Examples` 内。

## Readiness Gate

判定“材料够不够写 contract”。**注意：五格填满只是结构完整，不等于契约充分**——Intent 写了但 Scope 没覆盖它、Must 每条可判却漏了关键成功条件、Good/Bad sample 都在却只覆盖平凡情况、三态标题齐全却没阈值，都能骗过纯结构检查。所以 Gate 分两层，两层都过才算 ready。

### 第一层：Structural readiness（结构完整，规则可判）

纯布尔检查，代码/规则即可回答，不用模型：

| 模块 | 结构条件 |
|---|---|
| Intent | 非空 |
| Scope | In 与 Out 两节都存在 |
| Acceptance | 至少 1 条 Must |
| Examples | 至少 1 Good + 1 Bad |
| Evaluation | PASS / CONDITIONAL PASS / FAIL 三态标题齐 |

结构缺失 → 直接判为缺口。结构齐全**不代表**过线，继续第二层。

### 第二层：Semantic readiness（语义充分，需模型/人工判断）

- **Intent↔Scope 一致**：Scope 覆盖 Intent 声明的目的，没有跑题或遗漏。
- **Acceptance 覆盖 Intent 关键结果**：每个关键目的都有对应 Must，不是只挑好判的写。
- **Must → Evaluation 映射**：每条 Must 至少对应一个 Evaluation check，check 指明**执行者、输入证据、判定规则**，不是只有一句“检查一下”。
- **Examples → Acceptance 映射**：样例的价值是划清决策边界，不是数量。每个样例至少映射到一条关键 Acceptance；主观质量 / 高风险任务还需 boundary sample，否则明确记录“缺失的决策边界”。
- **三态可执行**：三态边界互斥且覆盖预期结果；`CONDITIONAL PASS` 必须定义**允许遗留什么、谁批准、何时补齐**，否则它就是模糊放行口。
- **Out of Scope 有信息量**（不是"非空即可"）：若存在合理的相邻范围 / 扩张风险，必须明确排除；若确实没有，允许写 `No additional exclusions identified` 并说明依据。填“本次不做无关事项”这类占位文字**不算过线**。
- **无未解决的矛盾、歧义、未经授权的假设**。

### 三层职责（谁来判）

- **规则**：结构与引用完整性（第一层，及 Must↔check 是否成对存在）。
- **模型 / 人工**：语义可判定性、覆盖、一致性、样例代表性（第二层）。
- **用户**：目的、偏好、风险接受、验收标准的最终授权——不能被规则或模型替代。

### 循环逻辑（非单调，需重判受影响模块）

五模块**互相依赖**，不是五个独立槽位：补了 Scope 可能让原本过线的 Acceptance 失效，补 Bad Sample 可能暴露 Intent 或设计错误。所以“勾掉即永久完成”不成立——**勾选是当前状态，不是永久状态**。

```text
每轮：
  1. 跑两层 Gate
  2. 有缺口 → 按根因路由补齐（见 Step 3）
  3. 补完后不只重判该缺口，还要重判：
       - 被这次答案影响的模块
       - 全局一致性
  4. 直到达到某个终态
```

**总轮次预算**：给整个 Gate 一个上限（默认全程 ≤ 6 轮，同一缺口 ≤ 2 轮）；到顶不再硬聊，落到终态。

### 三种终态（替代旧的"放行/不放行"二元）

- **READY**：两层全过，无遗留风险 → 起草并可推进下游。
- **READY_WITH_ACCEPTED_RISKS**：仅**可降级**缺口未满（辅助样例、Should、非关键边界），已记录风险并经**用户明确接受** → 起草，风险写进 contract。
- **BLOCKED**：存在**不可豁免**缺口未解 → 停止下游路由，输出 `BLOCKED / unresolved decisions` 清单，回到用户或上游。

### 逃生阀：区分不可豁免缺口 vs 可接受风险

同一缺口超预算仍填不满时，**不能一律降级成 `Sample Coverage`**（那是类型错误：Intent 不清是"目标未知"，不是"样例不足"）。按缺口性质分流：

- **不可豁免**（缺则契约语义不成立）：Intent、核心 Scope、Must Acceptance、Must→Check 映射。→ 判 **BLOCKED**，不得放行起草。
- **可降级**（缺则只是风险，契约仍可成立）：辅助样例、Should、非关键边界。→ 记录对应风险（样例类才用 `Sample Coverage`），**要求用户明确接受**后判 READY_WITH_ACCEPTED_RISKS。

## 工作流程

### Step 1: 收集输入

读取或整理：

- 用户原始请求；
- brainstorming 输出；
- design doc / plan；
- 相关历史产物；
- 用户提供的 reference；
- 当前任务准备进入的下游：writing-plans、task-orchestration、implementation、evaluation。

### Step 2: 判断是否需要先 Grill

Grill 只处理**文档层面的不清**（术语 / 领域模型 / 隐藏假设 / 内部矛盾）。存在以下情况先拷问，不要直接写 contract：

- 核心术语含糊；
- 领域对象不清；
- 关键取舍没有理由；
- 用户目的和技术方案混在一起；
- 文档内部自相矛盾。

拷问后再进 Readiness Gate。

（"好/坏无法举例""Acceptance 无法判定"**不在这里处理**——那是契约缺口，归 Step 3 的根因路由，避免同一缺口被 Step 2 和 Step 3 各路由一次。）

### Step 3: 跑 Readiness Gate，缺口按根因路由

按 [Readiness Gate](#readiness-gate) 跑两层判据：

- 达到 READY / READY_WITH_ACCEPTED_RISKS → 进 Step 4 起草。
- BLOCKED 或仍有缺口 → **按缺口的根因**选一个动作（不是一律 invoke brainstorming）：

| 缺口根因 | 动作 |
|---|---|
| 术语 / 领域模型 / 隐藏假设 / 内部矛盾 | 回 Step 2 `grill-with-docs` |
| 用户偏好 / 目标 / 范围 / 成功标准未知 | making-contract **自己做窄口径定向澄清**：一次一问、优先选择题、只问阻塞项，**不 invoke brainstorming** |
| 设计方案本身未决（需要重新探索方案） | **单向**把任务整段交回 `brainstorming`，不在这里硬聊设计 |
| 仅缺样例 | 先搜历史材料 / 生成候选样例请用户确认，**不启动 brainstorm** |

每次补齐后按[循环逻辑](#循环逻辑非单调需重判受影响模块)重判受影响模块与全局一致性，直到落到终态。

原则：能从材料（用户请求、brainstorming 输出、design doc、历史产物）可靠推断的格子直接填，不问用户；只对推断不出、又阻塞 contract 成立的格子提问。

### Step 4: 起草五模块 Contract

按最小模板写。保持短、硬、可验收。

### Step 5: 样例缺口检查

检查是否至少有 1 个 good sample 和 1 个 bad sample，且各自映射到关键 Acceptance（见 Semantic readiness）。

若没有：先生成候选样例并标注“待用户确认”；若确实补不齐，样例属**可降级**缺口——按逃生阀记 `Sample Coverage` 风险并**请用户明确接受**（落到 READY_WITH_ACCEPTED_RISKS），不要静默放行。

### Step 6: 用户确认

在进入 writing-plans 或 task-orchestration 前，必须让用户确认 contract，除非用户明确授权 agent 自行制定并继续。

### Step 7: 下游路由

- Contract 暴露出设计偏差 → **单向交回** `brainstorming` 回炉修订设计（不是 invoke-返回）。设计改回来后按下面的版本规则处理，再重跑 Readiness Gate。
- Contract 已确认，且要实现 → 进入 `writing-plans`。
- Contract 已确认，且要多 Agent 执行 → 进入 `task-orchestration`。
- Contract 已确认，且产物准备交付 → 进入 contract evaluator 或 review 流程。

**版本规则（设计变更使旧确认失效）**：任何影响 Intent / Scope / Acceptance / Evaluation 的设计变更，都会让针对旧版本的用户确认失效——必须标记受影响条款、对这些条款重跑 Gate、并**重新获得用户确认**，不能继承旧确认直接推进下游。

## 反模式

- 把 contract 写成第二份 design doc。
- 只写 Must，不写 Out of Scope。
- 只有抽象标准，没有 good / bad sample。
- 把网络 reference sample 当成用户 acceptance sample。
- 在 contract 没确认前直接写 implementation plan。
- 用 task-orchestration 的执行说明替代用户验收契约。
- 让 executor 自己补全用户目的。
- **把 brainstorming 当成"调用后返回"的子程序 invoke**——它是完整工作流，只能单向交接。
- **把"五格填满"当成契约充分**——结构完整 ≠ 语义充分，必须过 Semantic readiness。
- **把任意缺口一律降级成 `Sample Coverage` 风险放行**——不可豁免缺口必须判 BLOCKED。
- **在 making-contract 内复刻 brainstorming**（探索方案 / 出设计），把窄口径澄清做成第二个 brainstorm。

## 完成标准

一次 `making-contract` 完成时，必须产出：

- 一个独立 contract 文件；
- 五个主模块结构完整，且过 Semantic readiness（Intent↔Scope 一致、Acceptance 覆盖 Intent、每条 Must → Evaluation check、Examples 映射关键 Acceptance）；
- 至少一个 good sample 和一个 bad sample，或经用户接受的 `Sample Coverage` 风险；
- 可执行的三态 Evaluation（含 CONDITIONAL PASS 的遗留/批准/补齐规则）；
- 明确的终态：`READY` / `READY_WITH_ACCEPTED_RISKS` / `BLOCKED`；
- 下游路由建议。

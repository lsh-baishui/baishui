# 白水的 Agent Skills

面向中文内容创作与业务行动的技能集合。

| 技能 | 用途 |
|---|---|
| [human-short-video-writing](skills/human-short-video-writing/SKILL.md) | 中文短视频观点口播创作与改稿 |
| [xiapeng-action-coach](skills/xiapeng-action-coach/SKILL.md) | 夏鹏行动教练：客户访谈、价值主张、交付验证、增长与团队行动 |

## 中文短视频观点口播

一个聚焦中文短视频观点口播的 Agent Skill。它用真实材料和可核事实形成单一核心判断，再完成开头、论证、反方、边界、口播和观众价值检查。

适合创作或改写个人 IP 观点稿、知识口播、商业观察、职场与自我成长内容，也可以只优化开头、诊断传播力和去除模板化表达。

不处理纯剧情短剧、镜头分镜、直播带货、挂车销售文案和知乎、公众号等长篇写作。

## 安装

从 GitHub 安装：

```bash
npx -y skills add lsh-baishui/baishui -g --all
```

从本地仓库安装：

```bash
npx -y skills add . -g --all
```

## 使用

创作：

> 使用 $human-short-video-writing，根据我的选题、受众和真实材料，写一条 60 秒中文观点口播。直接交成稿。

局部改稿：

> 使用 $human-short-video-writing，只改这篇稿的前两句，保留我的核心判断和克制语气，不要重贴正文。

诊断：

> 使用 $human-short-video-writing，只诊断这篇口播是否能发，不改稿。请给结论和三项最优先修改动作。

## 内容

```text
skills/human-short-video-writing/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── evidence-and-boundaries.md
│   ├── revision-and-diagnosis.md
│   └── viewpoint-and-structure.md
└── scripts/check_script.py
```

检查脚本只使用 Python 标准库：

```bash
python3 skills/human-short-video-writing/scripts/check_script.py 稿件.md --seconds 60
```

## 当前验证

- Skill 结构、相对引用、YAML 和 Python 语法校验通过。
- 检查脚本的正常、警告、阻断和参数错误路径通过。
- 正常创作、伪造亲历边界、只诊断、近邻任务退出和局部改稿回归样本通过。
- 本地 `skills add` 能发现并复制全部 6 个运行文件，文件内容与源目录一致。
- 已从真实 GitHub 远端完成全新安装；全部 6 个运行文件与仓库源目录逐文件一致，远程安装校验通过。

本地评测样本、预期答案、执行记录和个人路径不进入公开仓库。

## 夏鹏行动教练

依据星途三天培训，结合友邻培训与课堂工具，将真实业务材料变成有证据的判断和可执行产出。保留26项行动方法，并补充客户分群、价值主张八项检查、获客与交付双循环、课程验收、经营核算和团队协作。

单独安装：

```bash
npx -y skills add lsh-baishui/baishui --skill xiapeng-action-coach -g
```

使用示例：

> 使用 $xiapeng-action-coach，根据我的产品资料和用户访谈，整理目标人群与价值主张，区分证据和假设，并产出下一轮验证方案。

> 使用 $xiapeng-action-coach，检查这门AI课程的交付设计，给出具体任务、验收要求和课后迁移验证。

> 使用 $xiapeng-action-coach，判断这个新品应该先做什么实验，写清继续、调整或停止的依据。

技能目录包含主说明、界面配置和8份参考文件，可直接使用，无需原始培训资料。参考文件中的来源代码用于说明方法依据；培训原稿、案例全文、本地备份和审计文件不在仓库中。该技能是方法整理与执行辅助，不代表夏鹏或相关机构的官方背书。

本次发布通过结构、相对引用及原版26项能力覆盖检查，并完成12个场景的自审推演；这些检查不代表真实经营效果已经验证。

## License

MIT

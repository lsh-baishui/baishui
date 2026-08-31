# human-short-video-writing

一个聚焦中文短视频观点口播的 Agent Skill。它用真实材料和可核事实形成单一核心判断，再完成开头、论证、反方、边界、口播和观众价值检查。

适合创作或改写个人 IP 观点稿、知识口播、商业观察、职场与自我成长内容，也可以只优化开头、诊断传播力和去除模板化表达。

不处理纯剧情短剧、镜头分镜、直播带货、挂车销售文案和知乎、公众号等长篇写作。

## 安装

从 GitHub 安装：

```bash
npx -y skills add lsh-hope/baishui -g --all
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
- 发布后将从真实 GitHub 远端验证上面的安装命令，并逐文件核对安装结果。

本地评测样本、预期答案、执行记录和个人路径不进入公开仓库。

## License

MIT

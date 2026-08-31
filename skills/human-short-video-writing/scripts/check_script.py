#!/usr/bin/env python3
"""检查中文短视频口播稿的机械风险，不自动改写文本。"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path


PLACEHOLDERS = (
    "TODO",
    "FIX" + "ME",
    "待补",
    "待填写",
    "此处补充",
    "补充案例",
    "补充数据",
)

WEAK_OPENERS = (
    "大家好",
    "今天我们来聊聊",
    "今天跟大家聊聊",
    "在这个时代",
    "随着时代的发展",
    "你有没有发现",
    "你知道吗",
    "三分钟告诉你",
)

META_TRANSITIONS = (
    "首先",
    "其次",
    "再次",
    "最后",
    "第一",
    "第二",
    "第三",
    "总而言之",
    "综上所述",
    "接下来",
)

AI_MARKERS = (
    "底层逻辑",
    "认知升级",
    "认知跃迁",
    "价值闭环",
    "商业闭环",
    "时代浪潮",
    "降本增效",
    "赋能",
    "抓手",
    "值得注意的是",
    "需要指出的是",
    "从某种意义上说",
    "更深一层",
    "还有一层",
    "说白了",
    "说穿了",
)

ABSOLUTE_MARKERS = (
    "所有人",
    "任何人都",
    "一定会",
    "必然会",
    "永远不会",
    "从来不会",
    "百分之百",
    "100%",
    "唯一答案",
)

PIVOT_PATTERNS = (
    re.compile(r"不是[^。！？\n]{1,70}而是"),
    re.compile(r"并非[^。！？\n]{1,70}而是"),
    re.compile(r"不在于[^。！？\n]{1,70}而在于"),
    re.compile(r"你以为[^。！？\n]{1,70}(?:其实|结果|但)"),
    re.compile(r"看似[^。！？\n]{1,70}(?:实则|其实|实际)"),
    re.compile(r"真正[^，。！？\n]{0,18}的是"),
)

SENTENCE_PATTERN = re.compile(r"[^。！？!?\n]+(?:[。！？!?]|$)")


def han_count(text: str) -> int:
    return len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]", text))


def line_number(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def excerpt(text: str, width: int = 46) -> str:
    value = re.sub(r"\s+", " ", text).strip()
    return value if len(value) <= width else value[: width - 1] + "…"


def read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def prose_only(text: str) -> str:
    """屏蔽代码块、网址和 Markdown 链接目标，避免把机器字段算进口播。"""

    def mask(match: re.Match[str]) -> str:
        return "".join("\n" if char == "\n" else " " for char in match.group())

    value = text
    for pattern in (
        re.compile(r"```.*?```", re.DOTALL),
        re.compile(r"`[^`\n]*`"),
        re.compile(r"\]\([^\n)]*\)"),
        re.compile(r"https?://[^\s)>]+"),
    ):
        value = pattern.sub(mask, value)
    return value


def term_hits(text: str, terms: tuple[str, ...]) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for term in terms:
        for match in re.finditer(re.escape(term), text, re.IGNORECASE):
            hits.append(
                {
                    "line": line_number(text, match.start()),
                    "term": match.group(),
                }
            )
    return sorted(hits, key=lambda item: (int(item["line"]), str(item["term"])))


def repeated_sentences(text: str) -> list[dict[str, object]]:
    values: list[tuple[str, int]] = []
    for match in SENTENCE_PATTERN.finditer(text):
        normalized = re.sub(r"[\s，,。！？!?]", "", match.group())
        if han_count(normalized) >= 6:
            values.append((normalized, line_number(text, match.start())))
    counts = collections.Counter(value for value, _ in values)
    results = []
    for value, count in counts.items():
        if count < 3:
            continue
        first_line = next(line for item, line in values if item == value)
        results.append({"line": first_line, "count": count, "text": excerpt(value)})
    return results


def long_sentences(text: str, threshold: int = 48) -> list[dict[str, object]]:
    results = []
    for match in SENTENCE_PATTERN.finditer(text):
        length = han_count(match.group())
        if length > threshold:
            results.append(
                {
                    "line": line_number(text, match.start()),
                    "han": length,
                    "text": excerpt(match.group()),
                }
            )
    return results


def pivot_hits(text: str) -> list[dict[str, object]]:
    results = []
    occupied: list[tuple[int, int]] = []
    for pattern in PIVOT_PATTERNS:
        for match in pattern.finditer(text):
            if any(match.start() < end and match.end() > start for start, end in occupied):
                continue
            occupied.append(match.span())
            results.append(
                {
                    "line": line_number(text, match.start()),
                    "text": excerpt(match.group()),
                }
            )
    return sorted(results, key=lambda item: int(item["line"]))


def analyze(text: str, seconds: int | None) -> dict[str, object]:
    prose = prose_only(text)
    total_han = han_count(prose)
    blockers: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []

    if total_han == 0:
        blockers.append({"code": "no_chinese", "message": "没有检测到中文口播内容。"})

    placeholders = term_hits(prose, PLACEHOLDERS)
    if placeholders:
        blockers.append(
            {
                "code": "unfinished_placeholder",
                "message": "成稿仍含未完成占位符。",
                "hits": placeholders,
            }
        )

    repeats = repeated_sentences(prose)
    if repeats:
        warnings.append(
            {
                "code": "repeated_sentence",
                "message": "同一句完整内容重复三次以上，确认这是有意反复，而非注水或复制错误。",
                "hits": repeats,
            }
        )

    stripped = re.sub(r"^[\s#>*_\-\d.、（）()]+", "", prose)
    weak = next((item for item in WEAK_OPENERS if stripped.startswith(item)), None)
    if weak:
        warnings.append(
            {
                "code": "weak_opener",
                "message": f"开头使用“{weak}”，尚未建立具体对象、冲突或收益。",
            }
        )

    transitions = term_hits(prose, META_TRANSITIONS)
    if len(transitions) >= 3:
        warnings.append(
            {
                "code": "template_transitions",
                "message": "结构路标出现三次以上，检查是否在用编号替代推进。",
                "hits": transitions,
            }
        )

    ai_hits = term_hits(prose, AI_MARKERS)
    if ai_hits:
        warnings.append(
            {
                "code": "abstract_or_ai_phrasing",
                "message": "发现容易抬高语气的抽象词或洞察路标，确认是否落到人、钱、时间和动作。",
                "hits": ai_hits,
            }
        )

    absolutes = term_hits(prose, ABSOLUTE_MARKERS)
    if absolutes:
        warnings.append(
            {
                "code": "absolute_claim",
                "message": "发现绝对化表达，核对证据与适用范围。",
                "hits": absolutes,
            }
        )

    pivots = pivot_hits(prose)
    if len(pivots) >= 2:
        warnings.append(
            {
                "code": "reversal_template",
                "message": "翻转句式出现两次以上，检查冲突是否来自事实，而非句型。",
                "hits": pivots,
            }
        )

    long_items = long_sentences(prose)
    if long_items:
        warnings.append(
            {
                "code": "long_sentence",
                "message": "发现超过 48 个汉字的句子，请完整读出声。",
                "hits": long_items,
            }
        )

    question_count = len(re.findall(r"[？?]", prose))
    if question_count >= 4:
        warnings.append(
            {
                "code": "question_density",
                "message": f"全文有 {question_count} 个问号，检查是否在连续制造悬念。",
            }
        )

    estimated = None
    if total_han:
        estimated = {
            "fast_seconds": round(total_han / 4.5),
            "slow_seconds": round(total_han / 3.5),
        }

    if seconds and total_han:
        lower = seconds * 3.5
        upper = seconds * 4.5
        if total_han < lower * 0.85 or total_han > upper * 1.15:
            warnings.append(
                {
                    "code": "duration_mismatch",
                    "message": (
                        f"目标 {seconds} 秒通常约 {round(lower)}～{round(upper)} 个汉字，"
                        f"当前为 {total_han} 个。实际仍需朗读计时。"
                    ),
                }
            )

    return {
        "han_count": total_han,
        "estimated_duration": estimated,
        "target_seconds": seconds,
        "blockers": blockers,
        "warnings": warnings,
    }


def render_text(report: dict[str, object]) -> None:
    print(f"汉字数 {report['han_count']}")
    duration = report["estimated_duration"]
    if isinstance(duration, dict):
        print(f"估算时长 {duration['fast_seconds']}～{duration['slow_seconds']} 秒，仍需真人朗读确认")

    for title, key in (("阻断项", "blockers"), ("需要人工判断", "warnings")):
        items = report[key]
        if not isinstance(items, list) or not items:
            continue
        print(f"\n{title}")
        for item in items:
            if not isinstance(item, dict):
                continue
            print(f"- {item['message']}")
            hits = item.get("hits")
            if isinstance(hits, list):
                for hit in hits[:6]:
                    if isinstance(hit, dict):
                        detail = hit.get("term") or hit.get("text") or ""
                        print(f"  第 {hit.get('line', '?')} 行 {detail}")

    if not report["blockers"] and not report["warnings"]:
        print("\n未发现这份检查器覆盖的机械风险。")


def main() -> int:
    parser = argparse.ArgumentParser(description="检查中文短视频口播稿的机械风险")
    parser.add_argument("path", help="UTF-8 文本或 Markdown 路径；使用 - 从标准输入读取")
    parser.add_argument("--seconds", type=int, help="目标口播秒数，必须大于 0")
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    parser.add_argument("--strict", action="store_true", help="有任何警告时返回非零状态")
    args = parser.parse_args()

    if args.seconds is not None and args.seconds <= 0:
        parser.error("--seconds 必须大于 0")

    try:
        text = read_text(args.path)
    except (OSError, UnicodeError) as error:
        print(f"无法读取稿件：{error}", file=sys.stderr)
        return 2

    report = analyze(text, args.seconds)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        render_text(report)

    if report["blockers"]:
        return 1
    if args.strict and report["warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

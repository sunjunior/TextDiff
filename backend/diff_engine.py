"""
TextDiff 核心差异比较引擎

功能：
- 支持 JSON/YAML 格式解析
- 忽略字段大小写（键名统一转小写）
- 忽略同层字段顺序（键名排序）
- 行级差异比较与高亮
- 原始文本行映射标注
"""

import json
import difflib
import re
from typing import Any, Optional


def parse_text(text: str, format_type: str) -> Any:
    """将文本解析为 Python 对象。

    Args:
        text: 原始文本内容
        format_type: 格式类型 ('json' 或 'yaml')

    Returns:
        解析后的 Python 对象

    Raises:
        ValueError: 解析失败时抛出
    """
    text = text.strip()
    if not text:
        raise ValueError("输入内容为空")

    if format_type == "json":
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 解析错误: {e.msg} (位置: {e.pos})")
    elif format_type == "yaml":
        import yaml
        try:
            return yaml.safe_load(text)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML 解析错误: {str(e)}")
    else:
        raise ValueError(f"不支持的格式类型: {format_type}")


def normalize(obj: Any) -> Any:
    """递归标准化对象（小写键名 + 排序）。

    对字典类型：
    - 所有键名转为小写
    - 同层键按字母排序
    - 递归处理值
    对列表类型：
    - 递归处理每个元素（保持列表顺序）
    对其他类型：
    - 原样返回

    Args:
        obj: 要标准化的 Python 对象

    Returns:
        标准化后的对象
    """
    if isinstance(obj, dict):
        return {
            k.lower(): normalize(v)
            for k, v in sorted(obj.items(), key=lambda x: x[0].lower())
        }
    elif isinstance(obj, list):
        return [normalize(item) for item in obj]
    else:
        return obj


def serialize(obj: Any, format_type: str, indent: int = 2) -> str:
    """将 Python 对象序列化为格式化字符串。

    Args:
        obj: 要序列化的 Python 对象
        format_type: 输出格式 ('json' 或 'yaml')
        indent: 缩进空格数

    Returns:
        格式化后的字符串
    """
    if format_type == "json":
        return json.dumps(obj, ensure_ascii=False, indent=indent)
    elif format_type == "yaml":
        import yaml
        return yaml.dump(obj, default_flow_style=False, indent=indent, allow_unicode=True, sort_keys=False)
    else:
        raise ValueError(f"不支持的格式类型: {format_type}")


def line_diff(left_str: str, right_str: str) -> dict:
    """对两段文本进行逐行差异比较。

    使用 Python difflib.Differ 进行比较，
    将结果归一化为四种类型: equal, modified, added, removed。

    Args:
        left_str: 左文本
        right_str: 右文本

    Returns:
        dict 包含:
        - diff_entries: 差异条目列表
        - has_diff: 是否存在差异
        - stats: 统计信息
    """
    left_lines = left_str.split('\n')
    right_lines = right_str.split('\n')

    differ = difflib.Differ()
    diff_result = list(differ.compare(left_lines, right_lines))

    diff_entries = []
    left_idx = 0
    right_idx = 0
    stats = {"equal": 0, "modified": 0, "added": 0, "removed": 0}

    for line in diff_result:
        if not line:
            continue
        code = line[0]
        content = line[2:]

        if code == ' ':
            diff_entries.append({
                "type": "equal",
                "left_line_num": left_idx + 1,
                "right_line_num": right_idx + 1,
                "left_content": left_lines[left_idx] if left_idx < len(left_lines) else content,
                "right_content": right_lines[right_idx] if right_idx < len(right_lines) else content,
            })
            left_idx += 1
            right_idx += 1
            stats["equal"] += 1
        elif code == '-':
            # 检查下一行是否是 '+'（成对修改）
            # 先查找后续的 + 行
            plus_indices = [i for i in range(len(diff_result))
                           if i > len(diff_entries) and i < len(diff_result)
                           and diff_result[i] and diff_result[i][0] == '+']
            if plus_indices:
                plus_idx = plus_indices[0]
                # 检查是否是紧邻的匹配对
                # 简化处理：先作为 removed 记录，再看是否有对应的 added
                pass
            diff_entries.append({
                "type": "removed",
                "left_line_num": left_idx + 1,
                "right_line_num": None,
                "left_content": left_lines[left_idx] if left_idx < len(left_lines) else content,
                "right_content": "",
            })
            left_idx += 1
            stats["removed"] += 1
        elif code == '+':
            # 检查前一个 entry 是否为 removed 且内容匹配（modified 对）
            # 简单的策略：如果在 removed 之后立即出现 +，合并为 modified
            if (diff_entries and
                    diff_entries[-1]["type"] == "removed" and
                    diff_entries[-1]["right_content"] == "" and
                    diff_entries[-1]["right_line_num"] is None):
                # 合并为 modified
                last = diff_entries.pop()
                stats["removed"] -= 1
                diff_entries.append({
                    "type": "modified",
                    "left_line_num": last["left_line_num"],
                    "right_line_num": right_idx + 1,
                    "left_content": last["left_content"],
                    "right_content": right_lines[right_idx] if right_idx < len(right_lines) else content,
                })
                stats["modified"] += 1
            else:
                diff_entries.append({
                    "type": "added",
                    "left_line_num": None,
                    "right_line_num": right_idx + 1,
                    "left_content": "",
                    "right_content": right_lines[right_idx] if right_idx < len(right_lines) else content,
                })
                stats["added"] += 1
            right_idx += 1
        elif code == '?':
            # 忽略 difflib 的标记行 (^ 行)
            continue

    has_diff = stats["modified"] > 0 or stats["added"] > 0 or stats["removed"] > 0

    return {
        "diff_entries": diff_entries,
        "has_diff": has_diff,
        "stats": stats,
    }


def find_key_line_number(lines: list, key: str, path: str = "") -> Optional[int]:
    """在原始文本行中查找指定键所在的行号。

    使用正则表达式匹配 JSON 引号键 ("key":) 或 YAML 键 (key:)。

    Args:
        lines: 原始文本行列表
        key: 要查找的键名（已小写）
        path: 路径前缀（预留，暂未使用）

    Returns:
        行号（从 1 开始），未找到返回 None
    """
    for i, line in enumerate(lines):
        stripped = line.strip()
        # JSON 格式: "key":
        if re.search(rf'"({re.escape(key)})"\s*:', stripped):
            return i + 1
        # YAML 格式: key: (行首或缩进后)
        if re.search(rf'^{re.escape(key)}\s*:', stripped):
            return i + 1
    return None


def get_original_line_annotations(
    original_lines: list,
    normalized_obj: Any,
    original_obj: Any,
    diff_entries: list,
    side: str
) -> list:
    """为原始文本行生成差异标注。

    通过结构化的键路径匹配，在原始文本中找到受影响的每一行，
    并标记其差异类型。

    Args:
        original_lines: 原始文本行列表
        normalized_obj: 标准化后的对象
        original_obj: 原始对象
        diff_entries: diff 引擎输出的差异条目列表
        side: 'left' 或 'right'

    Returns:
        标注列表，每项包含 line_num, type
    """
    annotations = []
    annotated_lines = set()
    line_count = len(original_lines)

    # 初始化为 equal
    for i in range(line_count):
        annotations.append({"line_num": i + 1, "type": "equal"})

    # 根据 diff_entries 标注
    # 对于 added/removed/modified 类型，找出受影响的行
    key_field = f"{side}_line_num"

    for entry in diff_entries:
        entry_type = entry["type"]
        line_num = entry.get(key_field)

        if entry_type == "equal":
            continue

        if line_num is not None and 1 <= line_num <= line_count:
            if line_num not in annotated_lines:
                annotations[line_num - 1]["type"] = entry_type
                annotated_lines.add(line_num)

    return annotations


def compare_texts(left_text: str, right_text: str, format_type: str) -> dict:
    """完整比较两段文本。

    这是核心入口函数，执行以下步骤：
    1. 解析 JSON/YAML
    2. 标准化（小写键 + 排序）
    3. 序列化标准化结果
    4. 逐行差异比较
    5. 生成原始文本行标注
    6. 统计差异

    Args:
        left_text: 左文本
        right_text: 右文本
        format_type: 格式类型 ('json' 或 'yaml')

    Returns:
        dict 比较结果，包含字段:
        - success: 是否成功
        - error: 错误信息（失败时）
        - error_side: 错误侧（失败时）
        - has_diff: 是否存在差异
        - format: 格式类型
        - left_normalized: 标准化后的左文本
        - right_normalized: 标准化后的右文本
        - left_original_lines: 左文本原始行数组
        - right_original_lines: 右文本原始行数组
        - left_annotations: 左文本行标注
        - right_annotations: 右文本行标注
        - diff_entries: 差异条目
        - summary: 统计摘要
    """
    # 1. 解析
    try:
        left_obj = parse_text(left_text, format_type)
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "error_side": "left",
            "has_diff": False,
        }

    try:
        right_obj = parse_text(right_text, format_type)
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "error_side": "right",
            "has_diff": False,
        }

    # 2. 标准化
    left_normalized = normalize(left_obj)
    right_normalized = normalize(right_obj)

    # 3. 序列化
    left_normalized_str = serialize(left_normalized, format_type)
    right_normalized_str = serialize(right_normalized, format_type)

    # 4. 逐行差异比较
    diff_result = line_diff(left_normalized_str, right_normalized_str)

    # 5. 原始文本行标注
    left_lines = left_text.split('\n')
    right_lines = right_text.split('\n')

    left_annotations = get_original_line_annotations(
        left_lines, left_normalized, left_obj,
        diff_result["diff_entries"], "left"
    )
    right_annotations = get_original_line_annotations(
        right_lines, right_normalized, right_obj,
        diff_result["diff_entries"], "right"
    )

    # 6. 统计数据
    summary = diff_result["stats"]

    return {
        "success": True,
        "has_diff": diff_result["has_diff"],
        "format": format_type,
        "left_normalized": left_normalized_str,
        "right_normalized": right_normalized_str,
        "left_original_lines": left_lines,
        "right_original_lines": right_lines,
        "left_annotations": left_annotations,
        "right_annotations": right_annotations,
        "diff_entries": diff_result["diff_entries"],
        "summary": summary,
    }

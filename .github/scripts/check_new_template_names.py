#!/usr/bin/env python3
"""只检查「本次 PR 新增」的模板文件命名。

存量命名（OnePlus_13.toml、huawei_mate_40_pro+.toml、huawei_matepad_10.8英寸.toml 等）
是既成事实，做全树扫描只会让每个 PR 都刷几十条噪音，因此不再检查它们。

对新增文件只对「大写字母 / 空白 / 控制字符」告警：
现有约定允许小写字母、数字、下划线、短横线、点号（尺寸）、加号（Pro+）与中文后缀，
而大写、空格、控制字符在 URL、shell 脚本和生成的模板 key 里最容易出问题。

用法（stdin 传入 git diff --name-only --diff-filter=A 的输出）：
    git diff --name-only --diff-filter=A "$BASE_SHA"...HEAD -- templates/ \
      | python .github/scripts/check_new_template_names.py
"""

import os
import re
import sys

# 不用 POSIX 字符类（[[:upper:]] / [[:cntrl:]] 在 C.UTF-8 下会误判中文字符），
# 这里用 Python 显式判定，与 locale 无关。
BAD_PATTERN = re.compile(r"[A-Z]|\s")


def is_bad_name(name: str) -> bool:
    if BAD_PATTERN.search(name):
        return True
    return any(ord(ch) < 32 or ord(ch) == 127 for ch in name)


def main() -> int:
    paths = [line.strip() for line in sys.stdin if line.strip().endswith(".toml")]
    if not paths:
        print("本次 PR 未新增 .toml 模板文件，跳过命名检查。")
        return 0

    warned = 0
    for path in paths:
        name = os.path.basename(path)
        if is_bad_name(name):
            print(
                f"::warning file={path}::新增模板文件名建议只用小写字母、数字、下划线、短横线、"
                f"点号、加号和中文（避免大写字母、空格与控制字符）。({name})"
            )
            warned += 1

    print(f"本次新增 {len(paths)} 个模板文件，命名告警 {warned} 个。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

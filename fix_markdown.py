"""
One-time repair script: fixes markdown files that got corrupted with
escaped special characters (\#, \*, \_, etc.) and broken paragraph
line-breaks during copy-paste. Run this from your flam_submission
folder. Safe to run multiple times - does nothing to already-clean files.
"""
import re
import glob
import os

files = glob.glob("**/*.md", recursive=True)
files = [f for f in files if ".venv" not in f and ".git" not in f]

fixed_count = 0
for f in files:
    with open(f, "r", encoding="utf-8") as fh:
        content = fh.read()

    if "\\#" not in content and "\\*" not in content and "\\_" not in content and "\\&" not in content and "\\-" not in content and "&#x20;" not in content:
        continue  # already clean, skip

    blocks = re.split(r'\n{4,}', content)
    fixed_blocks = []
    for block in blocks:
        lines = block.split('\n\n')
        is_table = any(l.strip().startswith('|') for l in lines)
        is_list = len(lines) > 1 and all(
            l.strip().startswith(('-', '*', '\\-', '\\*')) or re.match(r'^\d+\\?\.', l.strip()) or l.strip() == ''
            for l in lines
        )
        if is_table or is_list:
            joined = '\n'.join(l.strip() for l in lines if l.strip() != '')
        else:
            joined = ' '.join(l.strip() for l in lines if l.strip() != '')
        fixed_blocks.append(joined)

    fixed = '\n\n'.join(fixed_blocks)
    fixed = re.sub(r'\\([#*_~\[\]()&.\-])', r'\1', fixed)
    fixed = fixed.replace('&#x20;', ' ')
    fixed = fixed.strip() + '\n'

    with open(f, "w", encoding="utf-8") as fh:
        fh.write(fixed)
    print(f"FIXED: {f}")
    fixed_count += 1

print(f"\nDone. Fixed {fixed_count} file(s).")
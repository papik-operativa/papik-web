#!/usr/bin/env python3
"""
Inject a shared <link rel="stylesheet" href="(…)css/header.css"> into every
HTML file under public/, placed IMMEDIATELY before </head> so that it loads
AFTER all inline <style> blocks and wins the cascade at equal specificity.

Idempotent: if the link is already present, the file is skipped.
"""
from pathlib import Path

ROOT = Path("/Users/trisfisas/Desktop/CÓDIGO/papik-web/public")
MARKER = "<!-- PAPIK:SHARED-HEADER-CSS -->"

def link_tag(relative_prefix: str) -> str:
    return (
        f'  {MARKER}\n'
        f'  <link rel="stylesheet" href="{relative_prefix}css/header.css">\n'
    )

touched, skipped, not_matched = [], [], []

for html_path in ROOT.rglob("*.html"):
    # Compute the relative prefix to css/header.css from this file's folder
    try:
        rel = Path("css/header.css").resolve()
    except Exception:
        pass
    depth = len(html_path.relative_to(ROOT).parts) - 1  # 0 for root, 1 for es/, …
    prefix = "../" * depth

    text = html_path.read_text(encoding="utf-8")

    if MARKER in text:
        skipped.append(str(html_path.relative_to(ROOT)))
        continue

    if "</head>" not in text:
        not_matched.append(str(html_path.relative_to(ROOT)))
        continue

    new_text = text.replace("</head>", link_tag(prefix) + "</head>", 1)
    html_path.write_text(new_text, encoding="utf-8")
    touched.append(str(html_path.relative_to(ROOT)))

print(f"Touched:     {len(touched)}")
print(f"Skipped:     {len(skipped)}")
print(f"No </head>:  {len(not_matched)}")
if not_matched:
    print("  Files without </head>:")
    for f in not_matched:
        print(f"    - {f}")

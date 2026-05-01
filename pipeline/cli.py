"""CLI orchestrator for the SEO inject pipeline (Mode B).

Mode B reads each page declared in seo-internal/slug-mapping.json, finds the
matching HTML file under public/, and injects a `<!-- papik-pipeline -->` block
in the <head> containing:

    - <link rel="alternate" hreflang="..."> tags (one per locale + x-default)
    - <script type="application/ld+json"> blocks with the schema appropriate
      to the page type (Article, CreativeWork, LocalBusiness, Service,
      BreadcrumbList, etc. — see seo-internal/schemas/)

If a page already has its own <script type="application/ld+json"> outside the
pipeline block (e.g. placed by generate_html.py), the pipeline ONLY adds
hreflang and leaves the schema alone — never duplicates.

Idempotent: re-running strips the previous pipeline block before writing a
fresh one, so it is safe to run repeatedly.

Usage:
    python -m pipeline.cli inject [--dry-run] [-v]
    python -m pipeline.cli inject --only-id article-principis-passivhaus
    python -m pipeline.cli inject --only-locale ca
    python -m pipeline.cli inject --only-type article
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

from .lib import LOCALES, load_pages
from .inject import inject_into_file


def _filter_pages(pages, *, only_id=None, only_type=None):
    out = []
    for p in pages:
        if only_id and p.id != only_id:
            continue
        if only_type and p.type != only_type:
            continue
        out.append(p)
    return out


def cmd_inject(args):
    pages = _filter_pages(load_pages(), only_id=args.only_id, only_type=args.only_type)
    locales = [args.only_locale] if args.only_locale else list(LOCALES)

    by_status: dict[str, int] = defaultdict(int)
    failures = []

    for page in pages:
        for loc in locales:
            r = inject_into_file(page, loc, dry_run=args.dry_run)
            if r.success:
                by_status["success"] += 1
                if r.schemas_skipped_pre_existing:
                    by_status["success (hreflang only, schema preserved)"] += 1
                if args.verbose:
                    rel = r.file.relative_to(Path.cwd()) if r.file.is_absolute() else r.file
                    note = " (schema kept)" if r.schemas_skipped_pre_existing else ""
                    print(f"  OK  {page.id:<40} {loc}  schemas={r.schemas_added} hreflang={r.hreflang_added}{note}  {rel}")
            else:
                key = r.skipped_reason or r.error or "unknown"
                by_status[key] += 1
                if r.error:
                    failures.append(r)
                if args.verbose and r.error:
                    print(f"  ERR {page.id:<40} {loc}  {r.error}", file=sys.stderr)

    print()
    print("=== Inject summary ===")
    if args.dry_run:
        print("(DRY RUN — no files written)")
    print(f"{'success':<48}: {by_status['success']}")
    for k, v in sorted(by_status.items(), key=lambda x: -x[1]):
        if k == "success":
            continue
        print(f"{k:<48}: {v}")

    if failures:
        print()
        print(f"=== {len(failures)} failures (excluding skips) ===")
        for r in failures[:20]:
            print(f"  {r.page_id:<40} {r.locale}  {r.error}")
        if len(failures) > 20:
            print(f"  ... and {len(failures) - 20} more")
        return 1
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pipeline", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dry-run", action="store_true")
    common.add_argument("--only-locale", choices=LOCALES)
    common.add_argument("--only-type")
    common.add_argument("--only-id")
    common.add_argument("--verbose", "-v", action="store_true")

    p_inject = sub.add_parser("inject", parents=[common],
                              help="Inject schema+hreflang into existing HTML files")
    p_inject.set_defaults(func=cmd_inject)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

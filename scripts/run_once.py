#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from outlook_autoresponder.runner import run_once, run_loop


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--instance', default='', help='Instance name under instances/<name>/')
    parser.add_argument('--limit', type=int, default=3, help='Max messages to process in one run')
    parser.add_argument('--all-instances', action='store_true', help='Run all configured instances in sequence')
    parser.add_argument('--loop', action='store_true', help='Keep polling continuously')
    parser.add_argument('--poll-seconds', type=int, default=0, help='Override poll interval in seconds')
    parser.add_argument('--dry-run', action='store_true', help='Generate previews without creating Outlook drafts or marking messages processed')
    args = parser.parse_args()
    if args.loop:
        run_loop(
            limit=args.limit,
            instance_name=args.instance or None,
            all_instances=args.all_instances,
            poll_seconds=args.poll_seconds or None,
            dry_run=args.dry_run,
        )
        return
    run_once(
        limit=args.limit,
        instance_name=args.instance or None,
        all_instances=args.all_instances,
        dry_run=args.dry_run,
    )


if __name__ == '__main__':
    main()

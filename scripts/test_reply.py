#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from outlook_autoresponder import config
from outlook_autoresponder.models import EmailMessage
from outlook_autoresponder.kb import load_kb_documents, simple_search
from outlook_autoresponder.policy import classify_message
from outlook_autoresponder.responder import generate_reply, llm_connection_help_text


def build_message(args, payload):
    return EmailMessage(
        id='local-test-message',
        internet_message_id='local-test-message',
        subject=(args.subject or payload.get('subject') or '').strip(),
        from_name=(args.from_name or payload.get('from_name') or '').strip(),
        from_address=(args.from_address or payload.get('from_address') or '').strip(),
        received_at='local-test',
        body_preview=(args.body or payload.get('body') or '').strip()[:300],
        body_text=(args.body or payload.get('body') or '').strip(),
    )


def load_payload(path_value: str):
    if not path_value:
        return {}
    path = Path(path_value)
    if not path.exists():
        raise FileNotFoundError(f'Input file not found: {path}')
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--instance', default='', help='Instance name under instances/<name>/')
    parser.add_argument('--input', default='', help='Path to JSON email fixture')
    parser.add_argument('--subject', default='', help='Email subject override')
    parser.add_argument('--from-name', default='', help='Sender name override')
    parser.add_argument('--from-address', default='', help='Sender email override')
    parser.add_argument('--body', default='', help='Email body override')
    parser.add_argument('--kb-limit', type=int, default=5, help='Max KB hits to show')
    args = parser.parse_args()

    instance = config.load_instance(args.instance or None)
    payload = load_payload(args.input)
    message = build_message(args, payload)
    if not message.subject and not message.body_text:
        raise RuntimeError('Provide --input or at least --subject/--body for a local test')

    docs = load_kb_documents(instance['kb_path'])
    query = f"{message.subject} {message.body_text}"
    hits = simple_search(query, docs, limit=args.kb_limit)
    decision = classify_message(message, hits)
    try:
        reply = generate_reply(message, hits, decision)
    except Exception as exc:
        print(f'LLM_ERROR={exc}')
        print(llm_connection_help_text())
        raise

    print(f"INSTANCE={instance['instance_name']}")
    print(f"MAILBOX={instance['microsoft_user_email'] or 'local-test-only'}")
    print(f"KB_PATH={instance['kb_path']}")
    print('--- MESSAGE ---')
    print(f"SUBJECT={message.subject}")
    print(f"FROM={message.from_name} <{message.from_address}>")
    print(message.body_text)
    print('--- DECISION ---')
    print(f"ACTION={decision.action}")
    print(f"CONFIDENCE={decision.confidence}")
    print(f"REASONS={','.join(decision.reasons)}")
    print('--- KB HITS ---')
    if not hits:
        print('NO_KB_HITS')
    else:
        for idx, hit in enumerate(hits, start=1):
            print(f"[{idx}] score={hit.score} path={hit.path}")
            print(hit.text[:1200])
            print('---')
    print('--- REPLY ---')
    print(reply)


if __name__ == '__main__':
    main()

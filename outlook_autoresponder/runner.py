import time
from pathlib import Path

from .graph_client import get_access_token, graph_get, graph_post, graph_patch
from .kb import load_kb_documents, simple_search
from .responder import generate_reply
from .policy import classify_message
from .storage import is_processed, mark_processed
from .models import EmailMessage
from . import config


def fetch_recent_messages(token: str, mailbox_email: str):
    path = (
        f"/users/{mailbox_email}/mailFolders/inbox/messages"
        "?$top=10"
        "&$orderby=receivedDateTime desc"
        "&$select=id,internetMessageId,subject,from,receivedDateTime,bodyPreview,isRead"
    )
    payload = graph_get(path, token)
    return payload.get('value', [])


def fetch_message_body(token: str, mailbox_email: str, message_id: str):
    payload = graph_get(
        f"/users/{mailbox_email}/messages/{message_id}?$select=body",
        token,
    )
    body = payload.get('body') or {}
    return (body.get('content') or '').strip()


def create_draft_reply(token: str, mailbox_email: str, message_id: str, body_text: str, dry_run: bool = False):
    if dry_run:
        return 'dry-run-no-draft-created'
    draft = graph_post(f"/users/{mailbox_email}/messages/{message_id}/createReply", token, {})
    draft_id = draft.get('id')
    if not draft_id:
        raise RuntimeError('Outlook draft reply did not return an id')
    graph_patch(
        f"/users/{mailbox_email}/messages/{draft_id}",
        token,
        {
            'body': {
                'contentType': 'Text',
                'content': body_text,
            }
        },
    )
    return draft_id


def normalize_message(row, body_text: str):
    sender = (row.get('from') or {}).get('emailAddress') or {}
    return EmailMessage(
        id=row.get('id', ''),
        internet_message_id=row.get('internetMessageId', ''),
        subject=row.get('subject', ''),
        from_name=sender.get('name', ''),
        from_address=sender.get('address', ''),
        received_at=row.get('receivedDateTime', ''),
        body_preview=row.get('bodyPreview', ''),
        body_text=body_text,
    )


def discover_instances():
    if not config.INSTANCES_DIR.exists():
        return []
    return [path.name for path in sorted(config.INSTANCES_DIR.iterdir()) if path.is_dir()]


def log_instance_line(instance_name: str, log_dir: Path, line: str):
    log_dir.mkdir(parents=True, exist_ok=True)
    with (log_dir / f'{instance_name}.log').open('a') as fh:
        fh.write(line.rstrip() + '\n')


def process_instance(limit: int = 3, instance_name: str | None = None, dry_run: bool = False):
    instance = config.load_instance(instance_name)
    mailbox_email = instance['microsoft_user_email']
    kb_path = instance['kb_path']
    data_path = instance['data_path']
    if not mailbox_email:
        raise RuntimeError(f"MICROSOFT_USER_EMAIL is not configured for instance {instance['instance_name']}")

    token = get_access_token()
    docs = load_kb_documents(kb_path)
    messages = fetch_recent_messages(token, mailbox_email)
    processed = 0
    log_dir = config.BASE_DIR / 'logs'

    header_lines = [
        f"INSTANCE={instance['instance_name']}",
        f"MAILBOX={mailbox_email}",
        f"KB_PATH={kb_path}",
        f"DATA_PATH={data_path}",
        f"DRY_RUN={str(dry_run).lower()}",
        '---',
    ]
    for line in header_lines:
        print(line)
        log_instance_line(instance['instance_name'], log_dir, line)

    for row in messages:
        message_id = row.get('id')
        if not message_id or is_processed(data_path, message_id):
            continue
        body_text = fetch_message_body(token, mailbox_email, message_id)
        message = normalize_message(row, body_text)
        query = f"{message.subject} {message.body_preview} {message.body_text}"
        hits = simple_search(query, docs)
        decision = classify_message(message, hits)
        reply = generate_reply(message, hits, decision)
        draft_id = create_draft_reply(token, mailbox_email, message.id, reply, dry_run=dry_run)
        if not dry_run:
            mark_processed(data_path, message.id)
        processed += 1
        block = [
            f"MESSAGE={message.id}",
            f"FROM={message.from_name} <{message.from_address}>",
            f"SUBJECT={message.subject}",
            f"CONFIDENCE={decision.confidence}",
            f"REASONS={','.join(decision.reasons)}",
            f"KB_HITS={len(hits)}",
            f"DRAFT_ID={draft_id}",
            'REPLY_PREVIEW_START',
            reply,
            'REPLY_PREVIEW_END',
            '---',
        ]
        for line in block:
            print(line)
            log_instance_line(instance['instance_name'], log_dir, line)
        if processed >= limit:
            break
    footer = f"PROCESSED={processed}"
    print(footer)
    log_instance_line(instance['instance_name'], log_dir, footer)
    return processed


def run_once(limit: int = 3, instance_name: str | None = None, all_instances: bool = False, dry_run: bool = False):
    if all_instances:
        total = 0
        for name in discover_instances():
            total += process_instance(limit=limit, instance_name=name, dry_run=dry_run)
        print(f"ALL_INSTANCES_PROCESSED={total}")
        return total
    return process_instance(limit=limit, instance_name=instance_name, dry_run=dry_run)


def run_loop(limit: int = 3, instance_name: str | None = None, all_instances: bool = False, poll_seconds: int | None = None, dry_run: bool = False):
    poll_seconds = poll_seconds or config.POLL_SECONDS
    while True:
        try:
            run_once(limit=limit, instance_name=instance_name, all_instances=all_instances, dry_run=dry_run)
        except Exception as exc:
            print(f"LOOP_ERROR={exc}")
        time.sleep(poll_seconds)


if __name__ == '__main__':
    run_once()

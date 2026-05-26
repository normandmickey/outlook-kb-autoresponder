import httpx
from openai import OpenAI
from . import config


def build_reply_prompt(message, kb_docs, decision):
    kb_blob = '\n\n'.join(f"Source: {doc.path}\n{doc.text[:2000]}" for doc in kb_docs)
    return f"""You are drafting an email response grounded in the provided knowledge base.

Incoming email subject: {message.subject}
Incoming email from: {message.from_name} <{message.from_address}>
Incoming email body:
{message.body_text or message.body_preview}

Decision context:
- action: {decision.action}
- confidence: {decision.confidence}
- reasons: {', '.join(decision.reasons)}

Knowledge base:
{kb_blob}

Write a concise, helpful, professional email reply in plain text.
If the knowledge base is insufficient, say what is missing and do not invent policy or facts.
"""


def generate_reply(message, kb_docs, decision):
    if not config.LLM_BASE_URL or not config.LLM_MODEL:
        raise RuntimeError('LLM_BASE_URL and LLM_MODEL must be set in your local .env or instance .env')
    verify = config.LLM_CA_BUNDLE or config.LLM_VERIFY_SSL
    http_client = httpx.Client(verify=verify, timeout=120.0)
    client = OpenAI(
        api_key=config.OPENAI_API_KEY or 'local',
        base_url=config.LLM_BASE_URL,
        http_client=http_client,
    )
    prompt = build_reply_prompt(message, kb_docs, decision)
    resp = client.responses.create(
        model=config.LLM_MODEL,
        input=prompt,
        temperature=config.LLM_TEMPERATURE,
        max_output_tokens=config.LLM_MAX_TOKENS,
    )
    return (resp.output_text or '').strip()



def llm_connection_help_text():
    return (
        'LLM connection failed. If your in-house endpoint uses a self-signed certificate, either '
        'set LLM_VERIFY_SSL=false for local testing or set LLM_CA_BUNDLE to a PEM file that trusts that cert.'
    )

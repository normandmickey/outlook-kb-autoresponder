from .models import ReplyDecision

SENSITIVE_MARKERS = ['invoice', 'payment', 'wire', 'refund', 'legal', 'lawsuit', 'contract', 'termination']


def classify_message(message, kb_hits):
    text = f"{message.subject} {message.body_preview} {message.body_text}".lower()
    decision = ReplyDecision(action='draft', confidence='low', reasons=[])
    if any(marker in text for marker in SENSITIVE_MARKERS):
        decision.reasons.append('sensitive_topic')
        return decision
    if kb_hits:
        decision.confidence = 'medium'
        decision.reasons.append('kb_match_found')
    else:
        decision.reasons.append('no_kb_match')
    return decision

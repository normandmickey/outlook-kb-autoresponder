from dataclasses import dataclass, field
from typing import List


@dataclass
class EmailMessage:
    id: str
    internet_message_id: str
    subject: str
    from_name: str
    from_address: str
    received_at: str
    body_preview: str
    body_text: str = ''


@dataclass
class KnowledgeHit:
    path: str
    text: str
    score: int = 0


@dataclass
class ReplyDecision:
    action: str = 'draft'
    confidence: str = 'low'
    reasons: List[str] = field(default_factory=list)

from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_KB_PATH = BASE_DIR / 'knowledge_base'
DEFAULT_DATA_PATH = BASE_DIR / 'data'
INSTANCES_DIR = BASE_DIR / 'instances'

load_dotenv()

MICROSOFT_TENANT_ID = os.getenv('MICROSOFT_TENANT_ID', '')
MICROSOFT_CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID', '')
MICROSOFT_CLIENT_SECRET = os.getenv('MICROSOFT_CLIENT_SECRET', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
LLM_BASE_URL = os.getenv('LLM_BASE_URL', '').strip()
LLM_MODEL = os.getenv('LLM_MODEL', '').strip()
LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.10'))
LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '1500'))
LLM_CA_BUNDLE = os.getenv('LLM_CA_BUNDLE', '').strip()
LLM_VERIFY_SSL = os.getenv('LLM_VERIFY_SSL', 'true').strip().lower() not in {'0', 'false', 'no'}
MODE = os.getenv('OUTLOOK_AUTORESPONDER_MODE', 'draft').strip().lower()
POLL_SECONDS = int(os.getenv('OUTLOOK_AUTORESPONDER_POLL_SECONDS', '120'))


def load_instance(instance_name: str | None = None):
    instance_name = (instance_name or '').strip()
    if instance_name:
        instance_dir = INSTANCES_DIR / instance_name
        instance_env = instance_dir / '.env'
        if instance_env.exists():
            load_dotenv(instance_env, override=True)
        kb_path = Path(os.getenv('KB_PATH', instance_dir / 'knowledge_base'))
        data_path = Path(os.getenv('DATA_PATH', instance_dir / 'data'))
    else:
        kb_path = Path(os.getenv('KB_PATH', DEFAULT_KB_PATH))
        data_path = Path(os.getenv('DATA_PATH', DEFAULT_DATA_PATH))
    return {
        'instance_name': instance_name or 'default',
        'kb_path': kb_path,
        'data_path': data_path,
        'microsoft_user_email': os.getenv('MICROSOFT_USER_EMAIL', ''),
        'mode': os.getenv('OUTLOOK_AUTORESPONDER_MODE', MODE).strip().lower(),
    }

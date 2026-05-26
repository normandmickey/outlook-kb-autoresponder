import requests
from . import config

TOKEN_URL = 'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token'
GRAPH_ROOT = 'https://graph.microsoft.com/v1.0'


def get_access_token() -> str:
    resp = requests.post(
        TOKEN_URL.format(tenant=config.MICROSOFT_TENANT_ID),
        data={
            'client_id': config.MICROSOFT_CLIENT_ID,
            'client_secret': config.MICROSOFT_CLIENT_SECRET,
            'scope': 'https://graph.microsoft.com/.default',
            'grant_type': 'client_credentials',
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()['access_token']


def _headers(token: str):
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


def graph_get(path: str, token: str):
    resp = requests.get(f'{GRAPH_ROOT}{path}', headers=_headers(token), timeout=30)
    resp.raise_for_status()
    return resp.json()


def graph_post(path: str, token: str, payload: dict | None = None):
    resp = requests.post(
        f'{GRAPH_ROOT}{path}',
        headers=_headers(token),
        json=payload or {},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json() if resp.content else {}


def graph_patch(path: str, token: str, payload: dict):
    resp = requests.patch(
        f'{GRAPH_ROOT}{path}',
        headers=_headers(token),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json() if resp.content else {}

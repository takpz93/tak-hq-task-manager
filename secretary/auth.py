from __future__ import annotations

import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def _secretary_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def credentials_path() -> Path:
    return Path(os.environ.get("GOOGLE_CREDENTIALS", _secretary_dir() / "credentials.json"))


def token_path() -> Path:
    return Path(os.environ.get("GOOGLE_TOKEN", _secretary_dir() / "token.json"))


def _load_from_streamlit_secrets() -> Credentials | None:
    """Streamlit Cloud 環境では st.secrets から認証情報を読む"""
    try:
        import streamlit as st
        secrets = st.secrets
        if "google_token" not in secrets:
            return None
        token_data = json.loads(secrets["google_token"])
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            return creds
    except Exception:
        pass
    return None


def get_credentials() -> Credentials:
    """OAuth2 トークンを取得。Streamlit Cloud では secrets から読む。"""
    # Streamlit Cloud 環境を優先
    creds = _load_from_streamlit_secrets()
    if creds:
        return creds

    # ローカル環境：ファイルから読む
    creds = None
    path = token_path()
    if path.is_file():
        creds = Credentials.from_authorized_user_file(str(path), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        path.write_text(creds.to_json(), encoding="utf-8")
        return creds

    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path()), SCOPES)
    creds = flow.run_local_server(port=0)
    path.write_text(creds.to_json(), encoding="utf-8")
    return creds

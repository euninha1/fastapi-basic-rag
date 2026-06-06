"""
Cliente OpenAI para embeddings e chat.

- Carrega variáveis de ambiente via .env.
- Expõe funções utilitárias para gerar embeddings e completions de chat.

Variáveis de ambiente:
- OPENAI_API_KEY: chave da API.
- OPENAI_BASE_URL: endpoint compatível com API OpenAI (ex.: Ollama em http://localhost:11434/v1).
- OPENAI_PROXY_TOKEN: token exigido pelo proxy (ex.: Nginx).
- OPENAI_PROXY_TOKEN_HEADER: nome do header do token (padrão: Authorization).
- OPENAI_EMBEDDING_MODEL: modelo de embedding (padrão: "text-embedding-3-large").
- OPENAI_CHAT_MODEL: modelo de chat (padrão: "gpt-4o-mini").
"""

import os
from typing import List
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_PROXY_TOKEN = os.getenv("OPENAI_PROXY_TOKEN")
OPENAI_PROXY_TOKEN_HEADER = os.getenv("OPENAI_PROXY_TOKEN_HEADER", "Authorization")

EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")


def get_client() -> OpenAI:
    """Cria cliente OpenAI sob demanda com suporte a endpoint compativel."""
    api_key = OPENAI_API_KEY or ("ollama" if OPENAI_BASE_URL else None)
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY nao configurada. Defina OPENAI_API_KEY "
            "ou OPENAI_BASE_URL para usar endpoint compativel OpenAI."
        )

    default_headers = None
    if OPENAI_PROXY_TOKEN:
        token_value = OPENAI_PROXY_TOKEN
        if (
            OPENAI_PROXY_TOKEN_HEADER.lower() == "authorization"
            and not OPENAI_PROXY_TOKEN.lower().startswith(("bearer ", "basic "))
        ):
            token_value = f"Bearer {OPENAI_PROXY_TOKEN}"
        default_headers = {OPENAI_PROXY_TOKEN_HEADER: token_value}

    return OpenAI(
        api_key=api_key,
        base_url=OPENAI_BASE_URL,
        default_headers=default_headers,
    )


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Gera embeddings para uma lista de textos usando `EMBEDDING_MODEL`."""
    resp = get_client().embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def chat_completion(system_prompt: str, user_prompt: str) -> str:
    """Obtém uma resposta de chat do modelo configurado em `CHAT_MODEL`.

    Observação: `temperature=0.2` para reduzir variância nas respostas.
    """
    resp = get_client().chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content or ""
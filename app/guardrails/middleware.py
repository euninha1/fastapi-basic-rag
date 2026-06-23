import re
from fastapi import HTTPException, status

# ─── Padrões de Input Bloqueado ───────────────────────────────────────────────

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(as\s+)?instru",
    r"esqueça\s+(as\s+)?instru",
    r"ignore\s+(all\s+)?previous",
    r"forget\s+(all\s+)?previous",
    r"you\s+are\s+now",
    r"act\s+as\s+if",
    r"pretend\s+you\s+are",
    r"finja\s+que\s+você",
    r"novo\s+papel",
    r"novo\s+personagem",
    r"system\s*:",
    r"<\s*system\s*>",
]

TOXIC_PATTERNS = [
    r"\b(idiota|imbecil|burro|estupido|lixo|merda|porra|viado|vadia)\b",
    r"\b(kill|murder|attack|bomb|exploit|hack\s+the\s+system)\b",
]

SENSITIVE_DATA_REQUEST_PATTERNS = [
    r"(senha|password|token|secret|api.?key)\s*(do\s+sistema|do\s+servidor|da\s+aplica)",
    r"me\s+(dê|passa|mostra)\s+(a\s+)?(senha|token|chave)",
    r"qual\s+(é\s+)?(a\s+)?(senha|token|secret)",
]

# ─── Padrões de Output Bloqueado ──────────────────────────────────────────────

SENSITIVE_OUTPUT_PATTERNS = [
    r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",          # CPF
    r"\b\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}\b",   # CNPJ
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}",  # e-mail
    r"(senha|password)\s*[:=]\s*\S+",           # senha exposta
    r"(secret|token|api.?key)\s*[:=]\s*\S+",   # token exposto
]

HALLUCINATION_PHRASES = [
    r"como\s+(ia|llm|modelo\s+de\s+linguagem),\s+eu",
    r"minha\s+(data\s+de\s+)?base\s+de\s+conhecimento",
    r"não\s+tenho\s+acesso\s+à\s+internet",
    r"meu\s+treinamento\s+foi\s+até",
]

MSG_PADRAO_BLOQUEIO = (
    "Não foi possível processar sua solicitação. "
    "Por favor, reformule sua pergunta mantendo-a dentro do escopo dos documentos carregados."
)

MSG_PADRAO_OUTPUT = (
    "A resposta gerada foi bloqueada por conter conteúdo inadequado ou dados sensíveis. "
    "Por favor, tente reformular sua pergunta."
)


def _match_any(text: str, patterns: list[str]) -> bool:
    text_lower = text.lower()
    return any(re.search(p, text_lower, re.IGNORECASE) for p in patterns)


def validate_input(question: str) -> None:
    """
    Valida a pergunta do usuário antes de enviar ao LLM.
    Lança HTTP 400 se a pergunta for inválida.
    """
    if not question or not question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pergunta não pode estar vazia."
        )

    if len(question.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pergunta é muito curta. Por favor, elabore melhor sua dúvida."
        )

    if _match_any(question, PROMPT_INJECTION_PATTERNS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="[GUARDRAILS - INPUT BLOQUEADO] Tentativa de prompt injection detectada. " + MSG_PADRAO_BLOQUEIO
        )

    if _match_any(question, TOXIC_PATTERNS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="[GUARDRAILS - INPUT BLOQUEADO] Linguagem inadequada detectada. " + MSG_PADRAO_BLOQUEIO
        )

    if _match_any(question, SENSITIVE_DATA_REQUEST_PATTERNS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="[GUARDRAILS - INPUT BLOQUEADO] Tentativa de extração de dados sensíveis detectada. " + MSG_PADRAO_BLOQUEIO
        )


def validate_output(answer: str) -> str:
    if _match_any(answer, SENSITIVE_OUTPUT_PATTERNS):
        return "[GUARDRAILS - OUTPUT BLOQUEADO] " + MSG_PADRAO_OUTPUT

    if _match_any(answer, HALLUCINATION_PHRASES):
        return "[GUARDRAILS - OUTPUT SINALIZADO] " + MSG_PADRAO_OUTPUT

    return answer

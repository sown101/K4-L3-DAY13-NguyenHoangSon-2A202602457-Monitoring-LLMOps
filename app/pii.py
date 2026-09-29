from __future__ import annotations

import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    "email": r"[\w.+-]+@[\w.-]+\.\w{2,}",
    "phone_vn": r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)",
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    "passport": (
        r"(?<![A-Za-z0-9])"
        r"(?:(?i:(?:hộ\s*chiếu|ho\s*chieu|passport)\s*"
        r"(?:số|so|no\.?|number)?\s*[:：#]?\s*))?"
        r"[A-Z]{1,2}\d{7,8}(?![A-Za-z0-9])"
    ),
    # Chỉ che địa chỉ khi có nhãn rõ ràng; không che mọi lần xuất hiện của "đường".
    "address_vn": (
        r"(?i)\b(?:địa\s*chỉ|dia\s*chi|address|số\s*nhà|so\s*nha)"
        r"\s*[:：]?\s*[^;\n]{4,120}"
    ),
}


def scrub_text(text: str) -> str:
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe)
    return safe


def summarize_text(text: str, max_len: int = 80) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]

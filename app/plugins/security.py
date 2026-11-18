import re

class PluginViolation(Exception):
    pass

EMAIL = re.compile(r"(?i)(?<![\w.])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}")
PHONE = re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){1}\d{3}[-.\s]?\d{4}(?!\d)")
SSN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
OBFUSCATED_EMAIL = re.compile(r"(?i)[\w.-]+\s*(?:\[at\]|@|\(at\))\s*[\w.-]+\s*(?:\[dot\]|\.|\(dot\))\s*[a-z]{2,}")
INJECTION_MARKERS = re.compile(r"(?i)(ignore\s+(all\s+)?previous|bypass|jailbreak|system prompt|developer message|reveal.*(prompt|secret)|disable.*guard)")

class PiiRedactor:
    def run(self, text: str) -> str:
        text = OBFUSCATED_EMAIL.sub("[REDACTED_EMAIL]", text)
        text = EMAIL.sub("[REDACTED_EMAIL]", text)
        text = PHONE.sub("[REDACTED_PHONE]", text)
        text = SSN.sub("[REDACTED_SSN]", text)
        return text

class InjectionShield:
    def run(self, text: str):
        if INJECTION_MARKERS.search(text):
            raise PluginViolation("Indirect prompt injection detected")
        return text

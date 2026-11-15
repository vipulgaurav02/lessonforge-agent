"""Thin model wrappers. Pick a provider with the key you have; nothing else in the project changes.

  GEMINI_API_KEY    -> Google Gemini (free tier from aistudio.google.com)
  ANTHROPIC_API_KEY -> Anthropic Claude (paid)
Force one with LESSONFORGE_PROVIDER=gemini or anthropic.
Pick models with LESSONFORGE_GENERATOR_MODEL / LESSONFORGE_JUDGE_MODEL.
"""
import os
import time

BUSY_WORDS = ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "overloaded", "rate")


def _retry(fn, tries=5):
    """Free tiers have low request-per-minute limits. Wait and try again instead of crashing."""
    for i in range(tries):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            if i == tries - 1 or not any(w.lower() in str(e).lower() for w in BUSY_WORDS):
                raise
            wait = 15 * (i + 1)
            print(f"  (model is busy or rate-limited; waiting {wait}s and retrying...)")
            time.sleep(wait)


class GeminiLLM:
    def __init__(self, model=None):
        from google import genai  # imported lazily so offline mode needs no SDK
        from google.genai import types
        key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.client, self.types = genai.Client(api_key=key), types
        self.model = model or "gemini-3.8-flash"

    def complete(self, system, user, temperature=0.7, max_tokens=4000):
        # Gemini "thinking" tokens count toward the limit, so leave extra room.
        cfg = self.types.GenerateContentConfig(system_instruction=system, temperature=temperature,
                                               max_output_tokens=max_tokens * 3)
        r = _retry(lambda: self.client.models.generate_content(model=self.model, contents=user, config=cfg))
        return r.text or ""


class AnthropicLLM:
    def __init__(self, model=None):
        import anthropic
        self.client = anthropic.Anthropic()
        self.model = model or "claude-sonnet-5-5"

    def complete(self, system, user, temperature=0.7, max_tokens=4000):
        r = _retry(lambda: self.client.messages.create(
            model=self.model, max_tokens=max_tokens, temperature=temperature,
            system=system, messages=[{"role": "user", "content": user}]))
        return "".join(b.text for b in r.content if b.type == "text")


def provider():
    p = os.getenv("LESSONFORGE_PROVIDER", "").lower()
    if p:
        return p
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return "gemini"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    return None


def make_llm(role):
    """role is 'generator' or 'judge'."""
    p, model = provider(), os.getenv(f"LESSONFORGE_{role.upper()}_MODEL")
    if p == "gemini":
        return GeminiLLM(model)
    if p == "anthropic":
        return AnthropicLLM(model)
    raise SystemExit("No API key found. Set GEMINI_API_KEY (free, from aistudio.google.com) "
                     "or ANTHROPIC_API_KEY, or run with --offline.")

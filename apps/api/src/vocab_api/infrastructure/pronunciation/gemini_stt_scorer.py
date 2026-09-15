"""Gemini-backed STT scorer: Gemini transcribes the clip, then word-level match.

Same degraded contract as ``CloudSttScorer`` (no phoneme scoring —
``scored_phonemes=False``): Gemini's multimodal ``generateContent`` endpoint
takes the raw audio as inline base64 data and a plain-transcript instruction,
so the free/Pro Google AI Studio API key works without any dedicated GPU box.
"""

import base64

import httpx

from vocab_api.application.errors import PronunciationUnavailable
from vocab_api.domain.pronunciation.assessment import PronunciationAssessment
from vocab_api.infrastructure.pronunciation.cloud_stt_scorer import (
    match_words,
    overall_score,
)

_TRANSCRIBE_PROMPT = (
    "Transcribe the spoken words in this audio clip exactly as heard. "
    "Reply with ONLY the plain transcript text — no punctuation commentary, "
    "no quotes, no preamble. If nothing is audible, reply with an empty string."
)


class GeminiSttScorer:
    """Scores by transcribing audio via the Gemini API, then matching words."""

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: float,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        )
        self._timeout = timeout
        self._client = client

    async def score(self, audio: bytes, target_text: str, accent: str) -> PronunciationAssessment:
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": _TRANSCRIBE_PROMPT},
                        {
                            "inline_data": {
                                "mime_type": "audio/webm",
                                "data": base64.b64encode(audio).decode("ascii"),
                            }
                        },
                    ]
                }
            ],
            "generationConfig": {"temperature": 0.0},
        }
        client = self._client or httpx.AsyncClient(timeout=self._timeout)
        try:
            response = await client.post(
                self._url,
                params={"key": self._api_key},
                json=payload,
            )
            response.raise_for_status()
            transcript = _extract_text(response.json())
        except (httpx.HTTPError, ValueError, KeyError, TypeError, IndexError):
            raise PronunciationUnavailable() from None
        finally:
            if self._client is None:
                await client.aclose()
        words = match_words(transcript, target_text)
        return PronunciationAssessment(
            overall=overall_score(words),
            words=words,
            transcript=transcript,
            scored_phonemes=False,
        )


def _extract_text(data: object) -> str:
    if not isinstance(data, dict):
        raise ValueError("unexpected Gemini response")
    candidates = data.get("candidates") or []
    if not candidates:
        return ""
    parts = candidates[0].get("content", {}).get("parts", [])
    return "".join(str(part.get("text", "")) for part in parts).strip()

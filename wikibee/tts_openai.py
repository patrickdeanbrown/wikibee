from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

# Allow tests to monkeypatch `OpenAI` at module level without requiring the
# real `openai` package to be installed at import time. If the import fails
# we'll set OpenAI to None and import inside the constructor.
OpenAI: Any = None
try:
    from openai import OpenAI as _OpenAI

    OpenAI = _OpenAI
except Exception:  # pragma: no cover - import-time fallback
    OpenAI = None


class TTSClientError(RuntimeError):
    pass


def _resolve_dest_path(dest_path: str, base_dir: str) -> Path:
    """Resolve ``dest_path`` against ``base_dir`` and guard against traversal."""

    base_path = Path(base_dir).expanduser().resolve()
    candidate = Path(dest_path)
    if not candidate.is_absolute():
        candidate = base_path / candidate
    candidate = candidate.expanduser().resolve()

    try:
        candidate.relative_to(base_path)
    except ValueError as exc:  # Python <3.9 lacks Path.is_relative_to
        raise TTSClientError(
            f"Destination path '{candidate}' escapes base directory '{base_path}'"
        ) from exc

    candidate.parent.mkdir(parents=True, exist_ok=True)
    return candidate


def _stream_to_file(
    client: Any,
    dest: Path,
    base_kwargs: dict[str, object],
    file_format: Optional[str],
) -> str:
    """Stream audio to ``dest`` optionally requesting a specific format."""

    attempts = [True] if file_format else []
    attempts.append(False)

    last_type_error: Optional[TypeError] = None
    for include_format in attempts:
        kwargs = base_kwargs.copy()
        if include_format and file_format:
            kwargs["format"] = file_format
        try:
            with client.audio.speech.with_streaming_response.create(
                **kwargs
            ) as response:
                response.stream_to_file(str(dest))
            return str(dest)
        except TypeError as exc:
            if include_format and "format" in str(exc):
                last_type_error = exc
                continue
            raise

    if last_type_error is not None:
        raise last_type_error
    return str(dest)


class TTSOpenAIClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8880/v1",
        api_key: str = "not-needed",
    ):
        # Store connection parameters and defer constructing the real
        # OpenAI client until synthesis time. This lets tests monkeypatch
        # `OpenAI` to simulate failures that occur during client creation.
        self._base_url = base_url
        self._api_key = api_key
        self.client: Any = None

    def synthesize_to_file(
        self,
        text: str,
        dest_path: str,
        base_dir: str = ".",
        model: str = "kokoro",
        voice: Optional[str] = None,
        file_format: str = "mp3",
        timeout: int = 60,
    ) -> str:
        """Synthesize `text` using the OpenAI-compatible
        `audio.speech.with_streaming_response.create` API.

        Streams the response to `dest_path` (relative to base_dir). Returns
        the saved file path.
        """
        try:
            # Lazily create the OpenAI client if needed.
            global OpenAI
            if self.client is None:
                if OpenAI is None:
                    try:
                        from openai import OpenAI as _OpenAI

                        OpenAI = _OpenAI
                    except Exception as e:  # pragma: no cover - tests monkeypatch
                        raise TTSClientError(
                            "OpenAI client is not available; install 'openai' or "
                            "monkeypatch OpenAI in tests"
                        ) from e
                try:
                    self.client = OpenAI(base_url=self._base_url, api_key=self._api_key)
                except Exception as e:
                    raise TTSClientError("Failed to initialize OpenAI client") from e

            dest = _resolve_dest_path(dest_path, base_dir)

            base_kwargs = {
                "model": model,
                "input": text,
                "timeout": timeout,
            }
            if voice is not None:
                base_kwargs["voice"] = voice

            streamed_path = _stream_to_file(
                self.client,
                dest,
                base_kwargs,
                file_format,
            )

            return streamed_path
        except TTSClientError:
            raise
        except Exception as e:
            raise TTSClientError("Audio synthesis failed") from e

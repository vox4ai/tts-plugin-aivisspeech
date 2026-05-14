from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, Optional

import aiohttp
from tts_plugin_bridge.protocol import TTSConnector, TTSRequest, TTSResponse


class AivisSpeechConnector(TTSConnector):
    """AivisSpeech Engine 向け TTS Connector (VOICEVOX 2-step protocol)."""

    ENGINE_NAME = "aivisspeech"
    SUPPORTED_PARAMS = [
        "style_id",
        "intonation_scale",
        "tempo_dynamics",
        "pre_phoneme_length",
        "post_phoneme_length",
        "output_stereo",
        "pitch_scale",
    ]

    def __init__(
        self,
        server_url: str = "http://localhost:10101",
        timeout: float = 30.0,
        default_style_id: Optional[int] = None,
    ):
        self.server_url = server_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.default_style_id = default_style_id
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def is_available(self) -> bool:
        try:
            session = await self._get_session()
            async with session.get(
                f"{self.server_url}/engine_manifest", timeout=2
            ) as resp:
                return resp.status == 200
        except Exception:
            return False

    async def list_speakers(self) -> list[dict[str, Any]]:
        try:
            session = await self._get_session()
            async with session.get(f"{self.server_url}/speakers") as resp:
                if resp.status != 200:
                    raise RuntimeError(
                        f"Failed to fetch speakers: HTTP {resp.status}"
                    )
                return await resp.json()
        except (aiohttp.ClientError, RuntimeError) as e:
            raise type(e)(f"Cannot list speakers: {e}") from e

    def _resolve_style_id(self, req: TTSRequest) -> Optional[int]:
        style_id = req.extra.get("style_id")
        if style_id is not None:
            return int(style_id)
        return self.default_style_id

    async def synthesize(self, req: TTSRequest) -> TTSResponse:
        try:
            style_id = self._resolve_style_id(req)
            if style_id is None:
                return TTSResponse.fail(
                    "style_id is required. Pass extra={'style_id': <int>} "
                    "or set default_style_id in the constructor."
                )

            session = await self._get_session()

            async with session.post(
                f"{self.server_url}/audio_query",
                params={"speaker": style_id, "text": req.text},
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    return TTSResponse.fail(
                        f"audio_query failed: HTTP {resp.status}: {error_text}"
                    )
                audio_query = await resp.json()

            clamped_speed = max(0.5, min(2.0, req.speed))
            audio_query["speedScale"] = clamped_speed

            if req.volume is not None:
                clamped_volume = max(0.0, min(2.0, req.volume))
                audio_query["volumeScale"] = clamped_volume

            if "intonation_scale" in req.extra:
                val = max(0.0, min(2.0, float(req.extra["intonation_scale"])))
                audio_query["intonationScale"] = val

            if "tempo_dynamics" in req.extra:
                val = max(0.0, min(2.0, float(req.extra["tempo_dynamics"])))
                audio_query["tempoDynamicsScale"] = val

            if "pre_phoneme_length" in req.extra:
                audio_query["prePhonemeLength"] = float(
                    req.extra["pre_phoneme_length"]
                )
            if "post_phoneme_length" in req.extra:
                audio_query["postPhonemeLength"] = float(
                    req.extra["post_phoneme_length"]
                )

            if "output_stereo" in req.extra:
                audio_query["outputStereo"] = bool(req.extra["output_stereo"])

            if "pitch_scale" in req.extra:
                val = max(-0.15, min(0.15, float(req.extra["pitch_scale"])))
                audio_query["pitchScale"] = val

            async with session.post(
                f"{self.server_url}/synthesis",
                params={"speaker": style_id},
                json=audio_query,
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    return TTSResponse.fail(
                        f"synthesis failed: HTTP {resp.status}: {error_text}"
                    )
                audio_data = await resp.read()
                return TTSResponse.ok(
                    audio_data=audio_data,
                    metadata={
                        "speed_scale": clamped_speed,
                        "volume_scale": clamped_volume
                        if req.volume is not None
                        else None,
                        "style_id": style_id,
                    },
                )

        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            return TTSResponse.fail(f"Request error: {e}")
        except Exception as e:
            return TTSResponse.fail(
                f"Unexpected error: {type(e).__name__}: {e}"
            )

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def synthesize_stream(self, req: TTSRequest) -> AsyncIterator[bytes]:
        result = await self.synthesize(req)
        if result.success and result.audio_data:
            yield result.audio_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

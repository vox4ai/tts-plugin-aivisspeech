import pytest
from tts_plugin_bridge.protocol import TTSRequest

from tts_plugin_aivisspeech.connector import AivisSpeechConnector


@pytest.mark.asyncio
async def test_synthesize_integration():
    """Verify synthesis with a running AivisSpeech Engine (port 10101)."""
    connector = AivisSpeechConnector(server_url="http://localhost:10101")

    if not await connector.is_available():
        pytest.skip(
            "AivisSpeech Engine not running at http://localhost:10101. "
            "Skipping integration test."
        )

    import io

    import soundfile as sf

    extra = {"style_id": 888753760}
    req = TTSRequest(text="これは結合テストです", speed=1.0, extra=extra)
    resp = await connector.synthesize(req)

    assert resp.success is True
    assert resp.audio_data is not None
    assert len(resp.audio_data) > 0

    with io.BytesIO(resp.audio_data) as buf:
        data, samplerate = sf.read(buf)
        assert samplerate == 44100
        assert len(data) > 0

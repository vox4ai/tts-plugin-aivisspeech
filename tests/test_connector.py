import pytest
from aioresponses import aioresponses
from tts_plugin_bridge.protocol import TTSRequest

from tts_plugin_aivisspeech.connector import AivisSpeechConnector

MOCK_SAMPLE_AUDIO_QUERY = {
    "accent_phrases": [],
    "speedScale": 1.0,
    "intonationScale": 1.0,
    "tempoDynamicsScale": 1.0,
    "pitchScale": 0.0,
    "volumeScale": 1.0,
    "prePhonemeLength": 0.1,
    "postPhonemeLength": 0.1,
    "pauseLength": None,
    "pauseLengthScale": 1,
    "outputSamplingRate": 44100,
    "outputStereo": False,
    "kana": "hello",
}


@pytest.mark.asyncio
async def test_connector_is_available():
    connector = AivisSpeechConnector(server_url="http://localhost:10101")
    with aioresponses() as m:
        m.get("http://localhost:10101/engine_manifest", status=200)
        assert await connector.is_available() is True
    await connector.close()


@pytest.mark.asyncio
async def test_connector_is_available_failure():
    connector = AivisSpeechConnector(server_url="http://localhost:10101")
    with aioresponses() as m:
        m.get("http://localhost:10101/engine_manifest", exception=Exception)
        assert await connector.is_available() is False
    await connector.close()


@pytest.mark.asyncio
async def test_connector_synthesize_success():
    connector = AivisSpeechConnector(
        server_url="http://localhost:10101", default_style_id=888753760
    )
    req = TTSRequest(text="hello", speed=1.0)

    with aioresponses() as m:
        m.post(
            "http://localhost:10101/audio_query?speaker=888753760&text=hello",
            status=200,
            payload=MOCK_SAMPLE_AUDIO_QUERY,
        )
        m.post(
            "http://localhost:10101/synthesis?speaker=888753760",
            status=200,
            body=b"RIFF audio data",
        )

        res = await connector.synthesize(req)
        assert res.success is True
        assert res.audio_data == b"RIFF audio data"
    await connector.close()


@pytest.mark.asyncio
async def test_connector_synthesize_with_style_id_in_extra():
    connector = AivisSpeechConnector(server_url="http://localhost:10101")
    req = TTSRequest(text="hello", speed=1.0, extra={"style_id": 123456789})

    with aioresponses() as m:
        m.post(
            "http://localhost:10101/audio_query?speaker=123456789&text=hello",
            status=200,
            payload=MOCK_SAMPLE_AUDIO_QUERY,
        )
        m.post(
            "http://localhost:10101/synthesis?speaker=123456789",
            status=200,
            body=b"RIFF audio data",
        )

        res = await connector.synthesize(req)
        assert res.success is True
    await connector.close()


@pytest.mark.asyncio
async def test_connector_synthesize_missing_style_id():
    connector = AivisSpeechConnector(server_url="http://localhost:10101")
    req = TTSRequest(text="hello")

    res = await connector.synthesize(req)

    assert res.success is False
    assert "style_id" in res.error
    await connector.close()


@pytest.mark.asyncio
async def test_connector_synthesize_audio_query_fails():
    connector = AivisSpeechConnector(
        server_url="http://localhost:10101", default_style_id=1
    )
    req = TTSRequest(text="hello")

    with aioresponses() as m:
        m.post(
            "http://localhost:10101/audio_query?speaker=1&text=hello",
            status=500,
            body="Internal Error",
        )

        res = await connector.synthesize(req)
        assert res.success is False
        assert "audio_query" in res.error
    await connector.close()


@pytest.mark.asyncio
async def test_connector_synthesize_synthesis_fails():
    connector = AivisSpeechConnector(
        server_url="http://localhost:10101", default_style_id=1
    )
    req = TTSRequest(text="hello")

    with aioresponses() as m:
        m.post(
            "http://localhost:10101/audio_query?speaker=1&text=hello",
            status=200,
            payload=MOCK_SAMPLE_AUDIO_QUERY,
        )
        m.post(
            "http://localhost:10101/synthesis?speaker=1",
            status=500,
            body="Model not found",
        )

        res = await connector.synthesize(req)
        assert res.success is False
        assert "synthesis" in res.error
    await connector.close()


@pytest.mark.asyncio
async def test_connector_extra_params():
    connector = AivisSpeechConnector(
        server_url="http://localhost:10101", default_style_id=1
    )
    req = TTSRequest(
        text="hello",
        speed=1.5,
        volume=0.8,
        extra={
            "intonation_scale": 1.5,
            "tempo_dynamics": 0.5,
            "pre_phoneme_length": 0.2,
            "post_phoneme_length": 0.3,
            "output_stereo": True,
            "pitch_scale": 0.05,
        },
    )

    with aioresponses() as m:
        m.post(
            "http://localhost:10101/audio_query?speaker=1&text=hello",
            status=200,
            payload=MOCK_SAMPLE_AUDIO_QUERY.copy(),
        )
        m.post(
            "http://localhost:10101/synthesis?speaker=1",
            status=200,
            body=b"audio",
        )

        res = await connector.synthesize(req)
        assert res.success is True

        synth_calls = [
            v for k, v in m.requests.items()
            if k[0] == "POST" and "/synthesis" in str(k[1])
        ]
        body = synth_calls[0][0].kwargs["json"]
        assert body["speedScale"] == 1.5
        assert body["volumeScale"] == 0.8
        assert body["intonationScale"] == 1.5
        assert body["tempoDynamicsScale"] == 0.5
        assert body["prePhonemeLength"] == 0.2
        assert body["postPhonemeLength"] == 0.3
        assert body["outputStereo"] is True
        assert body["pitchScale"] == 0.05
        assert body["kana"] == "hello"
    await connector.close()


@pytest.mark.asyncio
async def test_connector_speed_clamping():
    connector = AivisSpeechConnector(
        server_url="http://localhost:10101", default_style_id=1
    )
    req = TTSRequest(text="hello", speed=3.0)

    with aioresponses() as m:
        m.post(
            "http://localhost:10101/audio_query?speaker=1&text=hello",
            status=200,
            payload=MOCK_SAMPLE_AUDIO_QUERY.copy(),
        )
        m.post(
            "http://localhost:10101/synthesis?speaker=1",
            status=200,
            body=b"audio",
        )

        res = await connector.synthesize(req)
        assert res.success is True

        synth_calls = [
            v for k, v in m.requests.items()
            if k[0] == "POST" and "/synthesis" in str(k[1])
        ]
        body = synth_calls[0][0].kwargs["json"]
        assert body["speedScale"] == 2.0
    await connector.close()


@pytest.mark.asyncio
async def test_connector_list_speakers():
    connector = AivisSpeechConnector(server_url="http://localhost:10101")
    mock_speakers = [
        {
            "name": "Test Speaker",
            "speaker_uuid": "abc-def",
            "styles": [{"id": 888753760, "name": "normal"}],
        }
    ]

    with aioresponses() as m:
        m.get("http://localhost:10101/speakers", status=200, payload=mock_speakers)
        speakers = await connector.list_speakers()
        assert speakers == mock_speakers
    await connector.close()


@pytest.mark.asyncio
async def test_connector_context_manager():
    async with AivisSpeechConnector() as connector:
        assert connector.ENGINE_NAME == "aivisspeech"

    if connector._session:
        assert connector._session.closed

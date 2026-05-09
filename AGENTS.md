# tts-plugin-aivisspeech

**Plugin for AivisSpeech Engine (VOICEVOX-compatible HTTP API)**

## KEY FILES
| File | Role |
|------|------|
| `tts_plugin_aivisspeech/connector.py` | AivisSpeechConnector implementation |

## ENTRY POINT
```python
# pyproject.toml
[project.entry-points."tts_bridge.connectors"]
aivisspeech = "tts_plugin_aivisspeech.connector:AivisSpeechConnector"
```

## USAGE
```bash
tts-plugin-bridge synthesize "こんにちは" -e aivisspeech --server-url http://localhost:10101
```

## IMPORTANT
- `style_id` is REQUIRED via `extra["style_id"]` (AivisSpeech uses dynamic 32-bit signed int style IDs)
- 2-step synthesis (audio_query + synthesis) handled internally
- Returns WAV bytes via `audio_data`
- First synthesis triggers model loading → may take time on first call

## SUPPORTED PARAMS
`style_id`, `intonation_scale`, `tempo_dynamics`, `pre_phoneme_length`, `post_phoneme_length`, `output_stereo`, `pitch_scale`

## CONVENTIONS
- Depends on: `tts-plugin-bridge` (core)
- Uses `aiohttp` for async HTTP
- Inherits `TTSConnector` ABC
- Python >=3.10
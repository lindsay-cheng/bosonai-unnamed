## Fuzzy Logic — We Bare Bears Council Edition

Fuzzy Logic brings the iconic bear trio to help with life's everyday dilemmas. Ask Grizzly, Panda, and Ice Bear any question from "Should I text my ex?" to "Is cereal a soup?"—and hear them debate in their iconic voices using BosonAI's voice cloning technology. It's a nostalgic, silly throwback that turns the We Bare Bears trio into your personal advisory council.

### Features

- **Voice Input**: Speak your questions using Gemini ASR
- **Three Bear Personalities**: Get opinions from Grizzly, Panda, and Ice Bear
- **Voice Responses**: Hear each bear speak using BosonAI TTS with voice cloning
- **Follow-up Questions**: Continue the conversation with contextual responses
- **Character-Accurate**: Each bear maintains their unique personality

### Architecture

**Full Audio Pipeline:**
1. User records audio → Gemini ASR transcribes to text
2. Text → Gemini LLM generates each bear's opinion (with personality)
3. Opinions → BosonAI TTS synthesizes audio for each bear
4. Frontend plays audio responses sequentially

**Stack:**
- Frontend: Next.js 15 + TypeScript + Tailwind CSS
- Backend: Flask + Python
- Speech-to-Text: Google Gemini Multimodal
- Text Generation: Google Gemini 2.5
- Text-to-Speech: BosonAI Higgs Audio Generation

### Environment Setup

Backend requires:
- `BOSON_API_KEY` (BosonAI for TTS)
- `GOOGLE_API_KEY` (Gemini for ASR + LLM)

Frontend requires:
- `NEXT_PUBLIC_API_URL` (Backend URL, defaults to http://localhost:8080)

---

## BosonAI Hackathon API — Agent Readme
 
### Overview

- **Protocol**: OpenAI-compatible REST API under a single base URL.
- **Base URL**: `https://hackathon.boson.ai/v1`
- **Auth**: `Authorization: Bearer $BOSON_API_KEY`
- **Models**
  - **Text/chat**: `Qwen3-32B-thinking-Hackathon`, `Qwen3-32B-non-thinking-Hackathon`, `Qwen3-14B-Hackathon`, `Qwen3-Omni-30B-A3B-Thinking-Hackathon`
  - **Audio understanding**: `higgs-audio-understanding-Hackathon`
  - **Audio generation (TTS & cloning)**: `higgs-audio-generation-Hackathon`
- **Voices (simple TTS)**: `belinda`, `broom_salesman`, `chadwick`, `en_man`, `en_woman`, `mabel`, `vex`, `zh_man_sichuan`

### Setup

- **Export API key**
```bash
export BOSON_API_KEY=YOUR_KEY
```

- **Python client**
```python
import openai, os
client = openai.Client(
  api_key=os.getenv("BOSON_API_KEY"),
  base_url="https://hackathon.boson.ai/v1"
)
```

### Text Chat Completions

- **Endpoint**: `POST /chat/completions`
- **Use**: General LLM tasks via Qwen3.* models
```bash
curl -X POST "https://hackathon.boson.ai/v1/chat/completions" \
  -H "Content-Type: application/json" -H "Authorization: Bearer $BOSON_API_KEY" \
  -d '{
    "model": "Qwen3-32B-thinking-Hackathon",
    "messages": [
      {"role":"system","content":"You are a helpful assistant."},
      {"role":"user","content":"Hello, how are you?"}
    ],
    "max_tokens": 128,
    "temperature": 0.7
  }'
```

### Audio Understanding (Transcription & Audio Chat)

- **Endpoint**: `POST /chat/completions` with `input_audio`, model `higgs-audio-understanding-Hackathon`
- **Audio**: base64-encoded; include `format` (e.g., `wav`, `mp3`).
```bash
AUDIO_BASE64=$(base64 -i /path/to/audio.wav)
curl -X POST "https://hackathon.boson.ai/v1/chat/completions" \
  -H "Content-Type: application/json" -H "Authorization: Bearer $BOSON_API_KEY" \
  -d '{
    "model": "higgs-audio-understanding-Hackathon",
    "messages": [
      {"role":"system","content":"Transcribe the audio."},
      {"role":"user","content":[
        {"type":"input_audio","input_audio":{"data":"'$AUDIO_BASE64'","format":"wav"}}
      ]}
    ],
    "max_completion_tokens": 256,
    "temperature": 0.0
  }'
```

```python
import base64, openai, os
client = openai.Client(api_key=os.getenv("BOSON_API_KEY"), base_url="https://hackathon.boson.ai/v1")
b64 = lambda p: base64.b64encode(open(p,"rb").read()).decode()
audio_path = "/path/to/audio.wav"
resp = client.chat.completions.create(
  model="higgs-audio-understanding-Hackathon",
  messages=[
    {"role":"system","content":"Transcribe this audio."},
    {"role":"user","content":[{"type":"input_audio","input_audio":{"data": b64(audio_path), "format":"wav"}}]},
  ],
  max_completion_tokens=256, temperature=0.0
)
print(resp.choices[0].message.content)
```

### Audio Generation (TTS)

- **Approaches**
  - Simple TTS via `POST /audio/speech` → returns PCM bytes
  - Controlled generation / cloning via `POST /chat/completions` with `modalities=["text","audio"]`

```bash
curl -X POST "https://hackathon.boson.ai/v1/audio/speech" \
  -H "Content-Type: application/json" -H "Authorization: Bearer $BOSON_API_KEY" \
  -d '{
    "model": "higgs-audio-generation-Hackathon",
    "voice": "belinda",
    "input": "Today is a wonderful day to build something people love!",
    "response_format": "pcm"
  }' \
  --output speech.pcm && ffplay -f s16le -ar 24000 speech.pcm
```

```python
import openai, os, wave
client = openai.Client(api_key=os.getenv("BOSON_API_KEY"), base_url="https://hackathon.boson.ai/v1")
res = client.audio.speech.create(
  model="higgs-audio-generation-Hackathon",
  voice="belinda",
  input="Hello, this is a test of the audio generation system.",
  response_format="pcm"
)
with wave.open("tts.wav","wb") as wav:
  wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(24000)
  wav.writeframes(res.content)
```

### Voice Cloning (In-Context)

- **Pattern**: reference transcript (user) → reference audio (assistant `input_audio`) → new user content
- **Modalities**: `modalities=["text","audio"]`
```python
from openai import OpenAI
import base64, os
client = OpenAI(api_key=os.getenv("BOSON_API_KEY"), base_url="https://hackathon.boson.ai/v1")
b64 = lambda p: base64.b64encode(open(p,"rb").read()).decode()
reference_path = "./ref-audio/hogwarts_wand_seller_v2.wav"
reference_transcript = "I would imagine so. A wand with a dragon heartstring core ..."
resp = client.chat.completions.create(
  model="higgs-audio-generation-Hackathon",
  messages=[
    {"role":"user","content": reference_transcript},
    {"role":"assistant","content":[{"type":"input_audio","input_audio":{"data": b64(reference_path), "format":"wav"}}]},
    {"role":"user","content":"Welcome to Boson AI's voice generation system."}
  ],
  modalities=["text","audio"],
  max_completion_tokens=4096,
  temperature=1.0, top_p=0.95, stream=False,
  stop=["<|eot_id|>","<|end_of_text|>","<|audio_eos|>"],
  extra_body={"top_k":50}
)
open("output.wav","wb").write(base64.b64decode(resp.choices[0].message.audio.data))
```

### Streaming TTS

- **Request**: `stream=True` on `chat.completions.create`, `modalities=["text","audio"]`, `audio={"format":"pcm16"}`
- **Chunks**: base64 PCM16 @ 24kHz in `choices[0].delta.audio.data`

```python
import base64, os, subprocess, openai
client = openai.Client(api_key=os.getenv("BOSON_API_KEY"), base_url="https://hackathon.boson.ai/v1")
proc = subprocess.Popen(["ffplay","-f","s16le","-ar","24000","-i","-","-nodisp","-autoexit","-loglevel","error"], stdin=subprocess.PIPE)
stream = client.chat.completions.create(
  model="higgs-audio-generation-Hackathon",
  messages=[{"role":"system","content":"Convert the following text from the user into speech."},
            {"role":"user","content":"Hello from Boson AI! Live streaming test."}],
  modalities=["text","audio"], audio={"format":"pcm16"}, stream=True, max_completion_tokens=300
)
for chunk in stream:
  delta = getattr(chunk.choices[0], "delta", None)
  audio = getattr(delta, "audio", None)
  if audio: proc.stdin.write(base64.b64decode(audio["data"]))
proc.stdin.close(); proc.wait()
```

```python
import base64, openai, os, wave
client = openai.Client(api_key=os.getenv("BOSON_API_KEY"), base_url="https://hackathon.boson.ai/v1")
stream = client.chat.completions.create(
  model="higgs-audio-generation-Hackathon",
  messages=[{"role":"system","content":"Convert the following text from the user into speech."},
            {"role":"user","content":"Hello from Boson AI! Streaming to WAV test."}],
  modalities=["text","audio"], audio={"format":"pcm16"}, stream=True, max_completion_tokens=300
)
wf = wave.open("streamed_tts.wav","wb"); wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
for chunk in stream:
  delta = getattr(chunk.choices[0],"delta",None); audio = getattr(delta,"audio",None)
  if audio: wf.writeframes(base64.b64decode(audio["data"]))
wf.close()
```

### Qwen3-Omni Multimodal (image + audio + text → text)

- **Model**: `Qwen3-Omni-30B-A3B-Thinking-Hackathon`
- **Content**: OpenAI-style multimodal entries `image_url` and `audio_url`
```bash
curl -X POST "https://hackathon.boson.ai/v1/chat/completions" \
  -H "Content-Type: application/json" -H "Authorization: Bearer $BOSON_API_KEY" \
  -d '{
    "model":"Qwen3-Omni-30B-A3B-Thinking-Hackathon",
    "messages":[
      {"role":"system","content":"You are a helpful assistant."},
      {"role":"user","content":[
        {"type":"image_url","image_url":{"url":"https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3-Omni/demo/cars.jpg"}},
        {"type":"audio_url","audio_url":{"url":"https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3-Omni/demo/cough.wav"}},
        {"type":"text","text":"Describe what you see and what you hear in one sentence."}
      ]}
    ],
    "max_tokens":256,"temperature":0.2
  }'
```

### Practical Notes

- **PCM format/sampling**: PCM16, mono, 24kHz for generation and streaming
- **Ref audio alignment**: Match reference transcript to reference audio content for cloning
- **Control levers**: `temperature`, `top_p`, `top_k`, `max_completion_tokens`, `stop`
- **Scene control**: Use system prompt or scene tags (e.g., `<|scene_desc_start|> ... <|scene_desc_end|>`) to shape delivery
- **Multimodal**: Always include explicit textual instructions alongside media inputs

### Sources

- Repo: [boson-ai/hackathon-msac-public](https://github.com/boson-ai/hackathon-msac-public)
- API doc: [api_doc.md](https://github.com/boson-ai/hackathon-msac-public/blob/main/api_doc.md)
- Cloning example: [cloning_example.py](https://github.com/boson-ai/hackathon-msac-public/blob/main/cloning_example.py)
- Streaming — live playback: [streaming_example_live_playback.py](https://github.com/boson-ai/hackathon-msac-public/blob/main/streaming_examples/streaming_example_live_playback.py)
- Streaming — save to file: [streaming_example_save_to_file.py](https://github.com/boson-ai/hackathon-msac-public/blob/main/streaming_examples/streaming_example_save_to_file.py)



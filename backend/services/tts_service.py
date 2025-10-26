from openai import OpenAI
import base64
import os
import io
import wave


class TTSService:
    """handles text-to-speech using BosonAI"""
    
    def __init__(self, api_key: str = None):
        """initialize BosonAI client
        
        Args:
            api_key: BosonAI API key (defaults to BOSON_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("BOSON_API_KEY")
        if not self.api_key:
            raise ValueError("BosonAI API key is required for TTS")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://hackathon.boson.ai/v1"
        )
        
        # system prompt for TTS with courtroom scene
        self.system_prompt = (
            "You are an AI assistant designed to convert text into speech.\n"
            "If the user's message includes a [SPEAKER*] tag, do not read out the tag and generate speech for the following text, using the specified voice.\n"
            "If no speaker tag is present, select a suitable voice on your own.\n\n"
            "<|scene_desc_start|>\nAudio is recorded in a dramatic courtroom setting with slight reverb.\n<|scene_desc_end|>"
        )
    
    def _b64_encode(self, audio_path: str) -> str:
        """base64 encode audio file"""
        with open(audio_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def synthesize_speech(self, speaker_tag: str, ref_audio_path: str, 
                         ref_transcript: str, text: str,
                         conversation_history: list = None) -> bytes:
        """generate speech from text using voice cloning
        
        Args:
            speaker_tag: speaker identifier like "[SPEAKER1]"
            ref_audio_path: path to reference audio file for voice cloning
            ref_transcript: transcript of reference audio with speaker tag
            text: text to convert to speech
            conversation_history: previous messages for context (optional)
        
        Returns:
            audio data as bytes (WAV format)
        """
        # If reference audio is missing, fall back to simple TTS
        if not ref_audio_path or not os.path.exists(ref_audio_path):
            return self._simple_tts(text)

        try:
            # encode reference audio
            reference_audio_b64 = self._b64_encode(ref_audio_path)

            # build messages array
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": ref_transcript},
                {
                    "role": "assistant",
                    "content": [{
                        "type": "input_audio",
                        "input_audio": {"data": reference_audio_b64, "format": "wav"}
                    }],
                },
            ]

            # add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # add current text request
            messages.append({"role": "user", "content": f"{speaker_tag} {text}"})

            # call BosonAI API for cloning
            resp = self.client.chat.completions.create(
                model="higgs-audio-generation-Hackathon",
                messages=messages,
                modalities=["text", "audio"],
                max_completion_tokens=4096,
                temperature=1.0,
                top_p=0.95,
                stream=False,
                stop=["<|eot_id|>", "<|end_of_text|>", "<|audio_eos|>"],
                extra_body={"top_k": 50},
            )

            # extract and decode audio
            audio_b64 = resp.choices[0].message.audio.data
            return base64.b64decode(audio_b64)

        except Exception:
            # graceful fallback to simple TTS if cloning fails
            return self._simple_tts(text)

    def _simple_tts(self, text: str) -> bytes:
        """Simple TTS fallback (no cloning). Returns WAV bytes."""
        # Request PCM16 stream and wrap into WAV container in-memory
        res = self.client.audio.speech.create(
            model="higgs-audio-generation-Hackathon",
            voice="en_woman",
            input=text,
            response_format="pcm",
        )

        pcm_bytes = res.content
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit PCM
            wf.setframerate(24000)
            wf.writeframes(pcm_bytes)
        return wav_buffer.getvalue()


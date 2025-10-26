from openai import OpenAI
import google.generativeai as genai
import os


class WhisperService:
    """handles audio transcription using OpenAI Whisper API"""
    
    def __init__(self, api_key: str = None):
        """initialize Whisper client
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required for Whisper ASR")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def transcribe_audio(self, audio_file) -> dict:
        """transcribe audio file to text
        
        Args:
            audio_file: file object or path to audio file
                       supports mp3, wav, m4a, webm formats
        
        Returns:
            dict with 'text' and optional 'language' keys
        
        Raises:
            Exception: if transcription fails
        """
        try:
            if isinstance(audio_file, str):
                with open(audio_file, "rb") as f:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=f,
                        response_format="text"
                    )
            else:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            return {
                "text": transcript.strip() if isinstance(transcript, str) else transcript.text.strip(),
                "language": "en"
            }
        
        except Exception as e:
            raise Exception(f"Whisper transcription failed: {str(e)}")


class GeminiASRService:
    """handles audio transcription using Google Gemini multimodal API"""
    
    def __init__(self, api_key: str = None):
        """initialize Gemini client for audio transcription
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required for Gemini ASR")
        
        genai.configure(api_key=self.api_key)
    
    def transcribe_audio(self, audio_file) -> dict:
        """transcribe audio file to text using Gemini
        
        Args:
            audio_file: file object or path to audio file
                       supports various audio formats
        
        Returns:
            dict with 'text' and optional 'language' keys
        
        Raises:
            Exception: if transcription fails
        """
        try:
            if isinstance(audio_file, str):
                with open(audio_file, "rb") as f:
                    audio_data = f.read()
            else:
                audio_data = audio_file.read()
            
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            audio_part = {
                "mime_type": "audio/webm",
                "data": audio_data
            }
            
            prompt = "Please transcribe this audio recording. Only provide the transcription text, nothing else."
            
            response = model.generate_content([prompt, audio_part])
            
            return {
                "text": response.text.strip(),
                "language": "en"
            }
        
        except Exception as e:
            raise Exception(f"Gemini transcription failed: {str(e)}")


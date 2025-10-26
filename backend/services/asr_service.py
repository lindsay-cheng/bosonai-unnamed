from openai import OpenAI
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
            # if audio_file is a path string, open it
            if isinstance(audio_file, str):
                with open(audio_file, "rb") as f:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=f,
                        response_format="text"
                    )
            else:
                # assume it's already a file object
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            return {
                "text": transcript.strip() if isinstance(transcript, str) else transcript.text.strip(),
                "language": "en"  # whisper auto-detects but we can assume english
            }
        
        except Exception as e:
            raise Exception(f"Whisper transcription failed: {str(e)}")


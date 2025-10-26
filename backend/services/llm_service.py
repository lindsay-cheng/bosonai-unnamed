import google.generativeai as genai
import os
from typing import List, Dict, Optional


class LLMService:
    """handles text generation using Google Gemini API"""
    
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        """initialize Gemini client
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model: Gemini model to use (default: gemini-2.5-flash)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required for Gemini LLM")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model
    
    def generate_opinion(self, personality_prompt: str, question: str, 
                        conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """generate personality-appropriate opinion using Gemini
        
        Args:
            personality_prompt: system prompt defining the personality
            question: user's question or follow-up
            conversation_history: optional list of previous messages in format [{"role": "user", "content": "..."}, ...]
        
        Returns:
            generated text response (30-60 words)
        """
        try:
            model = genai.GenerativeModel(self.model_name)
            
            context = ""
            if conversation_history and len(conversation_history) > 1:
                context = "\n\nPrevious conversation:\n"
                for msg in conversation_history[:-1]:
                    context += f"{msg['role'].upper()}: {msg['content']}\n"
                context += "\n"
            
            user_message = f"{personality_prompt}\n{context}Question: {question}\n\nGive your opinion in 30-60 words. Stay in character."
            
            response = model.generate_content(user_message)
            return response.text.strip()
        
        except Exception as e:
            raise Exception(f"Gemini text generation failed: {str(e)}")


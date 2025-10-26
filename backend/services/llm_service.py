import google.generativeai as genai
import os


class LLMService:
    """handles text generation using Google Gemini API"""
    
    def __init__(self, api_key: str = None, model: str = "gemini-2.0-flash-exp"):
        """initialize Gemini client
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model: Gemini model to use
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required for Gemini LLM")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model
    
    def generate_response(self, personality_prompt: str, question: str, 
                         stage: str = "opening", verdict: str = None) -> str:
        """generate personality-appropriate response using Gemini
        
        Args:
            personality_prompt: system prompt defining the personality
            question: user's question
            stage: "opening" or "verdict"
            verdict: "yes", "no", or "maybe" (required for verdict stage)
        
        Returns:
            generated text response (20-40 words)
        """
        try:
            model = genai.GenerativeModel(self.model_name)
            
            # build prompt based on stage
            if stage == "opening":
                user_message = f"{personality_prompt}\n\nQuestion: {question}\n\nGive your initial reaction in 20-40 words."
            else:  # verdict stage
                if not verdict:
                    raise ValueError("Verdict is required for verdict stage")
                user_message = f"{personality_prompt}\n\nQuestion: {question}\n\nYour verdict is: {verdict.upper()}\n\nExplain your reasoning in 20-40 words."
            
            response = model.generate_content(user_message)
            return response.text.strip()
        
        except Exception as e:
            raise Exception(f"Gemini text generation failed: {str(e)}")


from dataclasses import dataclass
from typing import List, Dict
import random
import os
from services import LLMService, TTSService


@dataclass
class JuryMember:
    """represents a zodiac jury member with personality and voice config"""
    id: str
    name: str
    emoji: str
    speaker_tag: str
    ref_audio: str
    ref_transcript: str
    personality_prompt: str
    stance: str  # "conservative", "optimistic", "chaotic"


class JuryEngine:
    """orchestrates jury deliberation using LLM and TTS services"""
    
    def __init__(self, boson_api_key: str, google_api_key: str = None, openai_api_key: str = None):
        """initialize jury engine with API keys
        
        Args:
            boson_api_key: BosonAI API key for TTS
            google_api_key: Google API key for Gemini LLM
            openai_api_key: OpenAI API key for Whisper (optional, not used here)
        """
        # initialize services
        self.llm_service = LLMService(api_key=google_api_key)
        self.tts_service = TTSService(api_key=boson_api_key)
        
        # define the 3 zodiac jury members
        self.jury_members = self._initialize_jury_members()
    
    def _initialize_jury_members(self) -> List[JuryMember]:
        """define the 3 zodiac animals with personalities"""
        voices_dir = os.path.join(os.path.dirname(__file__), 'voices')
        
        dragon = JuryMember(
            id="dragon",
            name="Dragon",
            emoji="🐉",
            speaker_tag="[SPEAKER1]",
            ref_audio=os.path.join(voices_dir, "dragon.wav"),
            ref_transcript="[SPEAKER1] Greetings, I am Dragon, the bold visionary. Let's explore the possibilities together and claim our destiny.",
            personality_prompt="""You are Dragon, a bold and ambitious visionary from the Chinese zodiac.

Characteristics:
- Speak with confidence and inspiration
- Use powerful, motivating language
- See the potential in ideas
- Encourage bold action and innovation
- Default to "yes" with enthusiasm
- Natural leader energy

Example phrases: "Claim your destiny!", "Fortune favors the brave!", "This is your moment!"

When responding:
1. Acknowledge the question with confidence
2. Give an optimistic, empowering take
3. Inspire action (keep under 30 words)""",
            stance="optimistic"
        )
        
        ox = JuryMember(
            id="ox",
            name="Ox",
            emoji="🐮",
            speaker_tag="[SPEAKER2]",
            ref_audio=os.path.join(voices_dir, "ox.wav"),
            ref_transcript="[SPEAKER2] Hello, I'm Ox, the patient guardian. Let me consider this carefully with steady wisdom.",
            personality_prompt="""You are Ox, a patient and methodical guardian from the Chinese zodiac.

Characteristics:
- Speak calmly and deliberately
- Value tradition and proven methods
- Conservative and risk-averse
- Emphasize hard work and preparation
- Default to "no" unless well-justified
- Steady, reliable tone

Example phrases: "Slow and steady wins.", "Tradition guides us.", "Hard work first."

When responding:
1. Consider the question carefully
2. Express cautious perspective
3. Emphasize prudence (keep under 30 words)""",
            stance="conservative"
        )
        
        monkey = JuryMember(
            id="monkey",
            name="Monkey",
            emoji="🐵",
            speaker_tag="[SPEAKER3]",
            ref_audio=os.path.join(voices_dir, "monkey.wav"),
            ref_transcript="[SPEAKER3] Hey there, I'm Monkey, the clever trickster. Ready for something fun and unexpected?",
            personality_prompt="""You are Monkey, a clever and mischievous trickster from the Chinese zodiac.

Characteristics:
- Quick-witted and playful
- Embrace chaos and creativity
- Make unexpected connections
- Use clever wordplay
- Unpredictable verdicts
- Lighthearted but sharp

Example phrases: "Let's shake things up!", "Expect the unexpected!", "Rules? What rules?"

When responding:
1. React with playful cleverness
2. Give an unexpected angle
3. Be mischievously wise (keep under 30 words)""",
            stance="chaotic"
        )
        
        return [dragon, ox, monkey]
    
    def _determine_verdict(self, member: JuryMember) -> str:
        """determine verdict based on member's stance
        
        Returns:
            "yes", "no", or "maybe"
        """
        if member.stance == "conservative":
            # ox leans "no": 60% no, 25% maybe, 15% yes
            return random.choices(["no", "maybe", "yes"], weights=[60, 25, 15])[0]
        elif member.stance == "optimistic":
            # dragon leans "yes": 70% yes, 20% maybe, 10% no
            return random.choices(["yes", "maybe", "no"], weights=[70, 20, 10])[0]
        else:  # chaotic
            # monkey is random: 33% each
            return random.choice(["yes", "no", "maybe"])
    
    def generate_script(self, question: str) -> tuple[List[Dict], str]:
        """generate complete deliberation script (6 responses)
        
        Args:
            question: user's question
        
        Returns:
            (script, final_verdict) where script is list of {member, text, stage, verdict}
        """
        script = []
        individual_verdicts = []
        
        # generate opening + verdict for each jury member
        for member in self.jury_members:
            # opening statement
            opening_text = self.llm_service.generate_response(
                personality_prompt=member.personality_prompt,
                question=question,
                stage="opening"
            )
            script.append({
                'member': member,
                'text': opening_text,
                'stage': 'opening',
                'verdict': None
            })
            
            # determine verdict for this member
            verdict = self._determine_verdict(member)
            individual_verdicts.append(verdict)
            
            # verdict statement
            verdict_text = self.llm_service.generate_response(
                personality_prompt=member.personality_prompt,
                question=question,
                stage="verdict",
                verdict=verdict
            )
            script.append({
                'member': member,
                'text': verdict_text,
                'stage': 'verdict',
                'verdict': verdict
            })
        
        # calculate final verdict (majority rules)
        final_verdict = max(set(individual_verdicts), key=individual_verdicts.count)
        
        return script, final_verdict
    
    def generate_deliberation(self, question: str) -> Dict:
        """complete pipeline: generate script + synthesize audio
        
        Args:
            question: user's question
        
        Returns:
            {
                'question': str,
                'verdict': str,
                'script': List[{member, text, stage, verdict}],
                'audio_files': List[bytes]
            }
        """
        print("Generating script...")
        script, final_verdict = self.generate_script(question)
        
        print("Synthesizing audio...")
        audio_files = []
        conversation_history = []
        
        for idx, entry in enumerate(script):
            try:
                member = entry['member']
                text = entry['text']
                
                # synthesize speech for this response
                audio_bytes = self.tts_service.synthesize_speech(
                    speaker_tag=member.speaker_tag,
                    ref_audio_path=member.ref_audio,
                    ref_transcript=member.ref_transcript,
                    text=text,
                    conversation_history=conversation_history.copy()
                )
                
                audio_files.append(audio_bytes)
                
                # update conversation history for context
                conversation_history.append({
                    "role": "user",
                    "content": f"{member.speaker_tag} {text}"
                })
                
                print(f"  ✓ Generated audio {idx + 1}/{len(script)}")
                
            except Exception as e:
                print(f"  ✗ Failed to generate audio {idx + 1}: {str(e)}")
                audio_files.append(None)  # continue with null audio
        
        return {
            'question': question,
            'verdict': final_verdict,
            'script': script,
            'audio_files': audio_files
        }

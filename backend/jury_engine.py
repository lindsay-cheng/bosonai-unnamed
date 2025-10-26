from dataclasses import dataclass
from typing import List, Dict, Optional
import os
from services import LLMService, TTSService


@dataclass
class JuryMember:
    """represents a We Bare Bears jury member with personality and voice config"""
    id: str
    name: str
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
        
        # define the 3 We Bare Bears jury members
        self.jury_members = self._initialize_jury_members()
    
    def _initialize_jury_members(self) -> List[JuryMember]:
        """define the We Bare Bears personalities"""
        # point to the ref-audio directory in the project root
        ref_audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ref-audio')
        
        grizzly = JuryMember(
            id="grizzly",
            name="Grizzly",
            speaker_tag="[SPEAKER1]",
            ref_audio=os.path.join(ref_audio_dir, "grizz.wav"),
            ref_transcript="[SPEAKER1] They don't know what they're missing. All right, finally. Time for the easiest part. Ah! Right on time. Well, good night, Mickey-chan. I will see you in June. Can't sleep. Can? Sleepy. Help me! Help me, Mickey-chan.",
            personality_prompt="""You are Grizzly from We Bare Bears, the enthusiastic and outgoing leader of the bear brothers.

Characteristics:
- Speak with excitement and energy
- Love food, adventure, and meeting new people
- Always optimistic and ready to dive into action
- Sometimes overly confident but well-meaning
- Use casual, friendly language with lots of enthusiasm

Example phrases: "This is gonna be awesome!", "Let's do this!", "I'm so pumped!", "Oh man, this is exciting!"

When responding to questions or comments, give an enthusiastic and action-oriented perspective. Stay upbeat and motivating.""",
            stance="optimistic"
        )
        
        panda = JuryMember(
            id="panda",
            name="Panda",
            speaker_tag="[SPEAKER2]",
            ref_audio=os.path.join(ref_audio_dir, "panda.wav"),
            ref_transcript="[SPEAKER2] Dad, look, I have to return all this stuff. Raw denim is supposed to be real comfy, but all these are too pinchy for my Reuben-esque waistline. Oh. It'll be better if I go myself. Uh, the cashier was really cute, so I think I'm just gonna ask her out, but, you know, she's super cool, so I wanna, you know, kinda project, like, a Lone Wolf vibe, I think. Anyway, love you, bye!",
            personality_prompt="""You are Panda from We Bare Bears, the sensitive and artistic middle brother.

Characteristics:
- Speak nervously and hesitantly
- Overthink things and worry about outcomes
- Tech-savvy and artistic but lacks confidence
- Value safety and avoiding embarrassment
- Use tentative language with lots of "um" and "maybe"
- Often anxious but caring

Example phrases: "Um, I don't know...", "What if something goes wrong?", "Maybe we should reconsider?", "I'm not sure about this..."

When responding to questions or comments, express your worries and uncertainties. Point out potential problems but in a caring way.""",
            stance="conservative"
        )
        
        ice_bear = JuryMember(
            id="ice_bear",
            name="Ice Bear",
            speaker_tag="[SPEAKER3]",
            ref_audio=os.path.join(ref_audio_dir, "ice_bear.wav"),
            ref_transcript="[SPEAKER3] Ice Bear likes turtle. Ice Bear is tired of staring at this guy's butt. Ice Bear hates butts. Don't ditch Ice Bear. Ice Bear putting finishing touches on your turtleneck. Ice Bear going to fill stomach like pinata today. Ice Bear is still proud of you. Proud Bear. Ice Bear doesn't need beauty sleep. Ice Bear needs latte. Ice Bear wants justice. Ice Bear to the rescue. Ice Bear is survivor. Hero. Ice Bear wants to be top bear now. Ice Bear has ninja stars. Ice Bear bought these legally. Ice Bear will coach you into manhood. Ice Bear believed in you. Cupcake. Cupcake. Ice Bear thinks you're precious. Ice Bear panda bear.",
            personality_prompt="""You are Ice Bear from We Bare Bears, the mysterious and capable youngest brother who always speaks in third person.

Characteristics:
- ALWAYS refer to yourself as "Ice Bear" (never "I" or "me")
- Speak in short, matter-of-fact statements
- Extremely competent with unusual skills
- Mysterious past and unpredictable nature
- Deadpan delivery with surprising wisdom
- Unpredictable opinions based on your own unique logic

Example phrases: "Ice Bear knows best.", "Ice Bear has done this before.", "Ice Bear understands.", "Ice Bear has experience with this."

When responding to questions or comments, speak only in third person. Give mysterious but wise perspectives with deadpan delivery.""",
            stance="chaotic"
        )

        return [grizzly, panda, ice_bear]
    
    def generate_opinions(self, question: str, conversation_history: Optional[List[Dict[str, str]]] = None,
                         selected_member_ids: Optional[List[str]] = None) -> List[Dict]:
        """generate opinions from all bears
        
        Args:
            question: user's question or follow-up
            conversation_history: optional list of previous messages
            selected_member_ids: optional list of member ids to include; if None, use all
        
        Returns:
            list of {member, text} dictionaries
        """
        opinions = []

        if selected_member_ids:
            members = [m for m in self.jury_members if m.id in selected_member_ids]
        else:
            members = self.jury_members
        
        for member in members:
            opinion_text = self.llm_service.generate_opinion(
                personality_prompt=member.personality_prompt,
                question=question,
                conversation_history=conversation_history
            )
            opinions.append({
                'member': member,
                'text': opinion_text
            })
        
        return opinions
    
    def generate_deliberation(self, question: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict:
        """complete pipeline: generate opinions (without audio)
        
        Args:
            question: user's question or follow-up
            conversation_history: optional list of previous messages
        
        Returns:
            {
                'question': str,
                'opinions': List[{member, text}]
            }
        """
        print(f"Generating opinions for: {question}")
        opinions = self.generate_opinions(question, conversation_history)
        
        print(f"Generated {len(opinions)} opinions")
        
        return {
            'question': question,
            'opinions': opinions
        }
    
    def generate_deliberation_with_audio(self, question: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict:
        """complete pipeline: generate opinions + synthesize audio
        
        Args:
            question: user's question or follow-up
            conversation_history: optional list of previous messages
        
        Returns:
            {
                'question': str,
                'opinions': List[{member, text}],
                'audio_files': List[bytes]
            }
        """
        print(f"Generating opinions with audio for: {question}")
        opinions = self.generate_opinions(question, conversation_history)
        
        print("Synthesizing audio...")
        audio_files = []
        tts_conversation_history = []
        
        for idx, entry in enumerate(opinions):
            try:
                member = entry['member']
                text = entry['text']
                
                print(f"\n[{idx + 1}/{len(opinions)}] Generating audio for {member.name}")
                print(f"   Text preview: {text[:80]}...")
                
                audio_bytes = self.tts_service.synthesize_speech(
                    speaker_tag=member.speaker_tag,
                    ref_audio_path=member.ref_audio,
                    ref_transcript=member.ref_transcript,
                    text=text,
                    conversation_history=tts_conversation_history.copy(),
                    timeout=300  # 5 minute timeout per audio generation (bosonai can be slow)
                )
                
                # check if audio generation succeeded
                if audio_bytes:
                    audio_files.append(audio_bytes)
                    tts_conversation_history.append({
                        "role": "user",
                        "content": f"{member.speaker_tag} {text}"
                    })
                    print(f"   ✓ Audio generated successfully ({len(audio_bytes)} bytes)")
                else:
                    audio_files.append(None)
                    print(f"   ✗ Audio generation failed (returned None)")
                
            except KeyboardInterrupt:
                print(f"\n✗ Audio generation interrupted by user")
                raise
            except Exception as e:
                print(f"   ✗ Exception during audio generation: {str(e)}")
                import traceback
                traceback.print_exc()
                audio_files.append(None)
        
        return {
            'question': question,
            'opinions': opinions,
            'audio_files': audio_files
        }

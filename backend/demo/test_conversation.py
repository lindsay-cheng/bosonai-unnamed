import os
from dotenv import load_dotenv
from jury_engine import JuryEngine

# load environment variables
load_dotenv()

# get API keys
BOSON_API_KEY = os.getenv('BOSON_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# check keys
if not BOSON_API_KEY or not GOOGLE_API_KEY:
    print("Error: Missing API keys!")
    print(f"BOSON_API_KEY: {'OK' if BOSON_API_KEY else 'MISSING'}")
    print(f"GOOGLE_API_KEY: {'OK' if GOOGLE_API_KEY else 'MISSING'}")
    exit(1)

# initialize engine
print("Initializing We Bare Bears conversation engine...")
engine = JuryEngine(
    boson_api_key=BOSON_API_KEY,
    google_api_key=GOOGLE_API_KEY
)
print("Engine ready!\n")

# get user input
question = input("Enter your question: ").strip()

if not question:
    print("No question provided!")
    exit(1)

print(f"\nQuestion: {question}")
print("="*50)

# generate conversation
try:
    result = engine.generate_deliberation(question)
    
    # print the conversation
    print("\nWE BARE BEARS CONVERSATION\n")
    
    for idx, (entry, audio_bytes) in enumerate(zip(result['script'], result['audio_files'])):
        member = entry['member']
        text = entry['text']
        stage = entry['stage']
        
        print(f"{member.name} ({stage}):")
        print(f"   {text}\n")
        
        # save audio file
        if audio_bytes:
            output_file = f"conversation_{idx}_{member.id}.wav"
            with open(output_file, "wb") as f:
                f.write(audio_bytes)
            print(f"   Audio saved: {output_file}\n")
    
    print("="*50)
    print(f"Conversation complete! {len(result['audio_files'])} audio files generated.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
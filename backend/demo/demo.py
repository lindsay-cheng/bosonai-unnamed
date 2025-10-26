from openai import OpenAI
import google.generativeai as genai
import base64
import os

# api keys
BOSON_API_KEY = os.getenv("BOSON_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# setup clients
boson_client = OpenAI(api_key=BOSON_API_KEY, base_url="https://hackathon.boson.ai/v1")
genai.configure(api_key=GOOGLE_API_KEY)

def b64(path):
    return base64.b64encode(open(path, "rb").read()).decode("utf-8")

reference_path = "./ref-audio/jeongspeechphysics.wav"
reference_transcript = (
    "[SPEAKER1]"
    "Physics is the scientific study of matter, its fundamental constituents, its motion and behavior through space and time, and the related entities of energy and force. It is one of the most fundamental scientific disciplines. A scientist who specializes in the field of physics is called a physicist."
)

system = (
    "You are an AI assistant designed to convert text into speech.\n"
    "If the user's message includes a [SPEAKER*] tag, do not read out the tag and generate speech for the following text, using the specified voice.\n"
    "If no speaker tag is present, select a suitable voice on your own.\n\n"
    "<|scene_desc_start|>\nAudio is recorded from a quiet room.\n<|scene_desc_end|>"
)

# load reference audio once
reference_audio_b64 = b64(reference_path)

def generate_llm_response(user_message):
    """generate text response using gemini"""
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    response = model.generate_content(user_message)
    return response.text

def generate_speech(text):
    """generate speech from text input"""
    resp = boson_client.chat.completions.create(
        model="higgs-audio-generation-Hackathon",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": reference_transcript},
            {
                "role": "assistant",
                "content": [{
                    "type": "input_audio",
                    "input_audio": {"data": reference_audio_b64, "format": "wav"}
                }],
            },
            {"role": "user", "content": f"[SPEAKER1] {text}"},
        ],
        modalities=["text", "audio"],
        max_completion_tokens=4096,
        temperature=1.0,
        top_p=0.95,
        stream=False,
        stop=["<|eot_id|>", "<|end_of_text|>", "<|audio_eos|>"],
        extra_body={"top_k": 50},
    )
    
    audio_b64 = resp.choices[0].message.audio.data
    return base64.b64decode(audio_b64)

# main loop
print("AI Voice Chat ready! Type your message (or 'quit' to exit)")
counter = 1

while True:
    user_input = input("\nYou: ").strip()
    
    if user_input.lower() in ['quit', 'exit', 'q']:
        print("Goodbye!")
        break
    
    if not user_input:
        print("Please enter some text")
        continue
    
    try:
        # step 1: generate text response using gemini
        print("Thinking...")
        llm_response = generate_llm_response(user_input)
        print(f"AI: {llm_response}")
        
        # step 2: convert text to speech
        print("Generating speech...")
        audio_data = generate_speech(llm_response)
        output_file = f"output_{counter}.wav"
        open(output_file, "wb").write(audio_data)
        print(f"Audio saved to {output_file}")
        counter += 1
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
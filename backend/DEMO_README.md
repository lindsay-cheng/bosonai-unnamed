# The Jury - Demo Script

Quick demo to test the complete pipeline: LLM text generation + BosonAI audio synthesis.

## Setup

1. **Create `.env` file** in the `backend/` directory:

```env
BOSON_API_KEY=your_boson_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
LLM_PROVIDER=openai
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Make sure `jury_engine.py` is implemented** with:
   - `JuryEngine` class
   - `JuryMember` class  
   - All methods from the PRD

## Running the Demo

```bash
cd backend
python demo.py
```

## What the Demo Does

1. ✅ Loads and validates API keys
2. 🔧 Initializes JuryEngine with 3 jury members
3. 📝 Generates script (6 responses) using LLM
4. 🎙️ Synthesizes audio for each response using BosonAI voice cloning
5. 💾 Saves audio files to `./temp/demo/`
6. 📊 Displays timing and success metrics

## Sample Output

```
🏛️  THE JURY - DEMO SCRIPT
===========================================================

✅ API keys loaded
   LLM Provider: openai
   BosonAI: sk-boson...

🔧 INITIALIZING JURY ENGINE
===========================================================
✅ Jury engine initialized with 3 members
   ⚖️ Judge Protocol (conservative)
   ☀️ Sunny McPositive (optimistic)
   🌀 Agent Entropy (chaotic)

📝 GENERATING SCRIPT
===========================================================
Question: "Should I quit my job to become a professional cat video creator?"

✅ Script generated in 4.2s
   Responses: 6
   Final verdict: MAYBE

🎙️  SYNTHESIZING AUDIO
===========================================================
[1/6] ⚖️ Judge Protocol... ✅ (45231 bytes)
[2/6] ☀️ Sunny McPositive... ✅ (48192 bytes)
[3/6] 🌀 Agent Entropy... ✅ (43889 bytes)
[4/6] ⚖️ Judge Protocol... ✅ (46102 bytes)
[5/6] ☀️ Sunny McPositive... ✅ (47554 bytes)
[6/6] 🌀 Agent Entropy... ✅ (44201 bytes)

📊 DEMO SUMMARY
===========================================================
Final Verdict: MAYBE

Timing:
   Script Generation: 4.2s
   Audio Synthesis: 12.8s
   Total Time: 17.0s

Audio Files:
   Generated: 6/6

🎉 DEMO COMPLETE
```

## Troubleshooting

- **"jury_engine.py not found"**: Implement the JuryEngine class first
- **"API key not found"**: Create `.env` file with your keys
- **"Audio synthesis failed"**: Check BosonAI API quota/connectivity
- **"LLM generation failed"**: Verify OpenAI API key and credits

## Next Steps

After successful demo:

1. Run the full Flask API: `python app.py`
2. Start the frontend: `cd ../frontend && npm run dev`
3. Test the complete app in your browser


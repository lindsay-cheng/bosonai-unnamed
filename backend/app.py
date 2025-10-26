import os
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from jury_engine import JuryEngine
from services import GeminiASRService
import traceback

# load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# get API keys from environment
BOSON_API_KEY = os.getenv('BOSON_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# check required keys
if not BOSON_API_KEY:
    print("WARNING: BOSON_API_KEY not found in environment variables")
if not GOOGLE_API_KEY:
    print("WARNING: GOOGLE_API_KEY not found in environment variables")

# initialize jury engine
engine = None
if BOSON_API_KEY and GOOGLE_API_KEY:
    try:
        engine = JuryEngine(
            boson_api_key=BOSON_API_KEY,
            google_api_key=GOOGLE_API_KEY
        )
        print("✓ Jury engine initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize jury engine: {str(e)}")

# initialize gemini ASR service
asr_service = None
if GOOGLE_API_KEY:
    try:
        asr_service = GeminiASRService(api_key=GOOGLE_API_KEY)
        print("✓ Gemini ASR initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize Gemini ASR: {str(e)}")

# create temp directory for audio files
TEMP_DIR = os.path.join(os.path.dirname(__file__), 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)


@app.route('/health', methods=['GET'])
def health_check():
    """health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'bosonai_tts': 'connected' if BOSON_API_KEY else 'not configured',
            'google_gemini': 'connected' if GOOGLE_API_KEY else 'not configured',
            'gemini_asr': 'connected' if asr_service else 'not configured'
        },
        'engine': 'initialized' if engine else 'not initialized'
    })


@app.route('/api/jury-members', methods=['GET'])
def get_jury_members():
    """return list of jury members"""
    if not engine:
        return jsonify({'error': 'Engine not initialized'}), 500
    
    members = [{
        'id': member.id,
        'name': member.name,
        'stance': member.stance
    } for member in engine.jury_members]
    
    return jsonify(members)


@app.route('/api/opinions', methods=['POST'])
def generate_opinions():
    """generate bear opinions with audio for a question or audio file"""
    try:
        question = None
        conversation_history = []
        
        if 'audio' in request.files:
            if not asr_service:
                return jsonify({'error': 'ASR service not configured'}), 500
            
            audio_file = request.files['audio']
            if audio_file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            print(f"Transcribing audio file: {audio_file.filename}")
            result = asr_service.transcribe_audio(audio_file)
            question = result['text']
            print(f"Transcription: {question}")
            
            if request.form.get('conversation_history'):
                import json
                conversation_history = json.loads(request.form.get('conversation_history'))
        else:
            data = request.get_json()
            if not data or 'question' not in data:
                return jsonify({'error': 'Question or audio file is required'}), 400
            
            question = data['question'].strip()
            conversation_history = data.get('conversation_history', [])
        
        if len(question) < 3:
            return jsonify({'error': 'Question must be at least 3 characters'}), 400
        if len(question) > 500:
            return jsonify({'error': 'Question must be less than 500 characters'}), 400
        
        if not engine:
            return jsonify({'error': 'Engine not initialized'}), 500
        
        print(f"Generating opinions for: {question}")
        
        result = engine.generate_deliberation_with_audio(question, conversation_history)
        
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(TEMP_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        opinions = []
        for idx, (entry, audio_bytes) in enumerate(zip(result['opinions'], result['audio_files'])):
            member = entry['member']
            
            audio_index = None
            if audio_bytes:
                audio_path = os.path.join(session_dir, f'{idx}.wav')
                with open(audio_path, 'wb') as f:
                    f.write(audio_bytes)
                audio_index = idx
            
            opinions.append({
                'speaker': member.name,
                'text': entry['text'],
                'audio_index': audio_index
            })
        
        response = {
            'session_id': session_id,
            'question': question,
            'opinions': opinions
        }
        
        print(f"✓ Generated {len(opinions)} opinions with audio")
        return jsonify(response)
    
    except Exception as e:
        print(f"Error generating opinions: {str(e)}")
        print(traceback.format_exc())
        error_message = str(e)
        return jsonify({
            'error': f'Failed to generate opinions: {error_message}',
            'details': error_message
        }), 500


@app.route('/api/audio/<session_id>/<int:index>', methods=['GET'])
def get_audio(session_id, index):
    """serve audio file for a specific session and bear index"""
    try:
        audio_path = os.path.join(TEMP_DIR, session_id, f'{index}.wav')
        
        if not os.path.exists(audio_path):
            return jsonify({'error': 'Audio file not found'}), 404
        
        return send_file(audio_path, mimetype='audio/wav')
    
    except Exception as e:
        print(f"Error serving audio: {str(e)}")
        return jsonify({'error': 'Failed to serve audio'}), 500


@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """transcribe audio file to text using Gemini ASR"""
    try:
        if not asr_service:
            return jsonify({'error': 'ASR service not configured'}), 500
        
        if 'audio' not in request.files:
            return jsonify({'error': 'Audio file is required'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        print(f"Transcribing audio file: {audio_file.filename}")
        
        result = asr_service.transcribe_audio(audio_file)
        
        print(f"Transcription result: {result['text'][:50]}...")
        
        return jsonify({
            'transcript': result['text'],
            'language': result.get('language', 'en')
        })
    
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': 'Failed to transcribe audio',
            'details': str(e)
        }), 500


@app.route('/', methods=['GET'])
def index():
    """root endpoint with API info"""
    return jsonify({
        'name': 'The Jury API',
        'version': '2.0.0',
        'description': 'AI voice-based conversation with We Bare Bears personalities - Powered by Gemini + BosonAI',
        'endpoints': {
            'GET /health': 'Health check',
            'GET /api/jury-members': 'List all We Bare Bears jury members',
            'POST /api/transcribe': 'Transcribe audio to text using Gemini',
            'POST /api/opinions': 'Generate bear opinions with audio (accepts audio file or JSON with question)',
            'GET /api/audio/<session_id>/<index>': 'Get audio file for a bear response'
        }
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    print("\n" + "="*50)
    print("THE JURY - We Bare Bears Council")
    print("="*50)
    print(f"Port: {port}")
    print(f"Services:")
    print(f"  - BosonAI TTS: {'✓' if BOSON_API_KEY else '✗'}")
    print(f"  - Google Gemini LLM: {'✓' if GOOGLE_API_KEY else '✗'}")
    print(f"  - Gemini ASR: {'✓' if asr_service else '✗'}")
    print(f"Engine: {'✓ Ready' if engine else '✗ Not initialized'}")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=port)


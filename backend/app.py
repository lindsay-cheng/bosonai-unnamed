import os
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from jury_engine import JuryEngine
import traceback

# load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# initialize jury engine
BOSON_API_KEY = os.getenv('BOSON_API_KEY')
if not BOSON_API_KEY:
    print("WARNING: BOSON_API_KEY not found in environment variables")

engine = JuryEngine(BOSON_API_KEY) if BOSON_API_KEY else None

# create temp directory for audio files
TEMP_DIR = os.path.join(os.path.dirname(__file__), 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)


@app.route('/health', methods=['GET'])
def health_check():
    """health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'bosonai': 'connected' if BOSON_API_KEY else 'not configured'
    })


@app.route('/api/jury-members', methods=['GET'])
def get_jury_members():
    """return list of jury members"""
    if not engine:
        return jsonify({'error': 'Engine not initialized'}), 500
    
    members = [{
        'id': member.id,
        'name': member.name,
        'emoji': member.emoji,
        'stance': member.stance
    } for member in engine.jury_members]
    
    return jsonify(members)


@app.route('/api/verdict', methods=['POST'])
def generate_verdict():
    """generate jury deliberation for a question"""
    try:
        # validate request
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        
        question = data['question'].strip()
        
        # validate question length
        if len(question) < 10:
            return jsonify({'error': 'Question must be at least 10 characters'}), 400
        if len(question) > 500:
            return jsonify({'error': 'Question must be less than 500 characters'}), 400
        
        if not engine:
            return jsonify({'error': 'BosonAI API not configured'}), 500
        
        print(f"Generating verdict for: {question}")
        
        # generate deliberation
        result = engine.generate_deliberation(question)
        
        # create unique verdict ID
        verdict_id = str(uuid.uuid4())
        verdict_dir = os.path.join(TEMP_DIR, verdict_id)
        os.makedirs(verdict_dir, exist_ok=True)
        
        # save audio files and build response
        deliberation = []
        for idx, (entry, audio_bytes) in enumerate(zip(result['script'], result['audio_files'])):
            member = entry['member']
            
            # save audio file
            if audio_bytes:
                audio_path = os.path.join(verdict_dir, f'{idx}.wav')
                with open(audio_path, 'wb') as f:
                    f.write(audio_bytes)
            
            deliberation.append({
                'speaker': member.name,
                'emoji': member.emoji,
                'text': entry['text'],
                'stage': entry['stage'],
                'audio_index': idx if audio_bytes else None
            })
        
        response = {
            'verdict_id': verdict_id,
            'question': question,
            'verdict': result['verdict'],
            'deliberation': deliberation
        }
        
        print(f"Verdict generated: {result['verdict']}")
        return jsonify(response)
    
    except Exception as e:
        print(f"Error generating verdict: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': 'Failed to generate verdict',
            'details': str(e)
        }), 500


@app.route('/api/audio/<verdict_id>/<int:index>', methods=['GET'])
def get_audio(verdict_id, index):
    """serve audio file for a specific verdict and index"""
    try:
        audio_path = os.path.join(TEMP_DIR, verdict_id, f'{index}.wav')
        
        if not os.path.exists(audio_path):
            return jsonify({'error': 'Audio file not found'}), 404
        
        return send_file(audio_path, mimetype='audio/wav')
    
    except Exception as e:
        print(f"Error serving audio: {str(e)}")
        return jsonify({'error': 'Failed to serve audio'}), 500


@app.route('/', methods=['GET'])
def index():
    """root endpoint with API info"""
    return jsonify({
        'name': 'The Jury API',
        'version': '1.0.0',
        'description': 'AI voice-based decision oracle',
        'endpoints': {
            'GET /health': 'Health check',
            'GET /api/jury-members': 'List all jury members',
            'POST /api/verdict': 'Generate verdict for a question',
            'GET /api/audio/<verdict_id>/<index>': 'Get audio file'
        }
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Starting The Jury API on port {port}")
    print(f"BosonAI API configured: {BOSON_API_KEY is not None}")
    app.run(debug=True, host='0.0.0.0', port=port)


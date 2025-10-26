'use client';

import { useState, useRef } from 'react';

interface BearOpinion {
  speaker: string;
  text: string;
  audio_index?: number | null;
}

interface DeliberationData {
  question: string;
  opinions: BearOpinion[];
  session_id?: string;
}

interface DeliberationPageProps {
  data: DeliberationData;
  onReset: () => void;
  onFollowUp: (followUp: string) => void;
  isLoading?: boolean;
  apiUrl?: string;
}

export default function DeliberationPage({ data, onReset, onFollowUp, isLoading, apiUrl = 'http://localhost:8080' }: DeliberationPageProps) {
  const [followUpText, setFollowUpText] = useState('');
  const [playingIndex, setPlayingIndex] = useState<number | null>(null);
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);

  function handleSubmitFollowUp() {
    if (followUpText.trim()) {
      onFollowUp(followUpText.trim());
      setFollowUpText('');
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmitFollowUp();
    }
  }

  function handlePlayAudio(index: number, audioIndex: number | null | undefined, sessionId: string | undefined) {
    if (audioIndex === null || audioIndex === undefined || !sessionId) return;
    
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current = null;
    }
    
    setPlayingIndex(index);
    const audio = new Audio(`${apiUrl}/api/audio/${sessionId}/${audioIndex}`);
    currentAudioRef.current = audio;
    
    audio.onended = () => {
      setPlayingIndex(null);
      currentAudioRef.current = null;
    };
    
    audio.onerror = () => {
      console.error('Failed to play audio');
      setPlayingIndex(null);
      currentAudioRef.current = null;
    };
    
    audio.play().catch(err => {
      console.error('Failed to play audio:', err);
      setPlayingIndex(null);
      currentAudioRef.current = null;
    });
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="max-w-4xl w-full space-y-8">
        <div className="text-center space-y-3">
          <h1 className="text-3xl md:text-4xl font-bold text-white">Bear Council</h1>
          <p className="text-gray-400">{data.question}</p>
        </div>

        <div className="space-y-5">
          {data.opinions.map((opinion, index) => (
            <div
              key={opinion.speaker}
              className="p-6 rounded-xl bg-gray-900 transition-all duration-300"
            >
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-xl font-semibold text-white">{opinion.speaker}</h3>
                {opinion.audio_index !== null && opinion.audio_index !== undefined && (
                  <button
                    onClick={() => handlePlayAudio(index, opinion.audio_index, data.session_id)}
                    disabled={playingIndex === index}
                    className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {playingIndex === index ? 'Playing...' : 'Play Audio'}
                  </button>
                )}
              </div>
              <p className="text-gray-300 text-lg leading-relaxed">{opinion.text}</p>
            </div>
          ))}
        </div>

        {isLoading && (
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
            <p className="text-gray-400 mt-2">Bears are thinking...</p>
          </div>
        )}

        <div className="space-y-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={followUpText}
              onChange={(e) => setFollowUpText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Add a follow-up question..."
              disabled={isLoading}
              className="flex-1 px-4 py-3 bg-gray-900 text-white rounded-lg placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50"
            />
            <button
              onClick={handleSubmitFollowUp}
              disabled={!followUpText.trim() || isLoading}
              className="px-6 py-3 bg-white text-black font-medium rounded-lg hover:bg-gray-100 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Ask
            </button>
          </div>
          
          <button
            onClick={onReset}
            className="w-full px-6 py-3 bg-gray-800 text-white font-medium rounded-lg hover:bg-gray-700 transition-colors duration-200"
          >
            Start Over
          </button>
        </div>
      </div>
    </div>
  );
}

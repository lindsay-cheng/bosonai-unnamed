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

// bear colors for visual variety
const bearColors: Record<string, string> = {
  'Grizzly': 'from-amber-900/20 to-amber-950/20 border-amber-700/30',
  'Panda': 'from-gray-800/20 to-gray-900/20 border-gray-600/30',
  'Ice Bear': 'from-cyan-900/20 to-blue-950/20 border-cyan-700/30',
};

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
    <div className="min-h-screen bg-gradient-to-b from-black via-gray-900 to-black flex items-center justify-center p-6">
      <div className="max-w-4xl w-full space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
        {/* header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-white via-gray-200 to-white bg-clip-text text-transparent">
            The Bears
          </h1>
          <div className="max-w-2xl mx-auto">
            <p className="text-gray-300 text-lg italic">"{data.question}"</p>
          </div>
          <div className="h-px w-32 mx-auto bg-gradient-to-r from-transparent via-white/30 to-transparent"></div>
        </div>

        {/* opinions with staggered animation */}
        <div className="space-y-6">
          {data.opinions.map((opinion, index) => {
            const colorClass = bearColors[opinion.speaker] || 'from-gray-800/20 to-gray-900/20 border-gray-600/30';
            return (
              <div
                key={opinion.speaker}
                className={`p-6 rounded-2xl bg-gradient-to-br ${colorClass} border backdrop-blur-sm transition-all duration-500 hover:scale-[1.02] hover:shadow-xl hover:shadow-white/5 animate-in fade-in slide-in-from-left-8`}
                style={{ animationDelay: `${index * 150}ms` }}
              >
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="text-2xl font-bold text-white">
                    {opinion.speaker}
                  </h3>
                  {opinion.audio_index !== null && opinion.audio_index !== undefined && (
                    <button
                      onClick={() => handlePlayAudio(index, opinion.audio_index, data.session_id)}
                      disabled={playingIndex === index}
                      className="px-5 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed border border-white/10"
                    >
                      {playingIndex === index ? 'Playing...' : 'Play Audio'}
                    </button>
                  )}
                </div>
                <p className="text-gray-200 text-lg leading-relaxed">{opinion.text}</p>
              </div>
            );
          })}
        </div>

        {/* loading state */}
        {isLoading && (
          <div className="text-center py-8 animate-in fade-in duration-300">
            <div className="inline-flex items-center gap-3 px-6 py-3 bg-white/5 rounded-full border border-white/10">
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
              <p className="text-gray-300">Bears are thinking...</p>
            </div>
          </div>
        )}

        {/* actions */}
        <div className="space-y-4 pt-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={followUpText}
              onChange={(e) => setFollowUpText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a follow-up question..."
              disabled={isLoading}
              className="flex-1 px-5 py-4 bg-white/5 text-white rounded-xl placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white/30 focus:bg-white/10 disabled:opacity-50 transition-all duration-300 border border-white/10"
            />
            <button
              onClick={handleSubmitFollowUp}
              disabled={!followUpText.trim() || isLoading}
              className="px-8 py-4 bg-white text-black font-semibold rounded-xl hover:bg-gray-100 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 shadow-lg hover:shadow-xl"
            >
              Ask
            </button>
          </div>
          
          <button
            onClick={onReset}
            className="w-full px-6 py-4 bg-white/5 text-white font-medium rounded-xl hover:bg-white/10 transition-all duration-300 border border-white/10 hover:border-white/20"
          >
            Start Over
          </button>
        </div>
      </div>
    </div>
  );
}

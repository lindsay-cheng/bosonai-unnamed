'use client';

import { useState, useCallback } from 'react';
import HomePage from '@/components/HomePage';
import ThinkingPage from '@/components/ThinkingPage';
import DeliberationPage from '@/components/DeliberationPage';

type AppState = 'home' | 'thinking' | 'deliberation';

interface BearOpinion {
  speaker: string;
  text: string;
  audio_index: number | null;
}

interface DeliberationData {
  question: string;
  opinions: BearOpinion[];
  session_id: string;
}

interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export default function Home() {
  const [appState, setAppState] = useState<AppState>('home');
  const [deliberationData, setDeliberationData] = useState<DeliberationData | null>(null);
  const [conversationHistory, setConversationHistory] = useState<ConversationMessage[]>([]);
  const [isLoadingFollowUp, setIsLoadingFollowUp] = useState(false);

  const handleRecordingComplete = useCallback(async (blob: Blob) => {
    setAppState('thinking');

    try {
      const formData = new FormData();
      formData.append('audio', blob, 'recording.webm');
      formData.append('conversation_history', JSON.stringify(conversationHistory));

      const response = await fetch(`${API_BASE_URL}/api/opinions`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        console.error('Backend error:', errorData);
        throw new Error(errorData.error || 'Failed to get opinions from bears');
      }

      const data = await response.json();
      
      setDeliberationData({
        question: data.question,
        opinions: data.opinions,
        session_id: data.session_id
      });
      setConversationHistory(prev => [...prev, { role: 'user', content: data.question }]);
      setAppState('deliberation');
    } catch (error) {
      console.error('Recording error:', error);
      let errorMessage = 'Failed to get bear opinions';
      
      if (error instanceof Error) {
        if (error.message.includes('fetch')) {
          errorMessage = 'Cannot connect to backend. Please make sure the backend server is running on port 8080.';
        } else {
          errorMessage = error.message;
        }
      }
      
      alert(`${errorMessage}\n\nPlease check the console for details.`);
      setAppState('home');
    }
  }, [conversationHistory]);

  const handleFollowUp = useCallback(async (followUpText: string) => {
    if (!deliberationData) return;

    setIsLoadingFollowUp(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/opinions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: followUpText,
          conversation_history: [...conversationHistory, { role: 'user', content: followUpText }]
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        console.error('Backend error:', errorData);
        throw new Error(errorData.error || 'Failed to get follow-up opinions');
      }

      const data = await response.json();

      setDeliberationData({
        question: data.question,
        opinions: data.opinions,
        session_id: data.session_id
      });
      setConversationHistory(prev => [...prev, { role: 'user', content: followUpText }]);
      setIsLoadingFollowUp(false);
    } catch (error) {
      console.error('Follow-up error:', error);
      let errorMessage = 'Failed to get follow-up opinions';
      
      if (error instanceof Error) {
        if (error.message.includes('fetch')) {
          errorMessage = 'Cannot connect to backend. Please make sure the backend server is running on port 8080.';
        } else {
          errorMessage = error.message;
        }
      }
      
      alert(`${errorMessage}\n\nPlease check the console for details.`);
      setIsLoadingFollowUp(false);
    }
  }, [deliberationData, conversationHistory]);

  const handleReset = useCallback(() => {
    setAppState('home');
    setDeliberationData(null);
    setConversationHistory([]);
    setIsLoadingFollowUp(false);
  }, []);

  return (
    <div className="min-h-screen bg-black relative">
      <div className={`transition-opacity duration-500 ${appState === 'home' ? 'opacity-100' : 'opacity-0 absolute inset-0 pointer-events-none'}`}>
        {appState === 'home' && (
          <HomePage onRecordingComplete={handleRecordingComplete} />
        )}
      </div>
      <div className={`transition-opacity duration-500 ${appState === 'thinking' ? 'opacity-100' : 'opacity-0 absolute inset-0 pointer-events-none'}`}>
        {appState === 'thinking' && <ThinkingPage />}
      </div>
      <div className={`transition-opacity duration-500 ${appState === 'deliberation' ? 'opacity-100' : 'opacity-0 absolute inset-0 pointer-events-none'}`}>
        {appState === 'deliberation' && deliberationData && (
          <DeliberationPage
            data={deliberationData}
            onReset={handleReset}
            onFollowUp={handleFollowUp}
            isLoading={isLoadingFollowUp}
            apiUrl={API_BASE_URL}
          />
        )}
      </div>
    </div>
  );
}

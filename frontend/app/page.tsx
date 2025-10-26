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
      console.error('Error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to get bear opinions';
      alert(`${errorMessage}. Please check the console for details.`);
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
        throw new Error('Failed to get follow-up opinions');
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
      console.error('Error:', error);
      alert('Failed to get follow-up opinions. Please try again.');
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
    <div className="min-h-screen bg-black">
      {appState === 'home' && (
        <HomePage onRecordingComplete={handleRecordingComplete} />
      )}
      {appState === 'thinking' && <ThinkingPage />}
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
  );
}

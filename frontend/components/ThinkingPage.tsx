'use client';

export default function ThinkingPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="text-center space-y-8">
        <h1 className="text-4xl md:text-5xl font-bold text-white animate-pulse">
          Council Deliberating...
        </h1>
        
        <div className="flex justify-center space-x-3">
          <div className="w-4 h-4 bg-white rounded-full animate-bounce"></div>
          <div className="w-4 h-4 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-4 h-4 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
        
        <p className="text-gray-400 text-lg">
          The council members are reviewing your question...
        </p>
      </div>
    </div>
  );
}

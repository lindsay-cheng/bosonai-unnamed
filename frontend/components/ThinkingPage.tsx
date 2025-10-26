'use client';

export default function ThinkingPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-gradient-to-b from-black via-gray-900 to-black">
      <div className="text-center space-y-12 max-w-2xl">
        {/* main heading with gradient */}
        <div className="space-y-4">
          <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-white via-gray-300 to-white bg-clip-text text-transparent animate-pulse">
            Bears Deliberating
          </h1>
          <div className="h-1 w-48 mx-auto bg-gradient-to-r from-transparent via-white to-transparent animate-pulse"></div>
        </div>
        
        {/* improved loading animation */}
        <div className="flex justify-center items-center space-x-2">
          {[0, 1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="w-3 h-3 bg-white rounded-full animate-bounce"
              style={{ 
                animationDelay: `${i * 0.15}s`,
                animationDuration: '0.6s'
              }}
            />
          ))}
        </div>
        
        {/* enhanced description */}
        <div className="space-y-3">
          <p className="text-gray-400 text-lg">
            The Bears are reviewing your question
          </p>
          <div className="flex flex-wrap justify-center gap-2 text-sm text-gray-500">
            <span className="px-3 py-1 bg-white/5 rounded-full animate-pulse" style={{ animationDelay: '0s' }}>
              Analyzing context
            </span>
            <span className="px-3 py-1 bg-white/5 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}>
              Forming perspectives
            </span>
            <span className="px-3 py-1 bg-white/5 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}>
              Preparing responses
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

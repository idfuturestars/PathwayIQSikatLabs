import React from 'react';
import StarLogo from './StarLogo';

const LoadingScreen = () => {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-center">
        <div className="mb-8">
          <StarLogo size={80} className="mx-auto" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">StarGuide</h2>
        <p className="text-gray-400 mb-8">powered by IDFS PathwayIQ™</p>
        <div className="flex justify-center">
          <div className="loading-spinner w-8 h-8"></div>
        </div>
        <p className="text-gray-500 mt-4">Initializing your learning universe...</p>
      </div>
    </div>
  );
};

export default LoadingScreen;
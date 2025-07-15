import React from 'react';
import IDFSLogo from './IDFSLogo';
import SikatAgencyLogo from './SikatAgencyLogo';

const LoadingScreen = () => {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-center">
        <div className="mb-8">
          <IDFSLogo size="xl" className="mx-auto mb-4" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">IDFS PathwayIQ™</h2>
        <div className="space-y-2">
          <p className="text-gray-400">powered by SikatLabs™</p>
          <SikatAgencyLogo size="medium" className="mx-auto" />
        </div>
        <div className="mt-6 text-xs text-gray-500">
          <p>© 2024 SikatLabs™ behind IDFS PathwayIQ™</p>
        </div>
        <div className="flex justify-center mt-6">
          <div className="loading-spinner w-8 h-8"></div>
        </div>
        <p className="text-gray-500 mt-4">Initializing your learning pathway...</p>
      </div>
    </div>
  );
};

export default LoadingScreen;
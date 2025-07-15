import React from 'react';
import IDFSLogo from './IDFSLogo';
import SikatAgencyLogo from './SikatAgencyLogo';

const RegisterBrandingSection = ({ size = 'medium', className = '' }) => {
  return (
    <div className={`flex flex-col items-center text-center space-y-4 ${className}`}>
      {/* ID Future Stars Logo - Above title */}
      <IDFSLogo size={size} />
      
      {/* Main title */}
      <div className="space-y-2">
        <h2 className="text-3xl font-bold text-white">Join IDFS PathwayIQ™</h2>
        <div className="space-y-2">
          <p className="text-gray-400">powered by SikatLabs™</p>
          {/* Sikat Agency Logo - Below SikatLabs text */}
          <SikatAgencyLogo size={size === 'large' ? 'medium' : 'small'} />
        </div>
      </div>
      
      {/* Copyright Notice */}
      <div className="mt-6 text-xs text-gray-500">
        <p>© 2024 SikatLabs™ behind IDFS PathwayIQ™</p>
      </div>
      
      {/* Additional Instructions */}
      <p className="mt-4 text-gray-300">Create your account and start your learning adventure</p>
    </div>
  );
};

export default RegisterBrandingSection;
import React from 'react';
import IDFSLogo from './IDFSLogo';
import SikatAgencyLogo from './SikatAgencyLogo';

const BrandingSection = ({ size = 'medium', className = '' }) => {
  return (
    <div className={`flex flex-col items-center text-center space-y-4 ${className}`}>
      {/* ID Future Stars Logo - Above title */}
      <IDFSLogo size={size} />
      
      {/* Main title */}
      <div className="space-y-2">
        <h2 className="text-3xl font-bold text-white">Welcome to IDFS PathwayIQ™</h2>
        <div className="space-y-1">
          <p className="text-gray-400">powered by SikatLabs™</p>
          {/* Sikat Agency Logo - Below SikatLabs text */}
          <SikatAgencyLogo size={size === 'large' ? 'medium' : 'small'} />
        </div>
      </div>
    </div>
  );
};

export default BrandingSection;
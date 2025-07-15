import React from 'react';
import IDFSLogo from './IDFSLogo';
import SikatAgencyLogo from './SikatAgencyLogo';

const CombinedBrandingLogo = ({ size = 'medium', layout = 'horizontal', className = '' }) => {
  const isHorizontal = layout === 'horizontal';
  
  return (
    <div className={`flex ${isHorizontal ? 'flex-row items-center space-x-3' : 'flex-col items-center space-y-2'} ${className}`}>
      {/* IDFS Logo */}
      <IDFSLogo size={size} />
      
      {/* Sikat Agency Logo */}
      <SikatAgencyLogo 
        size={size === 'large' ? 'medium' : 'small'} 
        className="opacity-80"
      />
    </div>
  );
};

export default CombinedBrandingLogo;
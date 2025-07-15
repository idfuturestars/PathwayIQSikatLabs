import React from 'react';

const SikatAgencyLogo = ({ size = 'small', className = '' }) => {
  const sizeClasses = {
    small: 'h-6 w-auto',
    medium: 'h-8 w-auto',
    large: 'h-10 w-auto'
  };

  return (
    <div className={`inline-flex items-center justify-center ${className}`}>
      {/* The Sikat Agency Logo - Using text styling matching the provided logo */}
      <div className={`${sizeClasses[size]} flex items-center justify-center`}>
        <span className="text-white font-normal text-sm tracking-wide">
          the Sikat Agency
        </span>
      </div>
    </div>
  );
};

export default SikatAgencyLogo;
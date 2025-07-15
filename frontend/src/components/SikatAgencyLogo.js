import React from 'react';

const SikatAgencyLogo = ({ size = 'small', className = '' }) => {
  const sizeClasses = {
    small: 'h-6 w-auto',
    medium: 'h-8 w-auto',
    large: 'h-10 w-auto'
  };

  return (
    <div className={`inline-flex items-center justify-center ${className}`}>
      {/* The Sikat Agency Logo - Recreating the actual logo design */}
      <div className={`${sizeClasses[size]} flex items-center justify-center`}>
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg px-3 py-1.5">
          <span className="text-white font-semibold text-sm tracking-wide">
            the Sikat Agency
          </span>
        </div>
      </div>
    </div>
  );
};

export default SikatAgencyLogo;
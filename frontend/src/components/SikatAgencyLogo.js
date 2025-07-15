import React from 'react';

const SikatAgencyLogo = ({ size = 'small', className = '' }) => {
  const sizeClasses = {
    small: 'h-6 w-6 text-xs',
    medium: 'h-8 w-8 text-sm',
    large: 'h-10 w-10 text-base'
  };

  return (
    <div className={`inline-flex items-center ${className}`}>
      <div className={`bg-white rounded-sm ${sizeClasses[size]} flex items-center justify-center font-bold text-black`}>
        Sí
      </div>
    </div>
  );
};

export default SikatAgencyLogo;
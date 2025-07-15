import React from 'react';

const IDFSLogo = ({ size = 'medium', className = '' }) => {
  const sizeClasses = {
    small: 'h-8 w-auto',
    medium: 'h-12 w-auto',
    large: 'h-16 w-auto',
    xl: 'h-20 w-auto'
  };

  return (
    <div className={`inline-flex items-center justify-center ${className}`}>
      {/* ID Future Stars Logo - Using CSS background for now, will be replaced with actual image */}
      <div className={`bg-black rounded-full px-4 py-2 ${sizeClasses[size]} flex items-center justify-center space-x-2`}>
        {/* Star Icon */}
        <svg 
          className="h-4 w-4 text-white" 
          fill="currentColor" 
          viewBox="0 0 24 24"
        >
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
        
        {/* ID FUTURE STARS Text */}
        <div className="text-white font-bold text-sm leading-tight">
          <div>ID FUTURE</div>
          <div>STARS</div>
        </div>
      </div>
    </div>
  );
};

export default IDFSLogo;
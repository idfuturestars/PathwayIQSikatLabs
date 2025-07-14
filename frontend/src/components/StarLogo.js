import React from 'react';

const StarLogo = ({ size = 32, className = '' }) => {
  return (
    <div className={`star-logo ${className}`} style={{ width: size, height: size }}>
      <svg 
        width={size} 
        height={size} 
        viewBox="0 0 100 100" 
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge> 
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        <path 
          d="M50 5 L60 35 L90 45 L60 55 L50 85 L40 55 L10 45 L40 35 Z" 
          fill="white" 
          stroke="#4CAF50" 
          strokeWidth="1"
          filter="url(#glow)"
        />
        <circle 
          cx="50" 
          cy="45" 
          r="8" 
          fill="#4CAF50" 
          opacity="0.8"
        />
      </svg>
    </div>
  );
};

export default StarLogo;
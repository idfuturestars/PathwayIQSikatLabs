import React from 'react';

const PathwayIQLogo = ({ size = 32, className = '' }) => {
  return (
    <div className={`pathwayiq-logo ${className}`} style={{ width: size, height: size }}>
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
          d="M20 20 L80 20 L80 50 L50 50 L50 80 L20 80 Z" 
          fill="white" 
          stroke="#ffffff" 
          strokeWidth="2"
          filter="url(#glow)"
        />
        <path 
          d="M30 30 L70 30 L70 40 L30 40 Z" 
          fill="#0a0a0a" 
          opacity="0.8"
        />
        <path 
          d="M30 50 L40 50 L40 70 L30 70 Z" 
          fill="#0a0a0a" 
          opacity="0.8"
        />
        <text 
          x="50" 
          y="95" 
          textAnchor="middle" 
          fill="white" 
          fontSize="8" 
          fontFamily="Inter, sans-serif"
        >
          IQ
        </text>
      </svg>
    </div>
  );
};

export default PathwayIQLogo;
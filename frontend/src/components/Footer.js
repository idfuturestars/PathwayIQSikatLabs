import React from 'react';
import CombinedBrandingLogo from './CombinedBrandingLogo';

const Footer = () => {
  return (
    <footer className="bg-gray-900 border-t border-gray-800 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center">
          {/* Logo and Branding */}
          <div className="flex items-center space-x-4 mb-6 md:mb-0">
            <CombinedBrandingLogo size="medium" layout="horizontal" />
            <div>
              <h3 className="text-white font-bold text-lg">IDFS PathwayIQ™</h3>
              <p className="text-gray-400 text-sm">powered by SikatLabs™</p>
            </div>
          </div>
          
          {/* Copyright */}
          <div className="text-center md:text-right">
            <p className="text-gray-400 text-sm">
              © 2024 ID Future Stars. All rights reserved.
            </p>
            <p className="text-gray-500 text-xs mt-1">
              Powered by SikatLabs™ Technology
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
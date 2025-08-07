import React from 'react';

interface WakiliLogoProps {
  size?: 'sm' | 'md' | 'lg';
  showTagline?: boolean;
  className?: string;
}

export default function WakiliLogo({ size = 'md', showTagline = true, className = '' }: WakiliLogoProps) {
  const sizeClasses = {
    sm: 'text-lg',
    md: 'text-2xl',
    lg: 'text-3xl'
  };

  const taglineSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  return (
    <div className={`flex items-center ${className}`}>
      {/* Logo Icon */}
      <div className="relative mr-3">
        <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center shadow-lg">
          <svg
            className="w-5 h-5 text-white"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </div>
        {/* Decorative dots */}
        <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-400 rounded-full"></div>
        <div className="absolute -bottom-1 -left-1 w-2 h-2 bg-indigo-400 rounded-full"></div>
      </div>

            {/* Text */}
      <div className="flex flex-col">
        <h1 className={`font-bold text-gray-900 ${sizeClasses[size]} flex items-center`}>
          Wakili
          {showTagline && (
            <span className={`text-blue-600 font-medium ${taglineSizeClasses[size]} ml-1`}>
              : A Quick One
            </span>
          )}
        </h1>
      </div>
    </div>
  );
}
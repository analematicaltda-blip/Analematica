import React from 'react';

const PrestadorCardSkeleton: React.FC = () => {
  return (
    <div className="border rounded-lg shadow-md animate-pulse h-full bg-white">
      <div className="w-full h-48 bg-gray-300 rounded-t-lg"></div>
      <div className="p-4 flex flex-col flex-grow">
        <div className="h-6 bg-gray-300 rounded w-3/4 mb-2"></div>
        <div className="h-4 bg-gray-300 rounded w-1/2 mb-4"></div>
        <div className="h-10 bg-gray-300 rounded w-full mt-auto"></div>
      </div>
    </div>
  );
};

export default PrestadorCardSkeleton;
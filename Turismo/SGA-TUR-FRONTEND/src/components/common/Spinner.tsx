import React from 'react';

export function Spinner({ text }: { text?: string }) {
  return (
    <div className="flex flex-col justify-center items-center gap-2">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      {text && <p className="text-sm text-gray-500">{text}</p>}
    </div>
  );
}
export default Spinner;

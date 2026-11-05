// frontend/src/components/ui/skeleton.tsx
import React from 'react';

export const Skeleton = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
    <div className={`animate-pulse rounded-md bg-gray-200 ${className}`} {...props} />
);

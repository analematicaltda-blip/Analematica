// frontend/src/components/ui/alert.tsx
import React from 'react';

export const Alert = ({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
    <div {...props} style={{ border: '1px solid red', padding: '1rem', margin: '1rem 0' }}>{children}</div>
);

export const AlertTitle = ({ children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h5 {...props} style={{ fontWeight: 'bold' }}>{children}</h5>
);

export const AlertDescription = ({ children, ...props }: React.HTMLAttributes<HTMLParagraphElement>) => (
    <p {...props}>{children}</p>
);

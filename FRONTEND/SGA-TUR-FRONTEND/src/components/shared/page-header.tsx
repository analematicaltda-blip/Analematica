import React from 'react';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  description?: string;
  children?: React.ReactNode;
}

export function PageHeader({ title, subtitle, description, children }: PageHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
        {(subtitle || description) && <p className="text-muted-foreground">{subtitle || description}</p>}
      </div>
      {children && <div className="flex items-center gap-4">{children}</div>}
    </div>
  );
}

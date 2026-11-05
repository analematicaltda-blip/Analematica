'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

const TabsContext = React.createContext<{
  defaultValue: string;
  value: string;
  setValue: (value: string) => void;
}>({
  defaultValue: '',
  value: '',
  setValue: () => {},
});

const Tabs = ({ defaultValue, children }: { defaultValue: string; children: React.ReactNode }) => {
  const [value, setValue] = React.useState(defaultValue);
  return (
    <TabsContext.Provider value={{ defaultValue, value, setValue }}>
      <div>{children}</div>
    </TabsContext.Provider>
  );
};

const TabsList = ({ children, className }: { children: React.ReactNode; className?: string }) => {
  return (
    <div className={cn('inline-flex h-10 items-center justify-center rounded-md bg-gray-100 p-1 text-gray-500', className)}>
      {children}
    </div>
  );
};

const TabsTrigger = ({ value, children }: { value: string; children: React.ReactNode }) => {
  const { value: activeValue, setValue } = React.useContext(TabsContext);
  const isActive = activeValue === value;
  return (
    <button
      onClick={() => setValue(value)}
      className={cn(
        'inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
        isActive ? 'bg-white text-gray-900 shadow-sm' : 'hover:bg-gray-200'
      )}
    >
      {children}
    </button>
  );
};

const TabsContent = ({ value, children }: { value: string; children: React.ReactNode }) => {
  const { value: activeValue } = React.useContext(TabsContext);
  return activeValue === value ? <div>{children}</div> : null;
};

export { Tabs, TabsList, TabsTrigger, TabsContent };

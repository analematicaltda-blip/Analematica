import React from 'react';

interface DialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
}

export const Dialog: React.FC<DialogProps> = ({ open = false, children }) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      {children}
    </div>
  );
};

export const DialogTrigger = ({ children, ...props }: React.HTMLAttributes<HTMLButtonElement>) => (
  <button {...props}>{children}</button>
);

export const DialogContent = ({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div {...props} className="bg-white rounded-2xl p-6 shadow-xl max-w-lg w-full relative z-10 border border-slate-200">
    {children}
  </div>
);

export const DialogHeader = ({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div {...props} className="mb-4">{children}</div>
);

export const DialogTitle = ({ children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
  <h2 {...props} className="text-xl font-bold text-slate-900">{children}</h2>
);

export const DialogDescription = ({ children, ...props }: React.HTMLAttributes<HTMLParagraphElement>) => (
  <p {...props} className="text-sm text-slate-500 mt-1">{children}</p>
);

export const DialogFooter = ({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div {...props} className="mt-6 flex justify-end gap-3">{children}</div>
);

export const DialogClose = ({ children, ...props }: React.HTMLAttributes<HTMLButtonElement>) => (
  <button {...props}>{children}</button>
);

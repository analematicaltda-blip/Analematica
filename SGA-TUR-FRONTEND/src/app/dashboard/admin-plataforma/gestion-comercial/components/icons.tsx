import React from 'react';

export const MessageIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
  </svg>
);

export const ReplyIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6-6m-6 6l6 6" />
  </svg>
);

export const MediaIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
  </svg>
);

export const CalendarIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
  </svg>
);

export const BotIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M12 6V3m0 18v-3m6-3h2M3 12h2m14 0h2M9 9l2 2 2-2M9 15l2-2 2 2" />
  </svg>
);

export const SparklesIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M19 3v4M17 5h4M14 11l-1.5 1.5L11 11l-1.5-1.5L11 8l1.5 1.5L14 11zm7 7l-1.5 1.5L18 18l-1.5-1.5L18 15l1.5 1.5zM5 19v-4M3 17h4M19 19v-4M17 17h4" />
  </svg>
);

export const LoadingSpinner = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
  <svg className={`animate-spin ${className}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" {...rest}>
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
);

export const CalendarPlusIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2zM12 11v4m-2-2h4" />
    </svg>
);

export const CogIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924-1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066 2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
);

export const TrendingUpIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
  </svg>
);

export const MegaphoneIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-2.236 9.168-5.518" />
  </svg>
);

export const ChartBarIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
  </svg>
);

export const ChevronDoubleLeftIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
    </svg>
);

export const ChevronDoubleRightIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
    </svg>
);

export const BellIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
    </svg>
);

export const UserCircleIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9 9 0 100-18 9 9 0 000 18z" />
    </svg>
);

export const MenuIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
    </svg>
);

export const AnalyticsIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
  </svg>
);

export const MailIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
  </svg>
);

export const SmsIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
  </svg>
);

export const MmsIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
  </svg>
);

export const WhatsAppIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}>
    <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.487 5.235 3.487 8.413.003 6.557-5.338 11.892-11.894 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.886-.001 2.269.655 4.512 1.907 6.344l-1.495 5.454 5.57-1.45zM12.012 5.99c-3.326 0-6.031 2.703-6.031 6.028 0 1.403.523 2.62 1.39 3.612l.142.213-1.037 3.793 3.876-1.018.192.115c.968.581 2.053.929 3.18.929 3.325 0 6.031-2.703 6.031-6.028s-2.706-6.028-6.031-6.028zm0 10.632c-.989 0-1.943-.248-2.79-.705l-1.964.515 2.001-1.932a4.613 4.613 0 0 1-1.09-2.793c0-2.529 2.055-4.582 4.584-4.582 2.528 0 4.583 2.054 4.583 4.582 0 2.529-2.055 4.582-4.583 4.582z" />
  </svg>
);

export const FacebookIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}>
    <path d="M9 8h-3v4h3v12h5v-12h3.642l.358-4h-4v-1.667c0-.955.192-1.333 1.115-1.333h2.885v-5h-3.808c-3.596 0-5.192 1.583-5.192 4.615v2.385z" />
  </svg>
);

export const InstagramIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}>
    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.85s-.011 3.584-.069 4.85c-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07s-3.584-.012-4.85-.07c-3.252-.148-4.771-1.691-4.919-4.919-.058-1.265-.069-1.645-.069-4.85s.011-3.584.069-4.85c.149-3.225 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.85-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948s.014 3.667.072 4.947c.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072s3.667-.014 4.947-.072c4.358-.2 6.78-2.618 6.98-6.98.059-1.281.073-1.689.073-4.948s-.014-3.667-.072-4.947c-.2-4.358-2.618-6.78-6.98-6.98-1.281-.058-1.689-.072-4.948-.072zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.162 6.162 6.162 6.162-2.759 6.162-6.162-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4s1.791-4 4-4 4 1.79 4 4-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44 1.441-.645 1.441-1.44c0-.795-.645-1.44-1.441-1.44z" />
  </svg>
);

export const XIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 16 16" {...rest}>
    <path d="M12.6.75h2.454l-5.36 6.142L16 15.25h-4.937l-3.867-5.07-4.425 5.07H.316l5.733-6.57L0 .75h5.063l3.495 4.633L12.601.75Zm-.86 13.028h1.36L4.323 2.145H2.865l8.875 11.633Z" />
  </svg>
);

export const TikTokIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}>
    <path d="M12.525.02c1.31-.02 2.61-.01 3.91.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-1.06-.63-1.9-1.48-2.5-2.51-.86-1.49-1.11-3.29-1.01-5.11.12-2.02 1.09-3.86 2.62-5.16 1.66-1.4 3.84-2.12 6.04-1.99.09 2.15-.02 4.3.02 6.46-.03 1.14-.37 2.24-1.02 3.15-.79 1.09-2.01 1.8-3.34 1.87-1.12.06-2.22-.32-3.04-1.01-.64-.54-1.06-1.26-1.23-2.09-.12-1.05.02-2.17.43-3.15.53-1.27 1.44-2.31 2.6-2.99.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-1.06-.63-1.9-1.48-2.5-2.51-.86-1.49-1.11-3.29-1.01-5.11.12-2.02 1.09-3.86 2.62-5.16 1.66-1.4 3.84-2.12 6.04-1.99.09 2.15-.02 4.3.02 6.46-.03 1.14-.37 2.24-1.02 3.15-.79 1.09-2.01 1.8-3.34 1.87-1.12.06-2.22-.32-3.04-1.01-.64-.54-1.06-1.26-1.23-2.09-.12-1.05.02-2.17.43-3.15.53-1.27 1.44-2.31 2.6-2.99.53-1.02 1.2-1.94 2-2.73.57-.55 1.19-1.06 1.85-1.48.6-.38 1.25-.69 1.92-.9.01 2.91-.01 5.83.02 8.74z" />
  </svg>
);

export const YouTubeIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}>
    <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z" />
  </svg>
);

export const TwitchIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}>
    <path d="M2.149 0l-2.149 4.77v14.456h5.332v3.58h2.801l3.572-3.58h4.468l7.98-7.98v-11.246h-22.004zm18.983 10.395l-3.572 3.572h-5.913l-3.572 3.58v-3.58h-4.468v-12.21h17.525v8.638zm-4.468-5.06h2.246v5.332h-2.246v-5.332zm-5.332 0h2.246v5.332h-2.246v-5.332z" />
  </svg>
);

export const CheckCircleIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

export const XCircleIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

export const GlobeAltIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9V3m0 18a9 9 0 009-9m-9 9a9 9 0 00-9-9" />
    </svg>
);

export const TemplateIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 6a2 2 0 012-2h12a2 2 0 012 2v12a2 2 0 01-2-2H6a2 2 0 01-2-2V6zM10 9h4m-4 4h4m-4 4h4M6 9h.01M6 13h.01M6 17h.01" />
    </svg>
);

export const SaveIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
    </svg>
);

export const DuplicateIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
);

// FIX: Added PencilIcon to resolve missing icon error.
export const PencilIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L15.232 5.232z" />
    </svg>
);

export const CodeBracketIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
    </svg>
);

export const PlusCircleIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

export const TrashIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
);

export const XMarkIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
);

export const PostIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
);

export const StoryIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

export const ReelIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
    </svg>
);

export const EuroIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.121 15.536A9.004 9.004 0 0112 15c-2.435 0-4.665-.92-6.364-2.464M12 9v6M10 12h4" />
     <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18.364 5.636a9 9 0 11-12.728 0 9 9 0 0112.728 0z"></path>
  </svg>
);

export const UsersIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm6-11a4 4 0 11-8 0 4 4 0 018 0z" />
  </svg>
);

export const ClipboardListIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
  </svg>
);

export const PipelineIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
  </svg>
);

export const DashboardIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
  </svg>
);

export const ContactsIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
  </svg>
);


export const PlusIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
  </svg>
);

export const SearchIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
);

export const PhoneIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
  </svg>
);

export const BriefcaseIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
  </svg>
);

export const AlertTriangleIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
  </svg>
);

export const LinkedInIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}>
    <path d="M4.98 3.5c0 1.381-1.11 2.5-2.48 2.5s-2.48-1.119-2.48-2.5c0-1.38 1.11-2.5 2.48-2.5s2.48 1.12 2.48 2.5zm.02 4.5h-5v16h5v-16zm7.982 0h-4.98v16h4.98v-8.396c0-2.002 1.808-3.628 3.982-3.628 2.175 0 3.998 1.583 3.998 3.585v8.439h5v-8.542c0-4.71-3.025-8.458-7.996-8.458-3.728 0-5.996 2.083-5.996 4.93z" />
  </svg>
);

export const TargetIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
    </svg>
);

export const FormIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
    </svg>
);

export const SupportIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
);

export const BookOpenIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
    </svg>
);

export const ChatBubbleLeftRightIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
);

export const KanbanIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
    </svg>
);

export const ListIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
    </svg>
);

export const TicketIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
    </svg>
);

export const HourglassIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

export const PaperAirplaneIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
    </svg>
);

export const ArchiveBoxIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
    </svg>
);

export const HeartIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 010 6.364L12 20.364l7.682-7.682a4.5 4.5 0 01-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 01-6.364 0z" />
    </svg>
);

export const SendGridIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
);

export const TwilioIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
);

export const ReactIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="-11.5 -10.23174 23 20.46348" fill="none" stroke="currentColor" strokeWidth="1" {...rest}>
      <circle cx="0" cy="0" r="2.05" />
      <g>
        <ellipse rx="11" ry="4.2"/>
        <ellipse rx="11" ry="4.2" transform="rotate(60)"/>
        <ellipse rx="11" ry="4.2" transform="rotate(120)"/>
      </g>
    </svg>
);

export const PostgresIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
        <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
        <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
    </svg>
);

export const GoogleIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 48 48" {...rest}>
        <path fill="#FFC107" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12c0-6.627,5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24c0,11.045,8.955,20,20,20c11.045,0,20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"/>
        <path fill="#FF3D00" d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"/>
        <path fill="#4CAF50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.222,0-9.641-3.657-11.283-8.581l-6.522,5.025C9.505,39.556,16.227,44,24,44z"/>
        <path fill="#1976D2" d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.574l6.19,5.238C39.99,35.458,44,30.138,44,24C44,22.659,43.862,21.35,43.611,20.083z"/>
    </svg>
);

export const PinterestIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}>
        <path d="M12 0c-6.627 0-12 5.372-12 12 0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 .992.371 1.938.82 2.452l-1.464 5.922c-.254 1.006-.998 2.348-1.442 3.193.916.287 1.889.444 2.898.444 6.627 0 12-5.373 12-12s-5.373-12-12-12z" />
    </svg>
);

export const SnapchatIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}>
        <path d="M12 2c-5.523 0-10 4.477-10 10s4.477 10 10 10c.83 0 1.5-.67 1.5-1.5s-.67-1.5-1.5-1.5c-3.866 0-7-3.134-7-7s3.134-7 7-7 7 3.134 7 7-3.134 7-7 7c-.83 0-1.5.67-1.5 1.5s.67 1.5 1.5 1.5c5.523 0 10-4.477 10-10s-4.477-10-10-10zm-2 10.5c-.828 0-1.5.672-1.5 1.5s.672 1.5 1.5 1.5 1.5-.672 1.5-1.5-.672-1.5-1.5-1.5zm4 0c-.828 0-1.5.672-1.5 1.5s.672 1.5 1.5 1.5 1.5-.672 1.5-1.5-.672-1.5-1.5-1.5z" />
    </svg>
);

export const TelegramIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}>
        <path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm7.643 7.258l-2.316 10.838c-.144.667-.533.82-1.082.513l-3.535-2.6-1.71 1.648c-.19.19-.356.355-.71.355-.544 0-.488-.233-.672-.753l-1.258-4.125-3.87-1.204c-.66-.206-.666-.658.113-.974l12.774-4.84c.563-.213 1.082.138.895.83z" />
    </svg>
);

export const ZoomIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}>
        <path d="M12 2c-5.523 0-10 4.477-10 10s4.477 10 10 10 10-4.477 10-10-4.477-10-10-10zm-1.5 6h3c.828 0 1.5.672 1.5 1.5s-.672 1.5-1.5 1.5h-3c-.828 0-1.5-.672-1.5-1.5s.672-1.5 1.5-1.5zm-2.5 4h8c.828 0 1.5.672 1.5 1.5s-.672 1.5-1.5 1.5h-8c-.828 0-1.5-.672-1.5-1.5s.672-1.5 1.5-1.5zm1.5 4h5c.828 0 1.5.672 1.5 1.5s-.672 1.5-1.5 1.5h-5c-.828 0-1.5-.672-1.5-1.5s.672-1.5 1.5-1.5z" />
    </svg>
);

export const TeamsIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}>
        <path d="M12 2c-5.523 0-10 4.477-10 10s4.477 10 10 10 10-4.477 10-10-4.477-10-10-10zm-1 5h2v12h-2v-12zm-4 4h2v8h-2v-8zm8 0h2v8h-2v-8z" />
    </svg>
);

export const StarIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}>
        <path d="M12 .587l3.668 7.568 8.332 1.151-6.064 5.828 1.48 8.279-7.416-3.967-7.417 3.967 1.481-8.279-6.064-5.828 8.332-1.151z" />
    </svg>
);

export const InvoiceIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
);

export const SapIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}><path d="M2.33 0h19.339v24h-19.34zm2.593 2.534v8.13h8.13v-8.13zm9.585 0v18.933h6.56v-18.933z" /></svg>
);

export const QuickbooksIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}><path d="M12 24c6.627 0 12-5.373 12-12s-5.373-12-12-12-12 5.373-12 12 5.373 12 12 12zm0-19.5c4.142 0 7.5 3.358 7.5 7.5s-3.358 7.5-7.5 7.5-7.5-3.358-7.5-7.5 3.358-7.5 7.5-7.5zm-3.141 6.551c-.699.278-1.048.818-1.048 1.458v.099c0 .64.349 1.18 1.048 1.458l3.141 1.258c.699.278 1.048.818 1.048 1.458v.099c0 .64-.349 1.18-1.048 1.458l-3.952 1.579c-1.111.444-1.859.185-1.859-1.01v-6.307c0-1.195.748-1.454 1.859-1.01zm6.282 0c-.699.278-1.048.818-1.048 1.458v.099c0 .64.349 1.18 1.048 1.458l3.141 1.258c.699.278 1.048.818 1.048 1.458v.099c0 .64-.349 1.18-1.048 1.458l-3.952 1.579c-1.111.444-1.859.185-1.859-1.01v-6.307c0-1.195.748-1.454 1.859-1.01z" /></svg>
);

export const ShopifyIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}><path d="M12.632 3.924c-2.262 0-3.987 1.242-4.992 2.304-.522.553-1.002 1.242-1.34 1.812l1.393.81c.216-.402.585-.9 1.01-1.386.918-.945 2.223-1.848 3.928-1.848 1.458 0 2.51.621 2.51 1.812 0 .864-.531 1.458-1.83 2.016l-3.486 1.485c-2.736 1.161-4.254 2.655-4.254 5.256 0 2.271 1.575 3.87 3.879 3.87 2.034 0 3.513-1.053 4.545-2.07l-1.35-1.01c-.342.36-.909.846-1.539.846-.666 0-1.146-.423-1.146-1.08 0-.756.558-1.224 1.773-1.746l3.486-1.485c2.934-1.251 4.347-2.793 4.347-5.325.001-2.673-1.926-4.545-5.01-4.545zm-1.701 19.347h-10.931l1.83-5.265h10.931z" /></svg>
);

export const FileExportIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
);

export const ShieldCheckIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 20.944a11.955 11.955 0 019-4.944c3.396 0 6.425 1.255 8.618 3.322" />
    </svg>
);

export const AppStoreIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}><path d="M12.164 2.808c-1.42-.047-3.324.936-4.22 2.56-1.04 1.868-.696 4.385.64 5.86.924.968 2.373 1.59 3.805 1.543 1.52-.047 2.94-1.03 3.824-1.955-1.45-.968-2.333-2.65-2.07-4.384.28-1.868 1.63-3.19 2.9-3.62zm-3.824 10.375c-.28 3.033 2.122 4.21 2.373 4.256.12.023.237.047.373.047.18 0 .42-.047.534-.093.28-.112 2.585-1.282 2.48-4.522-.047-1.442-.64-2.843-1.63-3.806-1.08-1.053-2.63-1.702-4.13-1.543-.1.002-.19.002-.28.002-2.14 0-3.64 1.485-3.64 3.665 0 1.955 1.15 3.056 2.33 3.62l.14.07zm3.64-12.87c3.96 0 6.67 2.918 6.67 6.897 0 4.14-2.88 7.01-6.9 7.01-4.01 0-6.66-2.868-6.66-6.92 0-3.99 2.7-6.987 6.89-6.987z" /></svg>
);

export const GooglePlayIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" {...rest}><path d="M12 24c6.627 0 12-5.373 12-12s-5.373-12-12-12-12 5.373-12 12 5.373 12 12 12zm-3.513-17.342l8.837 5.09-6.89 4.237-1.947-8.327zm.33 13.626l-1.464-1.432 4.237-3.666 4.88 2.808-7.653 2.29zm8.568-7.234l-5.06-2.915.012 11.758 5.048-5.141z" /></svg>
);

export const FunnelIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2a1 1 0 01-.293.707L16 11.414V16l-4 2v-6.586L3.293 6.707A1 1 0 013 6V4z" />
    </svg>
);

export const WorkflowIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12s-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
    </svg>
);

export const LinkIcon = ({ className = 'w-6 h-6', ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
  </svg>
);

export const VideoCameraIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
);

export const CursorArrowRaysIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15.042 21.672L13.684 16.6m0 0l-2.51 2.225.569-2.474m0 0L3.272 7.246l6.584 2.345L12.028 3.272l3.014 8.4m0 0l2.225-2.51.569 2.474m0 0l2.474.569-2.225 2.51m0 0l-8.4-3.014 2.345-6.584 7.246 3.272" />
    </svg>
);

export const ChevronRightIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
    </svg>
);
export const LightBulbIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    </svg>
);

export const RocketLaunchIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
       <path strokeLinecap="round" strokeLinejoin="round" d="M15.59 14.37a6 6 0 01-5.84 7.38v-4.82m5.84-2.56a14.95 14.95 0 00-5.84-2.56m0 0a14.95 14.95 0 00-5.84 2.56m5.84-2.56V4.72a6 6 0 0112 0v2.65a6 6 0 01-12 0v0z" />
    </svg>
);

export const ChevronUpIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M5 15l7-7 7 7" />
    </svg>
);

export const ChevronDownIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
    </svg>
);

export const UserGroupIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.653-.084-1.282-.24-1.88M9 4a4 4 0 100 8 4 4 0 000-8zM15 8a4 4 0 10-8 0 4 4 0 008 0z" />
  </svg>
);

export const TagIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M7 7h.01M7 3h5a2 2 0 012 2v5a2 2 0 01-2 2H7a2 2 0 01-2-2V5a2 2 0 012-2z" />
    </svg>
);

export const EyeIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
);

export const EyeSlashIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878l-1.49 1.49m6.02-6.02l1.49-1.49M21 12a9.97 9.97 0 00-2.458-5.385M3 12a9.97 9.97 0 012.458-5.385" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 3l18 18" />
    </svg>
);

export const DevicePhoneMobileIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 1.5H8.25A2.25 2.25 0 006 3.75v16.5a2.25 2.25 0 002.25 2.25h7.5A2.25 2.25 0 0018 20.25V3.75a2.25 2.25 0 00-2.25-2.25H13.5m-3 0V3h3V1.5m-3 0h3m-3 18.75h3" />
    </svg>
);

export const DeviceTabletIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5h3m-6.75 2.25h10.5a2.25 2.25 0 002.25-2.25v-15a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 4.5v15a2.25 2.25 0 002.25 2.25z" />
    </svg>
);

export const ComputerDesktopIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25A2.25 2.25 0 015.25 3h13.5A2.25 2.25 0 0121 5.25z" />
    </svg>
);

export const PaintBrushIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.47 2.118 2.25 2.25 0 01-2.47-2.118c0-.62.28-1.22.755-1.634m12.062-1.128a3 3 0 01-5.78 1.128 2.25 2.25 0 00-2.47 2.118 2.25 2.25 0 00-2.47-2.118c0-.62.28-1.22.755-1.634m12.062 1.128a3 3 0 00-5.78-1.128 2.25 2.25 0 01-2.47-2.118 2.25 2.25 0 012.47-2.118c.62 0 1.22-.28 1.634-.755m-12.062-1.128a3 3 0 01-5.78-1.128 2.25 2.25 0 00-2.47-2.118 2.25 2.25 0 002.47 2.118c.62 0 1.22.28 1.634.755m12.062 1.128a3 3 0 005.78 1.128 2.25 2.25 0 012.47-2.118 2.25 2.25 0 012.47 2.118c0 .62-.28 1.22-.755 1.634m-16.5-1.634a3 3 0 015.78 1.128 2.25 2.25 0 002.47-2.118 2.25 2.25 0 00-2.47 2.118c.62 0 1.22.28 1.634.755" />
    </svg>
);

export const Cog6ToothIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.438.995s.145.755.438.995l1.003.827c.424.35.534.954.26 1.431l-1.296 2.247a1.125 1.125 0 01-1.37.49l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.063-.374-.313-.686-.645-.87a6.52 6.52 0 01-.22-.127c-.324-.196-.72-.257-1.075-.124l-1.217.456a1.125 1.125 0 01-1.37-.49l-1.296-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.437-.995s-.145-.755-.437-.995l-1.004-.827a1.125 1.125 0 01-.26-1.431l1.296-2.247a1.125 1.125 0 011.37-.49l1.217.456c.355.133.75.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.213-1.28z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
);

export const CheckIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
);

export const QuestionMarkCircleIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

export const ChevronLeftIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
    </svg>
);

export const ShoppingCartIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
    </svg>
);

export const LayersIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9.75l-9-5.25m0 0l9 5.25m9-5.25l-9 5.25" />
    </svg>
);

export const BeakerIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547a2 2 0 00-.547 1.806l.477 2.387a6 6 0 00.517 3.86l.158.318a6 6 0 00.517 3.86l2.387.477a2 2 0 001.806-.547a2 2 0 00.547-1.806l-.477-2.387a6 6 0 00-.517-3.86l-.158-.318a6 6 0 00-.517-3.86l-.477-2.387a2 2 0 00-.547-1.806z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M20.655 8.345l-3.321-3.321a2 2 0 00-2.828 0l-3.321 3.321a2 2 0 000 2.828l3.321 3.321a2 2 0 002.828 0l3.321-3.321a2 2 0 000-2.828z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9.5l3.5 3.5" />
    </svg>
);

export const CreditCardIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
    </svg>
);

export const ServerIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
    </svg>
);

export const BookmarkIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
    </svg>
);

export const HomeIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
    </svg>
);

export const KeyIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17.5a2 2 0 01-2.828 0L7 16.25m0 0l-3.379-3.38a2 2 0 010-2.828L7 6.25m0 10l-3-3m0 0a2 2 0 010-2.828l3-3m0 0a2 2 0 012.828 0l3 3m0 0a2 2 0 010 2.828l-3 3z" />
    </svg>
);
export const ArrowsUpDownIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 7.5L7.5 3m0 0L12 7.5M7.5 3v13.5m13.5 0L16.5 21m0 0L12 16.5m4.5 4.5V7.5" />
    </svg>
);

export const ClockIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

export const AcademicCapIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path d="M12 14l9-5-9-5-9 5 9 5z" />
        <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 14l9-5-9-5-9 5 9 5zm0 0v9" />
    </svg>
);

export const BuildingStorefrontIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
    </svg>
);

export const PhotoIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
    </svg>
);

export const ChatBubbleBottomCenterTextIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193l-3.72 3.72a.75.75 0 01-1.06 0l-3.72-3.72C9.447 17.5 8.25 16.536 8.25 15.397V11.5c0-.97.616-1.813 1.5-2.097m6.75 0c.22.08.44.18.66.312m-6.75 0c-.22.08-.44.18-.66.312m0 0l.556 2.378a3.375 3.375 0 006.128 0l.556-2.378m0 0c.22-.08.44-.18.66-.312m-13.5 0c-.22.08-.44.18-.66.312m0 0c-1.14.54-2.016 1.5-2.516 2.653V11.5c0-1.136.847-2.1 1.98-2.193l3.72-3.72a.75.75 0 011.06 0l3.72 3.72C14.553 6.5 15.75 7.464 15.75 8.603V11.5" />
    </svg>
);

export const CalendarDaysIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0h18M9.75 14.25h.008v.008h-.008V14.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm3 0h.008v.008h-.008V14.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm3 0h.008v.008h-.008V14.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zM9.75 18h.008v.008h-.008V18zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm3 0h.008v.008h-.008V18zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm3 0h.008v.008h-.008V18zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
    </svg>
);
export const ShareIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M7.217 10.907a2.25 2.25 0 100 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186l9.566-5.314m-9.566 7.5l9.566 5.314m0 0a2.25 2.25 0 103.935 2.186 2.25 2.25 0 00-3.935-2.186zm0-12.814a2.25 2.25 0 103.933-2.186 2.25 2.25 0 00-3.933 2.186z" />
    </svg>
);
export const SwatchIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.47 2.118 2.25 2.25 0 01-2.47-2.118c0-.62.28-1.22.755-1.634m12.062-1.128a3 3 0 01-5.78 1.128 2.25 2.25 0 00-2.47 2.118 2.25 2.25 0 00-2.47-2.118c0-.62.28-1.22.755-1.634m12.062 1.128a3 3 0 00-5.78-1.128 2.25 2.25 0 01-2.47-2.118 2.25 2.25 0 012.47-2.118c.62 0 1.22-.28 1.634-.755m-12.062-1.128a3 3 0 01-5.78-1.128 2.25 2.25 0 00-2.47-2.118 2.25 2.25 0 002.47 2.118c.62 0 1.22.28 1.634.755m12.062 1.128a3 3 0 005.78 1.128 2.25 2.25 0 012.47-2.118 2.25 2.25 0 012.47 2.118c0 .62-.28 1.22-.755 1.634m-16.5-1.634a3 3 0 015.78 1.128 2.25 2.25 0 002.47-2.118 2.25 2.25 0 00-2.47 2.118c.62 0 1.22.28 1.634.755" />
    </svg>
);
export const CodeBracketSquareIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M14.25 9.75L16.5 12l-2.25 2.25m-4.5 0L7.5 12l2.25-2.25M6 20.25h12A2.25 2.25 0 0020.25 18V5.75A2.25 2.25 0 0018 3.5H6A2.25 2.25 0 003.75 5.75v12.5A2.25 2.25 0 006 20.25z" />
    </svg>
);
export const SitemapIcon = ({ className = "w-6 h-6", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 12.75V19.5m0 0a2.25 2.25 0 01-2.25 2.25H9.75A2.25 2.25 0 017.5 19.5V12.75m0 0V8.25a2.25 2.25 0 012.25-2.25h3a2.25 2.25 0 012.25 2.25v4.5M3.75 12.75h.008v.008H3.75v-.008zm16.5 0h.008v.008h-.008v-.008z" />
    </svg>
);

export const GripVerticalIcon = ({ className = "w-5 h-5", ...rest }: { className?: string, [key: string]: any }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} {...rest}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l0 14" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 5l0 14" />
    </svg>
);
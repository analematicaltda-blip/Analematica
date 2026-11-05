// src/components/Providers.tsx
"use client";

import { AuthProvider } from "@/contexts/AuthContext";
import { EntityProvider } from "@/contexts/EntityContext";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { AgentProvider } from "@/contexts/AgentContext";
import { usePathname } from 'next/navigation';
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import Chatbot from '@/components/shared/Chatbot';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function Providers({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isDashboard = pathname.includes('/dashboard');

  return (
    <AuthProvider>
      <EntityProvider>
        <LanguageProvider>
          <AgentProvider>
            {!isDashboard && <Header />}
            <main className={`flex-grow flex flex-col ${!isDashboard ? '' : 'h-full'}`}>
              {children}
            </main>
            {!isDashboard && (
              <>
                <Footer />
                <Chatbot />
              </>
            )}
            <ToastContainer position="bottom-right" autoClose={5000} theme="light" />
          </AgentProvider>
        </LanguageProvider>
      </EntityProvider>
    </AuthProvider>
  );
}

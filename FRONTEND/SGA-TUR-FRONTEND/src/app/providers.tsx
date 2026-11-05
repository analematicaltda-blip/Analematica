'use client';

import { ReactNode } from 'react';
import { AuthProvider } from '@/contexts/AuthContext';
import { EntityProvider } from '@/contexts/EntityContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { DashboardProvider } from '@/contexts/DashboardContext';
import { GRCProvider } from '@/contexts/GRCContext';
import { MSWProvider } from '@/components/MSWProvider';
import { SecurityShield } from '@/components/common/SecurityShield';
import { SecurityProvider } from '@/contexts/SecurityContext';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

type Props = {
  children: ReactNode;
};

export function Providers({ children }: Props) {
  return (
    <ThemeProvider>
      <MSWProvider>
        <DashboardProvider>
          <GRCProvider>
            <EntityProvider>
              <AuthProvider>
                <SecurityProvider>
                  <SecurityShield>
                    {children}
                  </SecurityShield>
                </SecurityProvider>
          <ToastContainer
          position="top-right"
          autoClose={5000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
          theme="light"
        />
              </AuthProvider>
            </EntityProvider>
          </GRCProvider>
        </DashboardProvider>
      </MSWProvider>
    </ThemeProvider>
  );
}

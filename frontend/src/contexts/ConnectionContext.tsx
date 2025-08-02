// frontend/src/contexts/ConnectionContext.tsx
/**
 * 连接状态全局上下文
 * 让所有组件都能感知和更新连接状态
 */

import React, { createContext, useContext, useState, useCallback } from 'react';

type ConnectionStatus = 'checking' | 'connected' | 'disconnected' | 'error';

interface ConnectionContextType {
  status: ConnectionStatus;
  lastCheck: Date;
  setStatus: (status: ConnectionStatus) => void;
  triggerCheck: () => void;
}

const ConnectionContext = createContext<ConnectionContextType | undefined>(undefined);

export const ConnectionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [status, setStatus] = useState<ConnectionStatus>('checking');
  const [lastCheck, setLastCheck] = useState<Date>(new Date());

  const updateStatus = useCallback((newStatus: ConnectionStatus) => {
    setStatus(newStatus);
    setLastCheck(new Date());
  }, []);

  const triggerCheck = useCallback(() => {
    // Trigger check logic can be implemented here
  }, []);

  return (
    <ConnectionContext.Provider value={{
      status,
      lastCheck,
      setStatus: updateStatus,
      triggerCheck
    }}>
      {children}
    </ConnectionContext.Provider>
  );
};

export const useConnection = () => {
  const context = useContext(ConnectionContext);
  if (context === undefined) {
    throw new Error('useConnection must be used within a ConnectionProvider');
  }
  return context;
};
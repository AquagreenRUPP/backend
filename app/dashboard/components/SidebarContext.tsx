"use client";

import { createContext, useContext, useState, ReactNode } from "react";

// Create Context
const SidebarContext = createContext<{
  sidebarWidth: number;
  setSidebarWidth: (width: number) => void;
}>({
  sidebarWidth: 200, // Default width
  setSidebarWidth: () => {}, // Default setter
});

// Sidebar Provider
export const SidebarProvider = ({ children }: { children: ReactNode }) => {
  const [sidebarWidth, setSidebarWidth] = useState<number>(300);

  return (
    <SidebarContext.Provider value={{ sidebarWidth, setSidebarWidth }}>
      {children}
    </SidebarContext.Provider>
  );
};

// Hook to Use Sidebar Context
export const useSidebar = () => useContext(SidebarContext);

"use client";

import { useSidebar } from "./SidebarContext";

export default function Main({ children }: { children: React.ReactNode }) {
  const { sidebarWidth } = useSidebar();

  return (
    <main
      className="p-4 bg-white"
      style={{
        marginLeft: `${sidebarWidth}px`, // Adjust margin dynamically
        marginTop: "64px", // Adjust based on header height if fixed
      }}
    >
      {children}
    </main>
  );
}

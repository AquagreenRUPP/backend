"use client";

import { useSidebar } from "./SidebarContext";

export default function Header() {
  const { sidebarWidth } = useSidebar();

  return (
    <header
      className="bg-gray-100 shadow-md p-4 fixed top-0"
      style={{ marginLeft: `${sidebarWidth}px` }}
    >
      <h1 className="text-2xl font-bold">Header</h1>
    </header>
  );
}

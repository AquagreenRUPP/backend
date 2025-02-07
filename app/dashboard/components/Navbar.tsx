"use client";

import { useEffect, useState } from "react";

interface NavbarProps {
  setActivePage: (page: string) => void;
  setSidebarWidth: (width: number) => void;
  sidebarWidth: number;
}

export default function Navbar({
  setActivePage,
  setSidebarWidth,
  sidebarWidth,
}: NavbarProps) {
  const [isResizing, setIsResizing] = useState(false);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isResizing) {
        const newWidth = Math.min(Math.max(e.clientX, 200), 500); // Restrict width
        setSidebarWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };

    if (isResizing) {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
    }

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isResizing, setSidebarWidth]);

  return (
    <div
      className={`fixed top-0 left-0 h-screen bg-gray-800 text-white shadow-lg flex flex-col ${
        isResizing ? "" : "transition-all duration-300"
      }`}
      style={{ width: `${sidebarWidth}px` }}
    >
      <h2 className="text-xl font-bold p-4">Navigation</h2>
      <ul className="space-y-2 p-4">
        <li>
          <button
            onClick={() => setActivePage("addProduct")}
            className="w-full text-left hover:bg-gray-700 p-2 rounded"
          >
            បន្ថែមផលិតផល
          </button>
        </li>
        <li>
          <button
            onClick={() => setActivePage("buySell")}
            className="w-full text-left hover:bg-gray-700 p-2 rounded"
          >
            កត់ត្រាការលក់និងទិញ
          </button>
        </li>
        <li>
          <button
            onClick={() => setActivePage("recordSellBuy")}
            className="w-full text-left hover:bg-gray-700 p-2 rounded"
          >
            រុករកការកត់ត្រាលក់និងទិញ
          </button>
        </li>
        <li>
          <button
            onClick={() => setActivePage("recordPawn")}
            className="w-full text-left hover:bg-gray-700 p-2 rounded"
          >
            កត់ត្រាការបញ្ចាំ
          </button>
        </li>
        <li>
          <button
            onClick={() => setActivePage("searchPawn")}
            className="w-full text-left hover:bg-gray-700 p-2 rounded"
          >
            រុករកការបញ្ចាំ
          </button>
        </li>
      </ul>
      <div
        className="absolute top-0 right-0 h-full w-2 bg-gray-600 cursor-ew-resize"
        onMouseDown={() => setIsResizing(true)}
      />
    </div>
  );
}
  
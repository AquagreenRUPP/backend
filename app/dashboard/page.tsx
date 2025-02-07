"use client";

import { useState } from "react";
import Navbar from "./components/Navbar";
import AddProduct from "./components/pages/addProduct";
import BuySell from "./components/pages/buySell";
import RecordSellBuy from "./components/pages/recordSellBuy";
import RecordPawn from "./components/pages/recordPawn";
import SearchPawn from "./components/pages/searchPawn";
import "../globals.css";

export default function Dashboard() {
  const [activePage, setActivePage] = useState<string>("addProduct");
  const [sidebarWidth, setSidebarWidth] = useState<number>(200);

  // Render the current active page dynamically
  const renderPage = () => {
    switch (activePage) {
      case "addProduct":
        return <AddProduct />;
      case "buySell":
        return <BuySell />;
      case "recordSellBuy":
        return <RecordSellBuy />;
      case "recordPawn":
        return <RecordPawn />;
      case "searchPawn":
        return <SearchPawn />;
      default:
        return (
          <div className="p-4 text-gray-600">
            Please select a page from the sidebar.
          </div>
        );
    }
  };

  return (
    <div className="flex h-screen">
      {/* Navigation Sidebar */}
      <Navbar
        setActivePage={setActivePage}
        setSidebarWidth={setSidebarWidth}
        sidebarWidth={sidebarWidth}
      />

      {/* Main Content Area */}
      <div
        className="flex-1 p-4 overflow-auto"
        style={{
          marginLeft: `${sidebarWidth}px`, // Adjust margin dynamically based on sidebar width
          transition: "margin-left 0.3s ease", // Smooth transition for resizing
        }}
      >
        {renderPage()}
      </div>
    </div>
  );
}

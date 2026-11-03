import React from "react";
import { CheckCircle, ShieldCheck } from "lucide-react";

export default function ModuleNav({ activeTab, setActiveTab }) {
  const tabs = [
    { id: "review", label: "Review" },
    { id: "how-it-works", label: "How it works" }
  ];

  return (
    <nav className="clean-nav-bar">
      <div className="clean-nav-inner">
        <div className="nav-tabs-group">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`clean-nav-tab ${isActive ? "active" : ""}`}
              >
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}

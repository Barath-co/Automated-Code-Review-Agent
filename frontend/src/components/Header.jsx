import React from "react";
import { Shield, Settings, History, CheckCircle2 } from "lucide-react";

export default function Header({ 
  serverHealth, 
  onOpenSettings, 
  onOpenHistory,
  apiKeyConfigured,
  activeModel
}) {
  const isOnline = serverHealth?.status === "online";

  return (
    <header className="clean-header">
      <div className="clean-header-inner">
        {/* Logo and Promise */}
        <div className="header-brand-group">
          <div className="header-logo-mark">
            <Shield size={20} className="header-logo-icon" />
          </div>
          <div className="header-brand-copy">
            <div className="brand-title-line">
              <h1 className="brand-name">CodeReview</h1>
              <span className="brand-tag">Agent</span>
            </div>
            <p className="brand-promise">Catch security and quality issues before they ship</p>
          </div>
        </div>

        {/* Right Controls */}
        <div className="header-controls">
          {/* Status Dot */}
          <div 
            className={`status-indicator ${isOnline ? "is-connected" : "is-disconnected"}`}
            title={isOnline ? "Backend connected" : "Backend offline"}
          >
            <span className="status-dot"></span>
            <span className="status-label">{isOnline ? "Connected" : "Offline"}</span>
          </div>

          {/* Mode Pill */}
          <button 
            onClick={onOpenSettings} 
            className={`mode-indicator-btn ${apiKeyConfigured ? "mode-live" : "mode-demo"}`}
            title="Configure API key and model"
          >
            <span>{apiKeyConfigured ? activeModel : "Demo mode"}</span>
          </button>

          {/* History button */}
          <button 
            onClick={onOpenHistory} 
            className="header-action-btn"
            title="View past reviews"
          >
            <History size={15} />
            <span>History</span>
          </button>

          {/* Settings button */}
          <button 
            onClick={onOpenSettings} 
            className="header-action-btn"
            title="Settings & API key"
          >
            <Settings size={15} />
            <span>Settings</span>
          </button>
        </div>
      </div>
    </header>
  );
}

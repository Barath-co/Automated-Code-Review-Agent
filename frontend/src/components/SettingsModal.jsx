import React, { useState } from "react";
import { X, Key, Sparkles, Check, AlertCircle, ExternalLink, Shield } from "lucide-react";

export default function SettingsModal({
  isOpen,
  onClose,
  apiKey,
  setApiKey,
  selectedModel,
  setSelectedModel
}) {
  const [tempKey, setTempKey] = useState(apiKey || "");
  const [tempModel, setTempModel] = useState(selectedModel || "gemini-2.5-flash");
  const [showKey, setShowKey] = useState(false);

  if (!isOpen) return null;

  const handleSave = () => {
    setApiKey(tempKey.trim());
    setSelectedModel(tempModel);
    // FIX C5: Do NOT persist the API key to localStorage.
    // The key is held in React state (session-only) and sent per-request to the backend.
    // Persisting API keys in localStorage is an XSS security anti-pattern.
    onClose();
  };

  const handleClear = () => {
    setTempKey("");
    setApiKey("");
    // No localStorage to clear — key was never stored there
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        {/* Header */}
        <div className="modal-header">
          <div className="modal-title-wrap">
            <Key size={18} className="text-cyan-400" />
            <h3 className="modal-title">Provider & Gemini API Configuration</h3>
          </div>
          <button onClick={onClose} className="modal-close-btn">
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div className="modal-body">
          <div className="info-banner">
            <Shield size={16} className="text-cyan-400 shrink-0 mt-0.5" />
            <p className="banner-text">
              Enter your Google Gemini API key to activate direct live Gemini model execution. 
              If left blank, the system automatically runs the high-fidelity <strong>Virtual Consensus Simulation Engine</strong>.
            </p>
          </div>

          {/* API Key Input */}
          <div className="form-group">
            <label className="form-label">Google Gemini API Key:</label>
            <div className="key-input-wrapper">
              <input
                type={showKey ? "text" : "password"}
                value={tempKey}
                onChange={(e) => setTempKey(e.target.value)}
                placeholder="AIzaSy..."
                className="modal-input"
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="show-key-btn"
              >
                {showKey ? "Hide" : "Show"}
              </button>
            </div>
            <div className="field-hint-row">
              <span className="field-hint">Your API key is kept in session memory only — never stored on disk or in the browser.</span>
              <a
                href="https://aistudio.google.com/app/apikey"
                target="_blank"
                rel="noreferrer"
                className="key-link"
              >
                <span>Get Free Key</span>
                <ExternalLink size={12} />
              </a>
            </div>
          </div>

          {/* Model Selector */}
          <div className="form-group">
            <label className="form-label">Active Gemini Model Provider:</label>
            <select
              value={tempModel}
              onChange={(e) => setTempModel(e.target.value)}
              className="modal-select"
            >
              <option value="gemini-2.5-flash">Gemini 2.5 Flash (Ultra-fast, High Accuracy - Recommended)</option>
              <option value="gemini-1.5-flash">Gemini 1.5 Flash (Cost-optimized Baseline)</option>
              <option value="gemini-2.5-pro">Gemini 2.5 Pro (Deep Code Reasoning)</option>
            </select>
            <span className="field-hint">
              Used across NCIO adapters to evaluate code review tasks.
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="modal-footer">
          {tempKey && (
            <button onClick={handleClear} className="btn-modal-danger">
              Clear Key
            </button>
          )}
          <div className="footer-right-btns">
            <button onClick={onClose} className="btn-modal-cancel">
              Cancel
            </button>
            <button onClick={handleSave} className="btn-modal-save">
              <Check size={14} />
              <span>Save Configuration</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

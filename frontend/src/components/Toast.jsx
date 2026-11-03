import React from "react";
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react";

export default function Toast({ toast, onClose }) {
  if (!toast) return null;

  const type = toast.type || "info";

  return (
    <div className={`toast-notification toast-${type}`}>
      <div className="toast-icon-wrap">
        {type === "success" && <CheckCircle2 size={16} />}
        {type === "error" && <AlertCircle size={16} />}
        {type === "info" && <Info size={16} />}
      </div>
      <span className="toast-message">{toast.message}</span>
      <button onClick={onClose} className="toast-close-btn" title="Dismiss">
        <X size={14} />
      </button>
    </div>
  );
}

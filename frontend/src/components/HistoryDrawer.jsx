import React, { useEffect, useState } from "react";
import { X, History, ExternalLink, RefreshCw } from "lucide-react";
import { fetchReviewHistory, fetchReportById } from "../utils/api";

export default function HistoryDrawer({ isOpen, onClose, onLoadReport, onShowToast }) {
  const [historyItems, setHistoryItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchReviewHistory();
      setHistoryItems(data);
    } catch (err) {
      setError(err.message);
      if (onShowToast) onShowToast("Failed to load review history", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadHistory();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSelectTask = async (taskId) => {
    try {
      setLoading(true);
      const report = await fetchReportById(taskId);
      onLoadReport(report);
      if (onShowToast) onShowToast(`Loaded review ${taskId}`, "success");
      onClose();
    } catch (err) {
      if (onShowToast) onShowToast(`Could not load report: ${err.message}`, "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="clean-drawer-backdrop" onClick={onClose}>
      <div className="clean-drawer-panel" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="clean-drawer-header">
          <div className="drawer-title-box">
            <History size={16} className="text-brand" />
            <h3 className="clean-drawer-title">Review history</h3>
          </div>
          <div className="drawer-actions">
            <button onClick={loadHistory} className="btn-clean-ghost icon-only" title="Refresh">
              <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
            </button>
            <button onClick={onClose} className="btn-clean-ghost icon-only" title="Close">
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="clean-drawer-body">
          {error && <div className="drawer-error-strip">{error}</div>}

          {historyItems.length === 0 && !loading && !error && (
            <div className="drawer-empty-state">
              <History size={28} className="text-muted" />
              <p className="empty-lead">No review history yet</p>
              <span className="empty-sub">Completed code reviews will appear here.</span>
            </div>
          )}

          <div className="history-task-list">
            {historyItems.map((item) => (
              <div 
                key={item.task_id} 
                onClick={() => handleSelectTask(item.task_id)}
                className="history-clean-card"
              >
                <div className="history-card-top">
                  <span className="task-id-tag">{item.task_id}</span>
                  <span className={`task-badge ${item.consensus_score >= 80 ? "badge-good" : "badge-warn"}`}>
                    {item.consensus_score}% agreement
                  </span>
                </div>

                <div className="history-card-middle">
                  <span className="history-lang">{item.language?.toUpperCase()}</span>
                  <span>·</span>
                  <span>{item.loc} lines</span>
                  <span>·</span>
                  <span>{item.latency_ms} ms</span>
                </div>

                <div className="history-card-bottom">
                  <span className="history-date">
                    {new Date(item.created_at).toLocaleDateString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
                  </span>
                  <span className="load-link">
                    Open <ExternalLink size={11} />
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

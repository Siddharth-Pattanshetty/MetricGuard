/**
 * ==========================================================
 * MetricGuard — LiveAlerts Component
 * ==========================================================
 * Real-time WebSocket alert feed with toast notifications
 * and scrollable alert history.
 */

import { useState, useEffect, useRef } from 'react';
import { createAlertWebSocket } from '../services/websocket';
import { fetchAlerts } from '../services/api';

export default function LiveAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [wsStatus, setWsStatus] = useState('disconnected');
  const [toasts, setToasts] = useState([]);
  const [loading, setLoading] = useState(true);
  const listRef = useRef(null);

  // Load historical alerts on mount
  useEffect(() => {
    (async () => {
      try {
        const data = await fetchAlerts();
        setAlerts(data || []);
      } catch {
        /* empty */
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Connect WebSocket for live updates
  useEffect(() => {
    const ws = createAlertWebSocket(
      (data) => {
        // Add to alerts list
        setAlerts((prev) => [data, ...prev].slice(0, 100));

        // Show toast notification
        const toast = { id: Date.now(), data };
        setToasts((prev) => [toast, ...prev].slice(0, 5));

        // Auto-dismiss toast after 5 seconds
        setTimeout(() => {
          setToasts((prev) => prev.filter((t) => t.id !== toast.id));
        }, 5000);
      },
      (status) => setWsStatus(status),
    );

    return () => ws.close();
  }, []);

  // Auto-scroll to top when new alerts arrive
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = 0;
    }
  }, [alerts]);

  const statusColor = {
    connected: 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]',
    connecting: 'bg-amber-400 animate-pulse shadow-[0_0_8px_rgba(251,191,36,0.5)]',
    disconnected: 'bg-slate-500',
    error: 'bg-rose-400 shadow-[0_0_8px_rgba(248,113,113,0.5)]',
  };

  const getSeverityStyle = (sev) => {
    const s = (sev || '').toLowerCase();
    if (s === 'critical') return { color: 'text-rose-400', bg: 'bg-rose-500/10', border: 'border-l-rose-500', badge: 'badge-critical' };
    if (s === 'high') return { color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-l-amber-500', badge: 'badge-warning' };
    if (s === 'medium') return { color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-l-yellow-500', badge: 'badge-medium' };
    return { color: 'text-sky-400', bg: 'bg-sky-500/10', border: 'border-l-sky-500', badge: 'badge-low' };
  };

  const renderSeverityIcon = (sev, className = "w-4 h-4") => {
    const s = (sev || '').toLowerCase();
    let pathD = 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'; // Default info
    if (s === 'critical' || s === 'high' || s === 'medium') {
      pathD = 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z';
    }
    const styles = getSeverityStyle(sev);
    return (
      <svg className={`${className} ${styles.color} shrink-0`} fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d={pathD} />
      </svg>
    );
  };

  return (
    <div className="space-y-4">
      {/* Toast Notifications Panel (Fixed, bottom-right) */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 max-w-sm w-full pointer-events-none">
        {toasts.map((toast) => {
          const styles = getSeverityStyle(toast.data.severity);
          return (
            <div
              key={toast.id}
              className={`pointer-events-auto bg-[#090d16]/95 border border-slate-800 rounded-xl p-4 shadow-2xl backdrop-blur-md flex items-start gap-3 border-l-4 ${styles.border} transition-all duration-300 transform translate-y-0 scale-100 animate-slide-up`}
            >
              {renderSeverityIcon(toast.data.severity, "w-5 h-5 mt-0.5")}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <p className="text-xs font-bold text-slate-200 truncate">
                    {toast.data.title || 'New Alert'}
                  </p>
                  <span className="text-[9px] font-mono text-slate-500 whitespace-nowrap">
                    Just now
                  </span>
                </div>
                <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                  {toast.data.message || toast.data.alert_id || ''}
                </p>
              </div>
              <button
                onClick={() => setToasts((prev) => prev.filter((t) => t.id !== toast.id))}
                className="text-slate-500 hover:text-slate-300 hover:bg-slate-800/40 p-1 rounded transition-colors"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          );
        })}
      </div>

      {/* Connection status card */}
      <div className="glass-card p-4 flex items-center justify-between border-slate-900 bg-slate-950/20">
        <div className="flex items-center gap-3">
          <span className={`w-2 h-2 rounded-full ${statusColor[wsStatus]}`} />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Alert Channel
          </span>
          <span className="text-[10px] text-slate-500 font-semibold font-mono capitalize">
            {wsStatus}
          </span>
        </div>
        <span className="text-[10px] font-mono font-bold text-slate-500 bg-slate-950/50 px-2 py-0.5 rounded border border-slate-900">
          {alerts.length} Records
        </span>
      </div>

      {/* Alert history list */}
      {loading ? (
        <div className="skeleton h-72 rounded-2xl" />
      ) : !alerts.length ? (
        <div className="glass-card p-8 text-center border-slate-900">
          <p className="text-slate-500 text-xs italic">No alerts recorded in this stream.</p>
        </div>
      ) : (
        <div className="glass-card p-0 overflow-hidden border-slate-900">
          <div ref={listRef} className="max-h-[480px] overflow-y-auto divide-y divide-slate-900/60 custom-scrollbar">
            {alerts.map((alert, idx) => {
              const styles = getSeverityStyle(alert.severity);
              return (
                <div
                  key={alert.alert_id || idx}
                  className="p-4 hover:bg-indigo-500/[0.02] transition-colors flex items-start gap-3.5"
                >
                  {renderSeverityIcon(alert.severity, "w-4 h-4 mt-1")}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                      <span className="font-mono text-[10px] font-bold text-slate-500">
                        {alert.alert_id || `ALT-${idx}`}
                      </span>
                      <span className={`badge ${styles.badge}`}>
                        {alert.severity}
                      </span>
                      <span className={`badge ${alert.status?.toLowerCase() === 'closed' ? 'badge-closed' : 'badge-open'}`}>
                        {alert.status || 'OPEN'}
                      </span>
                    </div>
                    <p className="text-xs text-slate-200 font-semibold mb-1 leading-snug">
                      {alert.title || 'System Alert'}
                    </p>
                    <p className="text-xs text-slate-400/80 leading-relaxed font-sans">
                      {alert.message || ''}
                    </p>
                    {alert.affected_services?.length > 0 && (
                      <div className="flex gap-1.5 mt-2.5 flex-wrap">
                        {(Array.isArray(alert.affected_services) ? alert.affected_services : [alert.affected_services]).map((svc) => (
                          <span
                            key={svc}
                            className="px-1.5 py-0.5 rounded-md bg-slate-950/60 border border-slate-900 text-slate-400 font-mono text-[9px]"
                          >
                            {svc}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <span className="text-[10px] font-mono text-slate-500 whitespace-nowrap mt-1">
                    {alert.timestamp ? new Date(alert.timestamp).toLocaleTimeString() : ''}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

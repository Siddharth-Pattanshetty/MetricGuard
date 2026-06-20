/**
 * ==========================================================
 * MetricGuard — RCAView Component
 * ==========================================================
 * Displays Root Cause Analysis stats with confidence bars.
 */

import { useState, useEffect } from 'react';
import { fetchRCAStats } from '../services/api';

export default function RCAView() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await fetchRCAStats();
        setStats(data);
      } catch {
        /* empty */
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="skeleton h-48 rounded-2xl" />;

  if (!stats) {
    return (
      <div className="glass-card p-8 text-center border border-slate-900">
        <p className="text-slate-500 text-sm">No RCA data available</p>
      </div>
    );
  }

  const byRootCause = stats.by_root_cause || {};
  const bySeverity = stats.by_severity || {};
  const total = stats.total_anomalies || 0;

  // Color map for root causes
  const rootCauseColors = {
    'CPU Usage': '#8b5cf6', // violet
    'Memory Usage': '#0ea5e9', // sky
    'Disk I/O': '#f59e0b', // amber
    'Network I/O': '#10b981', // emerald
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      {/* Total summary card */}
      <div className="glass-card p-6 bg-gradient-to-br from-indigo-500/10 to-violet-500/10 border-indigo-500/20 flex flex-col justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
            <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <div>
            <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Total Anomalies</p>
            <p className="text-4xl font-extrabold text-indigo-400 tracking-tight">{total}</p>
          </div>
        </div>
        <p className="text-xs text-slate-400/80 mt-4 leading-relaxed">
          Detected by isolation forest and autoencoder models across all system resource dimensions.
        </p>
      </div>

      {/* By Root Cause */}
      <div className="glass-card p-6">
        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">By Root Cause</h4>
        <div className="space-y-4">
          {Object.entries(byRootCause).map(([cause, count]) => {
            const pct = total > 0 ? (count / total) * 100 : 0;
            const color = rootCauseColors[cause] || '#64748b';
            return (
              <div key={cause} className="group">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-medium text-slate-400 group-hover:text-slate-300 transition-colors">{cause}</span>
                  <span className="text-xs font-mono font-bold text-slate-300 bg-slate-950/50 px-1.5 py-0.5 rounded border border-slate-900">{count}</span>
                </div>
                <div className="progress-bar">
                  <div
                    className="progress-bar-fill transition-all duration-500 ease-out"
                    style={{ 
                      width: `${pct}%`, 
                      background: color,
                      boxShadow: `0 0 8px ${color}50` 
                    }}
                  />
                </div>
              </div>
            );
          })}
          {Object.keys(byRootCause).length === 0 && (
            <p className="text-xs text-slate-600 italic">No breakdown available</p>
          )}
        </div>
      </div>

      {/* By Severity */}
      <div className="glass-card p-6">
        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">By Severity</h4>
        <div className="space-y-4">
          {Object.entries(bySeverity).map(([sev, count]) => {
            const pct = total > 0 ? (count / total) * 100 : 0;
            const s = sev.toLowerCase();
            const color = s === 'critical' ? '#f43f5e' : s === 'warning' ? '#f59e0b' : '#0ea5e9';
            return (
              <div key={sev} className="group">
                <div className="flex items-center justify-between mb-1.5">
                  <span className={`badge ${s === 'critical' ? 'badge-critical' : s === 'warning' ? 'badge-warning' : 'badge-medium'}`}>
                    {sev}
                  </span>
                  <span className="text-xs font-mono font-bold text-slate-300 bg-slate-950/50 px-1.5 py-0.5 rounded border border-slate-900">{count}</span>
                </div>
                <div className="progress-bar">
                  <div
                    className="progress-bar-fill transition-all duration-500 ease-out"
                    style={{ 
                      width: `${pct}%`, 
                      background: color,
                      boxShadow: `0 0 8px ${color}50` 
                    }}
                  />
                </div>
              </div>
            );
          })}
          {Object.keys(bySeverity).length === 0 && (
            <p className="text-xs text-slate-600 italic">No breakdown available</p>
          )}
        </div>
      </div>
    </div>
  );
}

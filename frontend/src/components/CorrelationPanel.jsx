/**
 * ==========================================================
 * MetricGuard — CorrelationPanel Component
 * ==========================================================
 * Card-based display of metric-log correlation results.
 */

import { useState, useEffect } from 'react';
import { fetchCorrelations } from '../services/api';

export default function CorrelationPanel() {
  const [correlations, setCorrelations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await fetchCorrelations();
        setCorrelations(data);
      } catch {
        /* empty */
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="skeleton h-52 rounded-2xl" />
        ))}
      </div>
    );
  }

  if (!correlations.length) {
    return (
      <div className="glass-card p-8 text-center border-slate-900">
        <p className="text-slate-500 text-xs italic">No correlation results available.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {correlations.map((c, idx) => {
        const score = c.correlation_score ?? c.confidence ?? 0;
        const scoreColor = score >= 0.8 ? 'text-rose-400' : score >= 0.5 ? 'text-amber-400' : 'text-emerald-400';
        const barColor = score >= 0.8 ? '#f43f5e' : score >= 0.5 ? '#f59e0b' : '#10b981';

        return (
          <div key={c.id || idx} className="glass-card p-6 border-slate-900 flex flex-col justify-between hover:border-indigo-500/25 transition-all">
            <div>
              {/* Score header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
                    <svg className="w-4 h-4 text-indigo-400" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
                    </svg>
                  </div>
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                    Relation #{idx + 1}
                  </span>
                </div>
                <span className={`text-lg font-bold font-mono ${scoreColor}`}>
                  {(score * 100).toFixed(0)}%
                </span>
              </div>

              {/* Score bar */}
              <div className="progress-bar mb-4">
                <div
                  className="progress-bar-fill"
                  style={{ 
                    width: `${(score * 100).toFixed(0)}%`, 
                    background: barColor,
                    boxShadow: `0 0 8px ${barColor}40`
                  }}
                />
              </div>

              {/* Metric anomaly */}
              <div className="mb-4">
                <p className="text-[9px] text-slate-500 font-bold uppercase tracking-wider mb-1">Metric Signal</p>
                <p className="text-xs text-slate-200 font-semibold leading-relaxed">
                  {c.metric_anomaly_id ? `Anomaly #${c.metric_anomaly_id}` : c.root_cause || 'Unknown metric event'}
                </p>
              </div>

              {/* Log anomaly */}
              <div className="mb-4">
                <p className="text-[9px] text-slate-500 font-bold uppercase tracking-wider mb-1">Correlated Log Template</p>
                <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed font-mono bg-slate-950/40 p-2.5 rounded-lg border border-slate-900">
                  {c.log_message || c.log_anomaly_id ? (c.log_message || `Anomaly ID: ${c.log_anomaly_id}`) : 'No related log signal'}
                </p>
              </div>
            </div>

            {/* Timestamp */}
            <div className="pt-3 border-t border-slate-900/60 mt-auto">
              <p className="text-[9px] text-slate-500 font-bold uppercase tracking-wider mb-1">Correlated At</p>
              <p className="text-[10px] font-mono text-slate-500">
                {c.created_at ? new Date(c.created_at).toLocaleString() : '—'}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

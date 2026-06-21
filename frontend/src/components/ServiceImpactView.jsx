/**
 * ==========================================================
 * MetricGuard — ServiceImpactView Component
 * ==========================================================
 * Displays service impact analysis results with impact cards.
 */

import { useState, useEffect } from 'react';
import { fetchServiceDashboard } from '../services/api';

export default function ServiceImpactView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const result = await fetchServiceDashboard();
        setData(result);
      } catch {
        /* empty */
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="skeleton h-48 rounded-2xl" />;

  if (!data) {
    return (
      <div className="glass-card p-8 text-center border-slate-900">
        <p className="text-slate-500 text-xs italic">No impact analysis data available.</p>
      </div>
    );
  }

  const severityColor = {
    Critical: 'text-rose-400 border-rose-500/20 from-rose-500/10 hover:border-rose-500/35 hover:ring-rose-500/10',
    High: 'text-amber-400 border-amber-500/20 from-amber-500/10 hover:border-amber-500/35 hover:ring-amber-500/10',
    Warning: 'text-amber-400 border-amber-500/20 from-amber-500/10 hover:border-amber-500/35 hover:ring-amber-500/10',
    Low: 'text-sky-400 border-sky-500/20 from-sky-500/10 hover:border-sky-500/35 hover:ring-sky-500/10',
  };

  const sc = severityColor[data.severity] || severityColor.Low;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Root Cause */}
        <div className={`glass-card p-6 bg-gradient-to-br ${sc} to-transparent transition-all duration-300`}>
          <div className="flex items-center gap-2 mb-2">
            <svg className="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Root Cause</p>
          </div>
          <p className="text-base font-bold text-slate-200 truncate">{data.root_cause || 'None detected'}</p>
        </div>

        {/* Affected Service */}
        <div className="glass-card p-6 hover:border-indigo-500/20 hover:ring-indigo-500/10 transition-all duration-300">
          <div className="flex items-center gap-2 mb-2">
            <svg className="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Affected Origin</p>
          </div>
          <p className="text-base font-bold text-indigo-400 truncate">{data.affected_service || '—'}</p>
        </div>

        {/* Severity */}
        <div className="glass-card p-6 hover:border-slate-800 transition-all duration-300">
          <div className="flex items-center gap-2 mb-3">
            <svg className="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">System Severity</p>
          </div>
          <span className={`badge ${
            (data.severity || 'low').toLowerCase() === 'critical' ? 'badge-critical' :
            (data.severity || 'low').toLowerCase() === 'warning' ? 'badge-warning' : 'badge-low'
          }`}>
            {data.severity || 'None'}
          </span>
        </div>

        {/* Total Affected */}
        <div className="glass-card p-6 hover:border-rose-500/10 transition-all duration-300">
          <div className="flex items-center gap-2 mb-1">
            <svg className="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Impacted Services</p>
          </div>
          <p className="text-3xl font-extrabold text-rose-400 tracking-tight">{data.total_affected || 0}</p>
        </div>
      </div>

      {/* Impacted Services List */}
      {data.impacted_services?.length > 0 && (
        <div className="glass-card p-6 border-slate-900/60">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3.5">Downstream Impact Path</h4>
          <div className="flex flex-wrap gap-2">
            {data.impacted_services.map((svc) => (
              <span
                key={svc}
                className="px-2.5 py-1 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold font-mono uppercase tracking-wider"
              >
                {svc}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Service Health Grid */}
      {data.service_health?.length > 0 && (
        <div className="glass-card p-6 border-slate-900/60">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Inventory Health Status</h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
            {data.service_health.map((svc) => {
              const s = (svc.status || '').toLowerCase();
              const dotColor = s === 'healthy' ? 'bg-emerald-400' : s === 'degraded' ? 'bg-amber-400' : 'bg-rose-400';
              const borderStyle = s === 'healthy' ? 'border-slate-800/40' : s === 'degraded' ? 'border-amber-500/20' : 'border-rose-500/20';
              const textStyle = s === 'healthy' ? 'text-slate-300' : s === 'degraded' ? 'text-amber-400 font-semibold' : 'text-rose-400 font-semibold';
              return (
                <div
                  key={svc.service_name}
                  className={`flex items-center gap-2.5 p-3 rounded-xl bg-slate-950/40 border ${borderStyle} hover:bg-slate-900/40 transition-colors`}
                >
                  <span className={`w-2 h-2 rounded-full ${dotColor} ${s !== 'healthy' ? 'animate-pulse' : ''}`} />
                  <span className={`text-xs truncate font-mono uppercase tracking-wider ${textStyle}`}>{svc.service_name}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

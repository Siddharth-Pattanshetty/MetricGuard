/**
 * ==========================================================
 * MetricGuard — IncidentTable Component
 * ==========================================================
 * Incident management table with status badges and filtering.
 */

import { useState, useEffect, useCallback } from 'react';
import { fetchIncidents } from '../services/api';

const STATUS_OPTIONS = ['ALL', 'OPEN', 'INVESTIGATING', 'MITIGATED', 'RESOLVED', 'CLOSED'];

function StatusBadge({ status }) {
  const s = (status || '').toLowerCase();
  let badgeClass = 'badge-closed';
  if (s === 'open') badgeClass = 'badge-open';
  else if (s === 'investigating') badgeClass = 'badge-investigating';
  else if (s === 'mitigated') badgeClass = 'badge-mitigated';
  else if (s === 'resolved') badgeClass = 'badge-resolved';

  return <span className={`badge ${badgeClass}`}>{status}</span>;
}

function PriorityBadge({ priority }) {
  const colors = {
    P1: 'bg-rose-500/10 text-rose-400 border-rose-500/20 shadow-[0_0_8px_rgba(244,63,94,0.15)]',
    P2: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    P3: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
    P4: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
  };
  return (
    <span className={`badge ${colors[priority] || colors.P4} font-mono font-bold`}>
      {priority}
    </span>
  );
}

export default function IncidentTable() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');
  const [total, setTotal] = useState(0);

  const load = useCallback(async () => {
    try {
      const params = {};
      if (filter !== 'ALL') params.status = filter;
      const result = await fetchIncidents(params);
      setIncidents(result.incidents || []);
      setTotal(result.total || 0);
    } catch {
      /* empty */
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    setLoading(true);
    load();
  }, [load]);

  return (
    <div className="glass-card p-0 overflow-hidden border-slate-900 shadow-2xl">
      {/* Filter bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-5 border-b border-slate-900/60 bg-slate-950/20">
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Status:</span>
          <div className="status-filter-container flex flex-wrap items-center gap-2 bg-[#090d16] p-1.5 rounded-xl border border-slate-800/80">
            {STATUS_OPTIONS.map((s) => (
              <button
                key={s}
                onClick={() => setFilter(s)}
                className={`status-filter-btn px-4 py-2 rounded-lg text-xs font-bold transition-all duration-200 cursor-pointer ${
                  filter === s
                    ? 'active bg-indigo-600 text-white shadow-lg shadow-indigo-600/15'
                    : 'inactive text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
        <span className="text-[10px] font-mono font-bold text-slate-500 bg-slate-950/50 px-2.5 py-1 rounded-lg border border-slate-900">
          {total} incidents
        </span>
      </div>

      {/* Table */}
      {loading ? (
        <div className="p-6"><div className="skeleton h-48 rounded-xl" /></div>
      ) : !incidents.length ? (
        <div className="p-12 text-center">
          <svg className="w-8 h-8 text-slate-600 mx-auto mb-2" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-slate-500 text-xs italic">No active incidents matching status.</p>
        </div>
      ) : (
        <div className="overflow-x-auto max-h-[460px] overflow-y-auto custom-scrollbar">
          <table className="w-full border-collapse text-left text-xs">
            <thead>
              <tr className="bg-slate-950/40 border-b border-slate-900/60 sticky top-0 z-10">
                <th className="px-6 py-4 font-bold text-slate-400 uppercase tracking-wider text-[10px]">Incident ID</th>
                <th className="px-6 py-4 font-bold text-slate-400 uppercase tracking-wider text-[10px]">Root Cause</th>
                <th className="px-6 py-4 font-bold text-slate-400 uppercase tracking-wider text-[10px]">Priority</th>
                <th className="px-6 py-4 font-bold text-slate-400 uppercase tracking-wider text-[10px]">Severity</th>
                <th className="px-6 py-4 font-bold text-slate-400 uppercase tracking-wider text-[10px]">Status</th>
                <th className="px-6 py-4 font-bold text-slate-400 uppercase tracking-wider text-[10px] text-center">Alerts</th>
                <th className="px-6 py-4 font-bold text-slate-400 uppercase tracking-wider text-[10px]">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-900/30">
              {incidents.map((inc) => (
                <tr key={inc.incident_id} className="hover:bg-indigo-500/[0.01] transition-colors duration-150">
                  <td className="px-6 py-4 font-mono text-indigo-400 font-bold">
                    {inc.incident_id}
                  </td>
                  <td className="px-6 py-4 text-slate-300 font-medium font-sans">
                    {inc.root_cause}
                  </td>
                  <td className="px-6 py-4">
                    <PriorityBadge priority={inc.priority} />
                  </td>
                  <td className="px-6 py-4">
                    <span className={`badge ${
                      (inc.severity || '').toLowerCase() === 'critical' ? 'badge-critical' :
                      (inc.severity || '').toLowerCase() === 'warning' ? 'badge-warning' : 'badge-low'
                    }`}>
                      {inc.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={inc.status} />
                  </td>
                  <td className="px-6 py-4 text-center text-slate-300 font-bold font-mono">
                    {inc.alert_count || 1}
                  </td>
                  <td className="px-6 py-4 text-slate-500 font-mono text-[10px] whitespace-nowrap">
                    {inc.created_at ? new Date(inc.created_at).toLocaleString() : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

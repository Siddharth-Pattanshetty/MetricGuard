/**
 * ==========================================================
 * MetricGuard — MetricAnomalies Component
 * ==========================================================
 * Table displaying metric anomaly results with severity badges.
 */

import { useState, useEffect } from 'react';
import { fetchMetricAnomalies } from '../services/api';

function SeverityBadge({ severity }) {
  const s = (severity || '').toLowerCase();
  const cls =
    s === 'critical' ? 'badge-critical' :
    s === 'warning'  ? 'badge-warning'  :
    s === 'high'     ? 'badge-high'     :
                       'badge-medium';
  return <span className={`badge ${cls}`}>{severity}</span>;
}

export default function MetricAnomalies() {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await fetchMetricAnomalies(50);
        setAnomalies(data);
      } catch {
        /* empty */
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="skeleton h-64 rounded-2xl" />;

  if (!anomalies.length) {
    return (
      <div className="glass-card p-8 text-center border-slate-900">
        <p className="text-slate-500 text-xs italic">No metric anomalies detected.</p>
      </div>
    );
  }

  return (
    <div className="glass-card p-0 overflow-hidden border-slate-900 shadow-2xl">
      <div className="overflow-x-auto max-h-[460px] overflow-y-auto custom-scrollbar">
        <table className="w-full border-collapse text-left text-xs">
          <thead>
            <tr className="bg-slate-950/40 border-b border-slate-900/60 sticky top-0 z-10">
              <th className="px-6 py-4 font-bold text-slate-400 uppercase tracking-wider text-[10px]">Timestamp</th>
              <th className="px-6 py-4 font-bold text-slate-400 uppercase tracking-wider text-[10px]">Root Cause</th>
              <th className="px-6 py-4 font-bold text-slate-400 uppercase tracking-wider text-[10px]">Score</th>
              <th className="px-6 py-4 font-bold text-slate-400 uppercase tracking-wider text-[10px]">Severity</th>
              <th className="px-6 py-4 font-bold text-slate-400 uppercase tracking-wider text-[10px]">Detected By</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-900/30">
            {anomalies.map((a) => (
              <tr key={a.id} className="hover:bg-indigo-500/[0.01] transition-colors duration-150">
                <td className="px-6 py-4 text-slate-500 font-mono text-[10px] whitespace-nowrap">
                  {new Date(a.timestamp).toLocaleString()}
                </td>
                <td className="px-6 py-4 font-semibold text-slate-300 font-sans">{a.root_cause || '—'}</td>
                <td className="px-6 py-4">
                  <span className={`font-mono font-bold ${a.anomaly_score > 0.8 ? 'text-rose-400' : 'text-amber-400'}`}>
                    {a.anomaly_score?.toFixed(4)}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <SeverityBadge severity={a.severity} />
                </td>
                <td className="px-6 py-4 text-slate-500 font-mono text-[10px]">{a.detected_by}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

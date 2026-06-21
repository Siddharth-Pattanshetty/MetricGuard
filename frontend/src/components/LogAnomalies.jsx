/**
 * ==========================================================
 * MetricGuard — LogAnomalies Component
 * ==========================================================
 * Scrollable table of log anomalies with anomaly score highlighting.
 */

import { useState, useEffect } from 'react';
import { fetchLogAnomalies } from '../services/api';

export default function LogAnomalies() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await fetchLogAnomalies(120, 50);
        setLogs(data);
      } catch {
        /* empty */
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="skeleton h-64 rounded-2xl" />;

  if (!logs.length) {
    return (
      <div className="glass-card p-8 text-center border-slate-900">
        <p className="text-slate-500 text-xs italic">No log anomalies detected.</p>
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
              <th className="px-6 py-4 font-bold text-slate-400 uppercase tracking-wider text-[10px]">Service</th>
              <th className="px-6 py-4 font-bold text-slate-400 uppercase tracking-wider text-[10px]">Message</th>
              <th className="px-6 py-4 font-bold text-slate-400 uppercase tracking-wider text-[10px]">Template</th>
              <th className="px-6 py-4 font-bold text-slate-400 uppercase tracking-wider text-[10px]">Score</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-900/30">
            {logs.map((log) => {
              const isHigh = log.anomaly_score >= 0.8;
              return (
                <tr key={log.id} className={`hover:bg-indigo-500/[0.01] transition-colors duration-150 ${isHigh ? 'bg-rose-500/[0.02]' : ''}`}>
                  <td className="px-6 py-4 text-slate-500 font-mono text-[10px] whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4">
                    <span className="badge badge-info">{log.service_name}</span>
                  </td>
                  <td className="px-6 py-4 max-w-xs truncate text-slate-300 font-sans" title={log.message}>
                    {log.message}
                  </td>
                  <td className="px-6 py-4 max-w-xs truncate text-slate-500 font-mono text-[10px]" title={log.template}>
                    {log.template}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2.5">
                      <div className="progress-bar w-16">
                        <div
                          className="progress-bar-fill"
                          style={{
                            width: `${(log.anomaly_score * 100).toFixed(0)}%`,
                            background: isHigh ? '#f43f5e' : '#f59e0b',
                            boxShadow: `0 0 6px ${isHigh ? '#f43f5e' : '#f59e0b'}40`
                          }}
                        />
                      </div>
                      <span className={`font-mono font-bold text-[10px] ${isHigh ? 'text-rose-400' : 'text-amber-400'}`}>
                        {log.anomaly_score?.toFixed(3)}
                      </span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/**
 * ==========================================================
 * MetricGuard — RecommendationPanel Component
 * ==========================================================
 * Displays recommendations from the Recommendation Engine,
 * fetched per-incident.
 */

import { useState, useEffect } from 'react';
import { fetchIncidents, fetchIncidentRecommendations } from '../services/api';

export default function RecommendationPanel() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [incidents, setIncidents] = useState([]);

  // Load incidents first, then fetch recommendations for the latest one
  useEffect(() => {
    (async () => {
      try {
        const result = await fetchIncidents({ limit: 10 });
        const incs = result.incidents || [];
        setIncidents(incs);

        if (incs.length > 0) {
          const latest = incs[0];
          setSelectedIncident(latest.incident_id);
          const recs = await fetchIncidentRecommendations(latest.incident_id);
          setRecommendations(recs.recommendations || []);
        }
      } catch {
        /* empty */
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleSelectIncident = async (incidentId) => {
    setSelectedIncident(incidentId);
    setLoading(true);
    try {
      const recs = await fetchIncidentRecommendations(incidentId);
      setRecommendations(recs.recommendations || []);
    } catch {
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !incidents.length) return <div className="skeleton h-64 rounded-2xl" />;

  return (
    <div className="space-y-4">
      {/* Incident selector */}
      {incidents.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap bg-slate-950/20 p-2.5 rounded-xl border border-slate-900/60">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mr-2">Incident:</span>
          <div className="flex flex-wrap gap-2">
            {incidents.map((inc) => (
              <button
                key={inc.incident_id}
                onClick={() => handleSelectIncident(inc.incident_id)}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                  selectedIncident === inc.incident_id
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/15'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/40 border border-transparent'
                }`}
              >
                {inc.incident_id}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[...Array(2)].map((_, i) => <div key={i} className="skeleton h-48 rounded-2xl" />)}
        </div>
      ) : !recommendations.length ? (
        <div className="glass-card p-8 text-center border-slate-900">
          <p className="text-slate-500 text-xs italic">No remediation suggestions available for this incident.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {recommendations.map((rec, idx) => {
            const confidence = rec.confidence || 0;
            const confPct = (confidence * 100).toFixed(0);
            const confColor =
              confidence >= 0.8 ? '#10b981' :
              confidence >= 0.5 ? '#f59e0b' : '#64748b';

            return (
              <div key={idx} className="glass-card p-6 border-slate-900 flex flex-col justify-between hover:border-violet-500/25 transition-all">
                <div>
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-lg bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
                        <svg className="w-4 h-4 text-violet-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                      </div>
                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                        Remediation Plan #{idx + 1}
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-mono font-bold" style={{ color: confColor }}>
                        {confPct}%
                      </span>
                      <p className="text-[9px] text-slate-600 font-bold uppercase tracking-wider mt-0.5">Confidence</p>
                    </div>
                  </div>

                  {/* Confidence bar */}
                  <div className="progress-bar mb-4">
                    <div
                      className="progress-bar-fill"
                      style={{ 
                        width: `${confPct}%`, 
                        background: confColor,
                        boxShadow: `0 0 8px ${confColor}40`
                      }}
                    />
                  </div>

                  {/* Category */}
                  {rec.category && (
                    <div className="mb-3.5">
                      <span className="badge badge-info">{rec.category}</span>
                    </div>
                  )}

                  {/* Action */}
                  <div className="mb-4">
                    <p className="text-[9px] text-slate-500 font-bold uppercase tracking-wider mb-1">Suggested Action</p>
                    <p className="text-xs text-slate-200 font-semibold leading-relaxed">{rec.action || rec.recommendation || '—'}</p>
                  </div>
                </div>

                {/* Rationale */}
                {rec.rationale && (
                  <div className="pt-3 border-t border-slate-900/60 mt-auto">
                    <p className="text-[9px] text-slate-500 font-bold uppercase tracking-wider mb-1">Rationale</p>
                    <p className="text-[11px] text-slate-400/90 leading-relaxed font-sans">{rec.rationale}</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

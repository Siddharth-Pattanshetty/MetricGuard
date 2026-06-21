/**
 * ==========================================================
 * MetricGuard — MetricCards Component
 * ==========================================================
 * Displays 4 color-coded cards for CPU, Memory, Disk, Network
 * with inline SVG icons, real-time sparklines, and auto-refresh.
 */

import { useState, useEffect, useCallback } from 'react';
import { fetchMetrics } from '../services/api';

const METRIC_CONFIG = [
  {
    key: 'cpu',
    label: 'CPU Usage',
    icon: (className) => (
      <svg className={className} fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    field: 'cpu_usage',
    unit: '%',
    gradient: 'from-violet-500/10 to-indigo-500/10',
    border: 'border-violet-500/20 hover:border-violet-500/40',
    color: 'text-violet-400',
    ring: 'ring-violet-500/10',
    sparklineColor: '#8b5cf6',
  },
  {
    key: 'memory',
    label: 'Memory Usage',
    icon: (className) => (
      <svg className={className} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 5h10a2 2 0 012 2v10a2 2 0 01-2 2H7a2 2 0 01-2-2V7a2 2 0 012-2z" />
      </svg>
    ),
    field: 'memory_usage',
    unit: '%',
    gradient: 'from-sky-500/10 to-cyan-500/10',
    border: 'border-sky-500/20 hover:border-sky-500/40',
    color: 'text-sky-400',
    ring: 'ring-sky-500/10',
    sparklineColor: '#0ea5e9',
  },
  {
    key: 'disk',
    label: 'Disk I/O',
    icon: (className) => (
      <svg className={className} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
      </svg>
    ),
    field: 'disk_read',
    unit: ' KB/s',
    gradient: 'from-amber-500/10 to-orange-500/10',
    border: 'border-amber-500/20 hover:border-amber-500/40',
    color: 'text-amber-400',
    ring: 'ring-amber-500/10',
    sparklineColor: '#f59e0b',
  },
  {
    key: 'network',
    label: 'Network RX',
    icon: (className) => (
      <svg className={className} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-.778.099-1.533.284-2.253" />
      </svg>
    ),
    field: 'network_rx',
    unit: ' KB/s',
    gradient: 'from-emerald-500/10 to-teal-500/10',
    border: 'border-emerald-500/20 hover:border-emerald-500/40',
    color: 'text-emerald-400',
    ring: 'ring-emerald-500/10',
    sparklineColor: '#10b981',
  },
];

function getStatus(value, isPercent) {
  if (!isPercent) return { label: 'Active', class: 'badge-resolved' };
  if (value >= 90) return { label: 'Critical', class: 'badge-critical' };
  if (value >= 70) return { label: 'Warning', class: 'badge-warning' };
  return { label: 'Normal', class: 'badge-resolved' };
}

export default function MetricCards() {
  const [latest, setLatest] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      const data = await fetchMetrics(10);
      setHistory(data || []);
      setLatest(data?.[0] || null);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, 10000);
    return () => clearInterval(interval);
  }, [load]);

  const renderSparkline = (cfg) => {
    if (history.length < 2) return null;
    // Get values oldest to newest
    const values = history.map(m => m[cfg.field]).reverse();
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min === 0 ? 1 : max - min;
    
    const width = 120;
    const height = 40;
    const padding = 4;
    const points = values.map((val, idx) => {
      const x = (idx / (values.length - 1)) * width;
      const y = height - padding - ((val - min) / range) * (height - 2 * padding);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });
    
    const pathD = `M ${points.join(' L ')}`;
    const areaD = `${pathD} L ${width},${height} L 0,${height} Z`;
    const gradientId = `sparkline-grad-${cfg.key}`;

    return (
      <svg className="w-24 h-10 overflow-visible" viewBox={`0 0 ${width} ${height}`}>
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={cfg.sparklineColor} stopOpacity="0.2" />
            <stop offset="100%" stopColor={cfg.sparklineColor} stopOpacity="0.0" />
          </linearGradient>
        </defs>
        <path d={areaD} fill={`url(#${gradientId})`} />
        <path
          d={pathD}
          fill="none"
          stroke={cfg.sparklineColor}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    );
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="skeleton h-36 rounded-2xl" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {METRIC_CONFIG.map((cfg) => {
        const value = latest?.[cfg.field];
        const displayValue = value != null ? (cfg.unit === '%' ? value.toFixed(1) : value.toFixed(0)) : '—';
        const isPercent = cfg.unit === '%';
        const status = getStatus(value, isPercent);
        const pct = isPercent ? Math.min(100, value || 0) : Math.min(100, ((value || 0) / 50000) * 100);

        return (
          <div
            key={cfg.key}
            className={`glass-card p-6 bg-gradient-to-br ${cfg.gradient} ${cfg.border} hover:ring-2 hover:${cfg.ring} transition-all duration-300`}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2.5">
                {cfg.icon(cfg.color)}
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">{cfg.label}</span>
              </div>
              <span className={`badge ${status.class}`}>{status.label}</span>
            </div>

            <div className="flex items-end justify-between mb-4">
              <div className={`text-3xl font-extrabold ${cfg.color} tracking-tight`}>
                {displayValue}
                <span className="text-xs font-semibold text-slate-500 ml-1">{cfg.unit}</span>
              </div>
              <div className="flex items-center">
                {renderSparkline(cfg)}
              </div>
            </div>

            <div className="progress-bar">
              <div
                className="progress-bar-fill"
                style={{
                  width: `${pct}%`,
                  background: pct > 90 ? '#f43f5e' : pct > 70 ? '#f59e0b' : '#10b981',
                }}
              />
            </div>

            {error && <p className="text-xs text-rose-400 mt-2 font-mono">{error}</p>}
          </div>
        );
      })}
    </div>
  );
}

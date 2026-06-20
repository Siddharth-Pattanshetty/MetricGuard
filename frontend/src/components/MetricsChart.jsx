/**
 * ==========================================================
 * MetricGuard — MetricsChart Component
 * ==========================================================
 * Recharts AreaCharts showing CPU, Memory, Disk, Network trends
 * with glowing gradient fades and custom glass tooltips.
 */

import { useState, useEffect, useCallback } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { fetchMetrics } from '../services/api';

const CHART_COLORS = {
  cpu_usage:     '#8b5cf6', // Violet
  memory_usage:  '#0ea5e9', // Sky
  disk_read:     '#f59e0b', // Amber
  network_rx:    '#10b981', // Emerald
};

const CHART_GOW_COLORS = {
  cpu_usage:     'rgba(139, 92, 246, 0.4)',
  memory_usage:  'rgba(14, 165, 233, 0.4)',
  disk_read:     'rgba(245, 158, 11, 0.4)',
  network_rx:    'rgba(16, 185, 129, 0.4)',
};

const CHART_LABELS = {
  cpu_usage:     'CPU Usage',
  memory_usage:  'Memory Usage',
  disk_read:     'Disk Read',
  network_rx:    'Network RX',
};

const CHART_UNITS = {
  cpu_usage:     '%',
  memory_usage:  '%',
  disk_read:     ' KB/s',
  network_rx:    ' KB/s',
};

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const data = payload[0];
  return (
    <div className="bg-[#090d16]/90 border border-slate-800/80 rounded-xl p-3 shadow-2xl backdrop-blur-md text-xs font-mono">
      <p className="text-slate-500 mb-1.5 font-sans font-semibold text-[10px] uppercase tracking-wider">{label}</p>
      <div className="flex items-center gap-2">
        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: data.color }} />
        <span className="text-slate-200 font-sans font-medium">{data.name}:</span>
        <span className="text-white font-bold">
          {typeof data.value === 'number' ? data.value.toFixed(2) : data.value}
          <span className="text-slate-400 text-[10px] font-normal ml-0.5">{CHART_UNITS[data.dataKey]}</span>
        </span>
      </div>
    </div>
  );
}

export default function MetricsChart() {
  const [limit, setLimit] = useState(50);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const raw = await fetchMetrics(limit);
      // Reverse so oldest is first (left side of chart)
      const formatted = raw
        .slice()
        .reverse()
        .map((m) => ({
          time: new Date(m.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          cpu_usage: m.cpu_usage,
          memory_usage: m.memory_usage,
          disk_read: m.disk_read,
          network_rx: m.network_rx,
        }));
      setData(formatted);
    } catch {
      /* Error handled silently — chart stays empty */
    } finally {
      setLoading(false);
    }
  }, [limit]);

  // Initial fetch and fetch on limit change
  useEffect(() => {
    setLoading(true);
    load();
  }, [limit, load]);

  // Auto-refresh interval
  useEffect(() => {
    const interval = setInterval(load, 15000);
    return () => clearInterval(interval);
  }, [load]);

  if (loading) {
    return (
      <div className="space-y-4">
        {/* Dynamic Range Selector Skeleton */}
        <div className="flex items-center justify-end bg-slate-900/40 p-2 px-4 rounded-xl border border-slate-800/60 max-w-max ml-auto h-10 w-[420px] skeleton" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton h-[360px] rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  const metrics = ['cpu_usage', 'memory_usage', 'disk_read', 'network_rx'];

  return (
    <div className="space-y-4">
      {/* Dynamic Range Selector */}
      <div className="timeframe-container ml-auto">
        <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mr-2 ml-1">Timeframe:</span>
        {[30, 50, 100, 200, 500, 1000].map((val) => (
          <button
            key={val}
            onClick={() => setLimit(val)}
            className={`timeframe-btn ${limit === val ? 'active' : 'inactive'}`}
          >
            {val} pts
          </button>
        ))}
      </div>

      {/* Grid of charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {metrics.map((key) => (
          <div key={key} className="glass-card p-6 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                {CHART_LABELS[key]}
              </h4>
              <span className="text-[10px] font-mono text-slate-500 bg-slate-950/40 px-2 py-0.5 rounded border border-slate-900">
                Last {data.length} pts
              </span>
            </div>
            <div className="w-full h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data} margin={{ top: 10, right: 5, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id={`gradient-${key}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={CHART_COLORS[key]} stopOpacity={0.25} />
                      <stop offset="95%" stopColor={CHART_COLORS[key]} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.03)" />
                  <XAxis
                    dataKey="time"
                    tick={{ fill: '#475569', fontSize: 9, fontFamily: 'monospace' }}
                    axisLine={{ stroke: 'rgba(148,163,184,0.05)' }}
                    tickLine={false}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    tick={{ fill: '#475569', fontSize: 9, fontFamily: 'monospace' }}
                    axisLine={{ stroke: 'rgba(148,163,184,0.05)' }}
                    tickLine={false}
                    width={40}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Area
                    type="monotone"
                    dataKey={key}
                    name={CHART_LABELS[key]}
                    stroke={CHART_COLORS[key]}
                    strokeWidth={2}
                    fillOpacity={1}
                    fill={`url(#gradient-${key})`}
                    activeDot={{ r: 4, fill: CHART_COLORS[key], strokeWidth: 0 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

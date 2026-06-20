/**
 * ==========================================================
 * MetricGuard — DependencyGraph Component
 * ==========================================================
 * React Flow interactive service dependency graph with auto-layout
 * and dynamic service health / impact status coordination.
 */

import { useState, useEffect } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { fetchServiceGraph, fetchServiceDashboard } from '../services/api';

// Custom node styling based on health/impact status
const nodeStyle = (status) => {
  let bg = 'linear-gradient(135deg, rgba(99,102,241,0.08), rgba(99,102,241,0.02))';
  let border = '1px solid rgba(99,102,241,0.2)';
  let color = '#c7d2fe';
  let shadow = '0 4px 12px rgba(99,102,241,0.04)';
  
  if (status === 'affected') {
    bg = 'linear-gradient(135deg, rgba(244,63,94,0.18), rgba(244,63,94,0.04))';
    border = '1.5px solid rgba(244,63,94,0.5)';
    color = '#f43f5e';
    shadow = '0 0 16px rgba(244,63,94,0.2)';
  } else if (status === 'impacted') {
    bg = 'linear-gradient(135deg, rgba(245,158,11,0.15), rgba(245,158,11,0.03))';
    border = '1px solid rgba(245,158,11,0.4)';
    color = '#f59e0b';
    shadow = '0 0 12px rgba(245,158,11,0.15)';
  } else if (status === 'healthy') {
    bg = 'linear-gradient(135deg, rgba(16,185,129,0.08), rgba(16,185,129,0.02))';
    border = '1px solid rgba(16,185,129,0.25)';
    color = '#a7f3d0';
    shadow = '0 4px 12px rgba(16,185,129,0.04)';
  }

  return {
    background: bg,
    border,
    borderRadius: '12px',
    padding: '10px 16px',
    color,
    fontSize: '11px',
    fontWeight: 700,
    fontFamily: 'monospace',
    boxShadow: shadow,
    minWidth: '140px',
    textAlign: 'center',
    letterSpacing: '0.03em',
    textTransform: 'uppercase',
  };
};

const edgeDefaults = {
  type: 'smoothstep',
  animated: true,
  style: { stroke: 'rgba(99, 102, 241, 0.25)', strokeWidth: 1.5 },
};

/**
 * Arrange nodes in a circular layout
 */
function autoLayout(services, affected, impacted, serviceHealthMap) {
  const count = services.length;
  const cx = 350, cy = 250;
  const radius = Math.max(160, count * 32);

  return services.map((name, i) => {
    const angle = (2 * Math.PI * i) / count - Math.PI / 2;
    
    // Determine status
    let status = 'healthy';
    if (name === affected) {
      status = 'affected';
    } else if (impacted.includes(name)) {
      status = 'impacted';
    } else {
      const hStatus = (serviceHealthMap[name] || 'healthy').toLowerCase();
      if (hStatus === 'degraded') status = 'impacted';
      else if (hStatus === 'unhealthy') status = 'affected';
    }

    const dotBg = 
      status === 'affected' ? 'bg-rose-500 animate-pulse' :
      status === 'impacted' ? 'bg-amber-500 animate-pulse' : 'bg-emerald-500';

    return {
      id: name,
      data: { 
        label: (
          <div className="flex items-center justify-center gap-2">
            <span className={`w-1.5 h-1.5 rounded-full ${dotBg}`} />
            <span>{name}</span>
          </div>
        )
      },
      position: {
        x: cx + radius * Math.cos(angle),
        y: cy + radius * Math.sin(angle),
      },
      style: nodeStyle(status),
    };
  });
}

export default function DependencyGraph() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [graphData, dashboardData] = await Promise.all([
          fetchServiceGraph(),
          fetchServiceDashboard()
        ]);

        const services = graphData.services || [];
        const graph = graphData.graph || {};
        
        const affected = dashboardData?.affected_service;
        const impacted = dashboardData?.impacted_services || [];
        
        // Build service health map
        const serviceHealthMap = {};
        if (dashboardData?.service_health) {
          dashboardData.service_health.forEach(sh => {
            serviceHealthMap[sh.service_name] = sh.status;
          });
        }

        // Create nodes with circular auto-layout and status styling
        const layoutNodes = autoLayout(services, affected, impacted, serviceHealthMap);
        setNodes(layoutNodes);

        // Create edges from adjacency list
        const newEdges = [];
        Object.entries(graph).forEach(([source, targets]) => {
          (targets || []).forEach((target) => {
            const isSourceImpacted = source === affected || impacted.includes(source);
            const isTargetImpacted = target === affected || impacted.includes(target);
            
            // If both nodes are impacted/affected, color the line orange/red
            const edgeStyle = (isSourceImpacted && isTargetImpacted)
              ? { stroke: 'rgba(244, 63, 94, 0.45)', strokeWidth: 2 }
              : (isSourceImpacted || isTargetImpacted)
              ? { stroke: 'rgba(245, 158, 11, 0.35)', strokeWidth: 1.5 }
              : edgeDefaults.style;

            newEdges.push({
              id: `${source}-${target}`,
              source,
              target,
              ...edgeDefaults,
              style: edgeStyle,
            });
          });
        });
        setEdges(newEdges);
      } catch {
        /* empty */
      } finally {
        setLoading(false);
      }
    })();
  }, [setNodes, setEdges]);

  if (loading) return <div className="skeleton h-[580px] rounded-2xl" />;

  if (!nodes.length) {
    return (
      <div className="glass-card p-8 text-center border border-slate-900">
        <p className="text-slate-500 text-xs italic">No service graph data available</p>
      </div>
    );
  }

  return (
    <div className="glass-card p-0 overflow-hidden border border-slate-900 shadow-2xl relative" style={{ height: '580px' }}>
      {/* Topology Legend */}
      <div className="absolute top-4 left-4 z-10 bg-slate-950/80 border border-slate-900/60 rounded-xl p-3 flex flex-col gap-2 backdrop-blur-md">
        <p className="text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-0.5">Topology Legend</p>
        <div className="flex items-center gap-2 text-[10px]">
          <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
          <span className="text-slate-300 font-medium font-sans">Root Failure Origin</span>
        </div>
        <div className="flex items-center gap-2 text-[10px]">
          <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
          <span className="text-slate-300 font-medium font-sans">Downstream Impacted</span>
        </div>
        <div className="flex items-center gap-2 text-[10px]">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          <span className="text-slate-300 font-medium font-sans">Operational / Healthy</span>
        </div>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        fitViewOptions={{ padding: 0.25 }}
        minZoom={0.3}
        maxZoom={2}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="rgba(148,163,184,0.03)" gap={24} size={1} />
        <Controls />
        <MiniMap
          nodeColor={(n) => {
            if (n.style?.color === '#f43f5e') return 'rgba(244, 63, 94, 0.4)';
            if (n.style?.color === '#f59e0b') return 'rgba(245, 158, 11, 0.4)';
            return 'rgba(16, 185, 129, 0.2)';
          }}
          maskColor="rgba(3, 7, 18, 0.85)"
          className="border border-slate-900/60 rounded-xl shadow-2xl"
        />
      </ReactFlow>
    </div>
  );
}

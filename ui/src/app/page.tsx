'use client';

import React, { useState, useEffect, useRef } from 'react';

interface GraphNode {
  id: string;
  type: string;
  name: string;
  statement?: string;
  status?: string;
  tier?: string;
  metadata?: any;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

interface GraphEdge {
  source_id: string;
  target_id: string;
  type: string;
  confidence: number;
  provenance: any;
}

export default function Home() {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  
  // API connection
  const [apiLive, setApiLive] = useState(false);
  const [apiToken, setApiToken] = useState('test_token');
  
  // Filtering states
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('ALL');
  
  // Panel Inputs
  const [arxivId, setArxivId] = useState('2303.1234');
  const [ingestLoading, setIngestLoading] = useState(false);
  const [ingestResult, setIngestResult] = useState<string | null>(null);

  // SMT inputs
  const [smtName, setSmtName] = useState('Fermat Last Case mod 5');
  const [smtEquation, setSmtEquation] = useState('x^2 + y^2 == z^2');
  const [smtModulus, setSmtModulus] = useState(5);
  const [smtVars, setSmtVars] = useState('x, y, z');
  const [smtLoading, setSmtLoading] = useState(false);

  // MCTS inputs
  const [proofName, setProofName] = useState('Identity Add and Mul');
  const [proofStart, setProofStart] = useState('x * 1 + 0');
  const [proofTarget, setProofTarget] = useState('x');
  const [proofVars, setProofVars] = useState('{"x": "Int"}');
  const [proofLoading, setProofLoading] = useState(false);

  // Canvas pan & zoom states
  const [pan, setPan] = useState({ x: 400, y: 300 });
  const [zoom, setZoom] = useState(1.0);
  const [isDraggingCanvas, setIsDraggingCanvas] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [draggedNodeId, setDraggedNodeId] = useState<string | null>(null);

  const svgRef = useRef<SVGSVGElement | null>(null);

  // Load Graph Data
  const fetchGraph = async () => {
    try {
      const res = await fetch('http://localhost:8000/graph', {
        headers: { 'Authorization': `Bearer ${apiToken}` }
      });
      if (res.ok) {
        const data = await res.json();
        // Initialize positions if not present
        const currentNodes = data.nodes.map((node: any, idx: number) => {
          const angle = (idx / data.nodes.length) * 2 * Math.PI;
          const radius = 150 + Math.random() * 50;
          return {
            ...node,
            x: node.x ?? (400 + radius * Math.cos(angle)),
            y: node.y ?? (300 + radius * Math.sin(angle)),
            vx: 0,
            vy: 0
          };
        });
        setNodes(currentNodes);
        setEdges(data.edges);
        setApiLive(true);
      } else {
        setApiLive(false);
      }
    } catch (e) {
      setApiLive(false);
    }
  };

  // Perform continuous graph layout simulation (Basic Force-Directed)
  useEffect(() => {
    let animationId: number;

    const tick = () => {
      setNodes(prevNodes => {
        if (prevNodes.length === 0) return prevNodes;

        // Clone nodes to update velocities and positions
        const nextNodes = prevNodes.map(n => ({ ...n, vx: n.vx || 0, vy: n.vy || 0 }));
        const nodeMap = new Map(nextNodes.map(n => [n.id, n]));

        const kRepulsion = 1500;
        const kAttraction = 0.04;
        const center = { x: 400, y: 300 };

        // 1. Repulsion between all nodes
        for (let i = 0; i < nextNodes.length; i++) {
          const n1 = nextNodes[i];
          if (n1.id === draggedNodeId) continue;
          
          for (let j = i + 1; j < nextNodes.length; j++) {
            const n2 = nextNodes[j];
            const dx = (n1.x || 0) - (n2.x || 0);
            const dy = (n1.y || 0) - (n2.y || 0);
            const dist = Math.sqrt(dx * dx + dy * dy) || 1.0;

            if (dist < 400) {
              const force = kRepulsion / (dist * dist);
              const fx = (dx / dist) * force;
              const fy = (dy / dist) * force;

              n1.vx! += fx;
              n1.vy! += fy;
              n2.vx! -= fx;
              n2.vy! -= fy;
            }
          }

          // Center gravity force
          const dxCenter = center.x - (n1.x || 0);
          const dyCenter = center.y - (n1.y || 0);
          n1.vx! += dxCenter * 0.005;
          n1.vy! += dyCenter * 0.005;
        }

        // 2. Attraction along edges
        edges.forEach(edge => {
          const n1 = nodeMap.get(edge.source_id);
          const n2 = nodeMap.get(edge.target_id);

          if (n1 && n2) {
            const dx = (n2.x || 0) - (n1.x || 0);
            const dy = (n2.y || 0) - (n1.y || 0);
            const dist = Math.sqrt(dx * dx + dy * dy) || 1.0;

            const force = kAttraction * (dist - 100);
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;

            if (n1.id !== draggedNodeId) {
              n1.vx! += fx;
              n1.vy! += fy;
            }
            if (n2.id !== draggedNodeId) {
              n2.vx! -= fx;
              n2.vy! -= fy;
            }
          }
        });

        // 3. Update positions using velocity + friction damping
        return nextNodes.map(n => {
          if (n.id === draggedNodeId) return n; // Keep dragged node at pointer position
          const friction = 0.8;
          const nextX = (n.x || 0) + n.vx! * friction;
          const nextY = (n.y || 0) + n.vy! * friction;
          
          return {
            ...n,
            x: nextX,
            y: nextY,
            vx: n.vx! * 0.4,
            vy: n.vy! * 0.4
          };
        });
      });

      animationId = requestAnimationFrame(tick);
    };

    animationId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animationId);
  }, [edges, draggedNodeId]);

  // Initial load
  useEffect(() => {
    fetchGraph();
    const interval = setInterval(fetchGraph, 5000);
    return () => clearInterval(interval);
  }, [apiToken]);

  // Handle Drag on Canvas
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target instanceof SVGElement && e.target.tagName === 'svg') {
      setIsDraggingCanvas(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDraggingCanvas) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    } else if (draggedNodeId) {
      // Move dragged node relative to SVG coordinates
      const rect = svgRef.current?.getBoundingClientRect();
      if (rect) {
        // Convert screen position to local SVG coordinates based on current pan and zoom
        const clientX = e.clientX - rect.left;
        const clientY = e.clientY - rect.top;
        
        const localX = (clientX - pan.x) / zoom;
        const localY = (clientY - pan.y) / zoom;

        setNodes(prev => prev.map(n => n.id === draggedNodeId ? { ...n, x: localX, y: localY } : n));
      }
    }
  };

  const handleMouseUp = () => {
    setIsDraggingCanvas(false);
    setDraggedNodeId(null);
  };

  const handleZoom = (factor: number) => {
    setZoom(prev => Math.min(Math.max(prev + factor, 0.2), 3.0));
  };

  // Trigger Ingestion
  const handleIngest = async () => {
    setIngestLoading(true);
    setIngestResult(null);
    try {
      const res = await fetch('http://localhost:8000/ingest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiToken}`
        },
        body: JSON.stringify({ arxiv_id: arxivId })
      });
      if (res.ok) {
        const data = await res.json();
        setIngestResult(`Success! Extracted ${data.claims_extracted} claims, ${data.concepts_extracted} concepts.`);
        fetchGraph();
      } else {
        setIngestResult(`Failed: ${res.statusText}`);
      }
    } catch (err: any) {
      setIngestResult(`Error: ${err.message}`);
    }
    setIngestLoading(false);
  };

  // Trigger SMT Check
  const handleSmtCheck = async () => {
    setSmtLoading(true);
    try {
      const variableList = smtVars.split(',').map(v => v.strip ? v.strip() : v.trim());
      const res = await fetch('http://localhost:8000/verify/conjecture', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiToken}`
        },
        body: JSON.stringify({
          conjecture_name: smtName,
          equation: smtEquation,
          modulus: smtModulus,
          variables: variableList
        })
      });
      if (res.ok) {
        fetchGraph();
      }
    } catch (e) {
      console.error(e);
    }
    setSmtLoading(false);
  };

  // Trigger Proof Verification (MCTS)
  const handleProofCheck = async () => {
    setProofLoading(true);
    try {
      const parsedVars = JSON.parse(proofVars);
      const res = await fetch('http://localhost:8000/verify/proof', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiToken}`
        },
        body: JSON.stringify({
          theorem_name: proofName,
          start_expression: proofStart,
          target_expression: proofTarget,
          variables: parsedVars
        })
      });
      if (res.ok) {
        fetchGraph();
      }
    } catch (e) {
      console.error(e);
    }
    setProofLoading(false);
  };

  // Filtering
  const filteredNodes = nodes.filter(node => {
    const matchesSearch = node.name.toLowerCase().includes(search.toLowerCase()) || 
      (node.statement && node.statement.toLowerCase().includes(search.toLowerCase()));
    
    const matchesType = filterType === 'ALL' || node.type === filterType;
    return matchesSearch && matchesType;
  });

  const nodeColor = (type: string) => {
    switch (type) {
      case 'MathematicalClaimNode': return '#059669'; // Emerald
      case 'PublicationNode': return '#4f46e5';       // Indigo
      case 'ConceptNode': return '#2563eb';           // Blue
      default: return '#0d9488';                      // Teal
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 font-sans text-slate-100">
      
      {/* LEFT CONTROL SIDEBAR */}
      <div className="w-80 border-r border-slate-800 bg-slate-900/90 flex flex-col p-4 space-y-4 overflow-y-auto shrink-0">
        
        {/* Brand & Connection info */}
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center justify-between">
            AXIOM Canvas
            <span className={`inline-block w-3 h-3 rounded-full ${apiLive ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
          </h1>
          <p className="text-xs text-slate-400 mt-1">Autonomous eXploration of Ideas, Observations & Models</p>
        </div>

        {/* API Authentication Config */}
        <div className="border border-slate-800 rounded bg-slate-950 p-2 text-xs">
          <label className="block text-slate-400 mb-1">API Token Header</label>
          <input 
            type="text" 
            className="w-full bg-slate-900 border border-slate-800 rounded p-1 text-slate-100" 
            value={apiToken}
            onChange={(e) => setApiToken(e.target.value)}
          />
        </div>

        {/* EIE Paper Ingestion */}
        <div className="border border-slate-800 rounded bg-slate-950 p-3 space-y-2">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400">R1: Ingest Literature</h2>
          <div className="space-y-1">
            <label className="text-2xs text-slate-500">arXiv Preprint Identifier</label>
            <input 
              type="text" 
              className="w-full bg-slate-900 border border-slate-800 rounded p-1 text-xs text-slate-100"
              value={arxivId}
              onChange={(e) => setArxivId(e.target.value)}
            />
          </div>
          <button 
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-xs font-medium py-1.5 rounded disabled:opacity-50"
            disabled={ingestLoading}
            onClick={handleIngest}
          >
            {ingestLoading ? 'Ingesting...' : 'Fetch & Parse'}
          </button>
          {ingestResult && <p className="text-2xs text-slate-400 mt-1 bg-slate-900 p-1 rounded break-words">{ingestResult}</p>}
        </div>

        {/* AVT SMT Solver Conjecture Verification */}
        <div className="border border-slate-800 rounded bg-slate-950 p-3 space-y-2">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400">R3: SMT Solver Sweeps</h2>
          <div className="space-y-1">
            <input 
              type="text" 
              placeholder="Conjecture Name"
              className="w-full bg-slate-900 border border-slate-800 rounded p-1 text-xs text-slate-100"
              value={smtName}
              onChange={(e) => setSmtName(e.target.value)}
            />
            <input 
              type="text" 
              placeholder="Equation (e.g. x + y == z)"
              className="w-full bg-slate-900 border border-slate-800 rounded p-1 text-xs text-slate-100"
              value={smtEquation}
              onChange={(e) => setSmtEquation(e.target.value)}
            />
            <div className="flex space-x-1">
              <input 
                type="number" 
                placeholder="Modulus"
                className="w-1/2 bg-slate-900 border border-slate-800 rounded p-1 text-xs text-slate-100"
                value={smtModulus}
                onChange={(e) => setSmtModulus(Number(e.target.value))}
              />
              <input 
                type="text" 
                placeholder="Vars (x, y)"
                className="w-1/2 bg-slate-900 border border-slate-800 rounded p-1 text-xs text-slate-100"
                value={smtVars}
                onChange={(e) => setSmtVars(e.target.value)}
              />
            </div>
          </div>
          <button 
            className="w-full bg-emerald-600 hover:bg-emerald-700 text-xs font-medium py-1.5 rounded disabled:opacity-50"
            disabled={smtLoading}
            onClick={handleSmtCheck}
          >
            {smtLoading ? 'Running SMT...' : 'Z3 Counterexample Scan'}
          </button>
        </div>

        {/* MCTS & LRK Proof Search */}
        <div className="border border-slate-800 rounded bg-slate-950 p-3 space-y-2">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400">R5: MCTS Algebra Proofs</h2>
          <div className="space-y-1">
            <input 
              type="text" 
              placeholder="Theorem Name"
              className="w-full bg-slate-900 border border-slate-800 rounded p-1 text-xs text-slate-100"
              value={proofName}
              onChange={(e) => setProofName(e.target.value)}
            />
            <input 
              type="text" 
              placeholder="Start expr (e.g. x + (y + 0))"
              className="w-full bg-slate-900 border border-slate-800 rounded p-1 text-xs text-slate-100"
              value={proofStart}
              onChange={(e) => setProofStart(e.target.value)}
            />
            <input 
              type="text" 
              placeholder="Target expr (e.g. x + y)"
              className="w-full bg-slate-900 border border-slate-800 rounded p-1 text-xs text-slate-100"
              value={proofTarget}
              onChange={(e) => setProofTarget(e.target.value)}
            />
            <input 
              type="text" 
              placeholder="Variables json dictionary"
              className="w-full bg-slate-900 border border-slate-800 rounded p-1 text-xs text-slate-100"
              value={proofVars}
              onChange={(e) => setProofVars(e.target.value)}
            />
          </div>
          <button 
            className="w-full bg-blue-600 hover:bg-blue-700 text-xs font-medium py-1.5 rounded disabled:opacity-50"
            disabled={proofLoading}
            onClick={handleProofCheck}
          >
            {proofLoading ? 'Searching Proof...' : 'MCTS Search & Export Lean'}
          </button>
        </div>

      </div>

      {/* CENTER INTERACTIVE CANVAS AREA */}
      <div className="flex-1 relative flex flex-col min-w-0">
        
        {/* GRAPH FILTER HEADER */}
        <div className="absolute top-4 left-4 right-4 z-10 flex space-x-2 bg-slate-900/80 border border-slate-800 p-2 rounded backdrop-blur max-w-lg shadow-lg">
          <input 
            type="text" 
            placeholder="Search claims or statements..." 
            className="flex-1 bg-slate-950 border border-slate-800 rounded p-1 text-xs text-slate-100"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select 
            className="bg-slate-950 border border-slate-800 rounded p-1 text-xs text-slate-300"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="ALL">All Node Types</option>
            <option value="MathematicalClaimNode">Mathematical Claims</option>
            <option value="ConceptNode">Definitions/Concepts</option>
            <option value="PublicationNode">Papers/Publications</option>
          </select>
        </div>

        {/* CANVAS CONTROLS */}
        <div className="absolute bottom-4 right-4 z-10 flex flex-col space-y-1">
          <button className="bg-slate-800 hover:bg-slate-700 text-white font-bold p-2 text-xs rounded border border-slate-700 shadow" onClick={() => handleZoom(0.1)}>+</button>
          <button className="bg-slate-800 hover:bg-slate-700 text-white font-bold p-2 text-xs rounded border border-slate-700 shadow" onClick={() => handleZoom(-0.1)}>-</button>
          <button className="bg-slate-800 hover:bg-slate-700 text-slate-400 p-2 text-xs rounded border border-slate-700 shadow" onClick={() => setPan({ x: 400, y: 300 })}>↺</button>
        </div>

        {/* INTERACTIVE SVG GRID */}
        <svg 
          ref={svgRef}
          className="w-full h-full cursor-grab active:cursor-grabbing bg-slate-950/20"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          {/* Grid Background */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255, 255, 255, 0.02)" strokeWidth="1" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />

          {/* Transformation Layer */}
          <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
            
            {/* 1. Render Lines/Edges */}
            {edges.map((edge, idx) => {
              const fromNode = nodes.find(n => n.id === edge.source_id);
              const toNode = nodes.find(n => n.id === edge.target_id);

              if (fromNode && toNode) {
                return (
                  <line 
                    key={idx}
                    x1={fromNode.x || 0}
                    y1={fromNode.y || 0}
                    x2={toNode.x || 0}
                    y2={toNode.y || 0}
                    stroke="rgba(255, 255, 255, 0.15)"
                    strokeWidth="1.5"
                    strokeDasharray={edge.type === 'REFUTES' ? '4' : '0'}
                  />
                );
              }
              return null;
            })}

            {/* 2. Render Nodes */}
            {filteredNodes.map((node) => {
              const borderStyles = node.status === 'VERIFIED' ? 'stroke-emerald-400 stroke-2' : 
                                   node.status === 'REFUTED' ? 'stroke-red-400 stroke-2' : 'stroke-slate-500';
              const isSelected = selectedNode?.id === node.id;

              return (
                <g 
                  key={node.id} 
                  transform={`translate(${node.x || 0}, ${node.y || 0})`}
                  className="cursor-pointer group"
                  onClick={() => setSelectedNode(node)}
                  onMouseDown={(e) => {
                    e.stopPropagation();
                    setDraggedNodeId(node.id);
                  }}
                >
                  <circle 
                    r={isSelected ? 16 : 12} 
                    fill={nodeColor(node.type)} 
                    className={`${borderStyles} transition-all duration-200 group-hover:scale-125`}
                  />
                  {/* Small Label Text */}
                  <text
                    y={25}
                    textAnchor="middle"
                    fill="#cbd5e1"
                    fontSize="10"
                    className="select-none font-medium opacity-80 group-hover:opacity-100"
                  >
                    {node.name.length > 15 ? `${node.name.substring(0, 15)}...` : node.name}
                  </text>
                </g>
              );
            })}

          </g>
        </svg>

      </div>

      {/* RIGHT DETAILS SIDEBAR */}
      <div className="w-80 border-l border-slate-800 bg-slate-900/90 flex flex-col p-4 space-y-4 overflow-y-auto shrink-0">
        <h2 className="text-sm font-semibold tracking-wider uppercase text-slate-400 border-b border-slate-800 pb-2">Properties & Proof</h2>
        
        {selectedNode ? (
          <div className="space-y-4">
            <div>
              <span className="text-2xs uppercase tracking-wide px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                {selectedNode.type.replace('Node', '')}
              </span>
              <h3 className="text-lg font-bold text-white mt-2 leading-snug">{selectedNode.name}</h3>
            </div>

            {selectedNode.statement && (
              <div className="bg-slate-950 p-2.5 rounded border border-slate-800 space-y-1">
                <h4 className="text-2xs font-semibold text-slate-500 uppercase">Statement</h4>
                <p className="text-xs font-mono text-emerald-300 select-all">{selectedNode.statement}</p>
              </div>
            )}

            {selectedNode.status && (
              <div className="flex space-x-2">
                <div className="w-1/2 bg-slate-950 p-2 rounded border border-slate-800 text-center">
                  <span className="text-2xs text-slate-500 uppercase block">Status</span>
                  <span className={`text-xs font-semibold ${selectedNode.status === 'VERIFIED' ? 'text-emerald-400' : selectedNode.status === 'REFUTED' ? 'text-red-400' : 'text-yellow-400'}`}>
                    {selectedNode.status}
                  </span>
                </div>
                <div className="w-1/2 bg-slate-950 p-2 rounded border border-slate-800 text-center">
                  <span className="text-2xs text-slate-500 uppercase block">Tier</span>
                  <span className="text-xs font-mono text-slate-300">
                    {selectedNode.tier ? selectedNode.tier.replace('TIER_', '') : '0'}
                  </span>
                </div>
              </div>
            )}

            {/* Proof Steps Metadata */}
            {selectedNode.metadata?.proof_path && (
              <div className="bg-slate-950 p-3 rounded border border-slate-800 space-y-2">
                <h4 className="text-2xs font-semibold text-slate-500 uppercase">MCTS Proof Steps</h4>
                <ol className="text-xs font-mono space-y-1 list-decimal list-inside text-blue-300">
                  {selectedNode.metadata.proof_path.map((step: any, idx: number) => (
                    <li key={idx} className="border-b border-slate-900 pb-1 last:border-0">
                      <span className="text-slate-500">{step[0]}: </span>
                      <span>{step[1]}</span>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {/* Compiler Status */}
            {selectedNode.metadata?.compiler_status && (
              <div className="bg-slate-950 p-2.5 rounded border border-slate-800 space-y-1 text-xs">
                <h4 className="text-2xs font-semibold text-slate-500 uppercase">Lean Compiler Verification</h4>
                <p className="font-mono text-slate-300 text-2xs bg-slate-900 p-1 rounded border border-slate-950">
                  {selectedNode.metadata.compiler_status}
                </p>
                {selectedNode.metadata.lean_file && (
                  <p className="text-3xs text-slate-500 truncate mt-1">Path: {selectedNode.metadata.lean_file}</p>
                )}
              </div>
            )}

            {/* RAW DATABASE JSON */}
            <details className="bg-slate-950 rounded border border-slate-800 text-xs">
              <summary className="cursor-pointer p-2 font-medium text-slate-400 select-none">Show Raw Node Record</summary>
              <pre className="p-2 overflow-x-auto text-3xs font-mono text-slate-500 select-all bg-slate-950 border-t border-slate-900">
                {JSON.stringify(selectedNode, null, 2)}
              </pre>
            </details>

          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-48 text-center text-slate-500 space-y-2">
            <svg className="w-8 h-8 opacity-40 animate-pulse text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
            </svg>
            <p className="text-xs">Click a node on the canvas to inspect verification logs and proof histories.</p>
          </div>
        )}

      </div>

    </div>
  );
}

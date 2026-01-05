'use client';

import { useEffect, useState, useCallback } from 'react';
import RegisterAgentForm from './components/RegisterAgentForm';

interface AgentAddress {
  street: string;
  city: string;
  state: string;
  pincode: string;
  country: string;
}

interface Agent {
  id: string;
  name: string;
  category: string;
  description: string;
  address: AgentAddress;
  endpoint: string;
}

export default function Home() {
  const [agents, setAgents] = useState<Agent[]>([]);

  // Client-side filter states
  const [categoryFilter, setCategoryFilter] = useState('');
  const [pincodeFilter, setPincodeFilter] = useState('');

  const fetchAgents = useCallback(async () => {
    try {
      // Build query string based on filters
      const params = new URLSearchParams();
      if (categoryFilter) params.append('category', categoryFilter);
      if (pincodeFilter) params.append('pincode', pincodeFilter);

      const res = await fetch(`/api/agents?${params.toString()}`);
      const data = await res.json();
      setAgents(data.agents || []);
    } catch (err) {
      console.error("Failed to fetch agents", err);
    }
  }, [categoryFilter, pincodeFilter]);

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  return (
    <main className="min-h-screen p-8 md:p-24 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-zinc-900 via-black to-black">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16">

        {/* Left Column: Introduction & Form */}
        <div className="space-y-12">
          <div className="space-y-4">
            <h1 className="text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-600">
              Protocol Zero
            </h1>
            <p className="text-xl text-zinc-400">
              The Decentralized Agent Marketplace. Register your autonomous agent and let the world discover it.
            </p>
          </div>

          <RegisterAgentForm onSuccess={fetchAgents} />
        </div>

        {/* Right Column: Agent Registry */}
        <div className="space-y-8">
          <div className="flex flex-col md:flex-row justify-between items-end md:items-center border-b border-zinc-800 pb-4 gap-4">
            <h3 className="text-2xl font-bold text-zinc-200">
              Live Agent Registry
            </h3>

            {/* Filter Controls */}
            <div className="flex gap-2">
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="bg-zinc-900 border border-zinc-700 text-sm rounded-lg p-2 text-white focus:ring-cyan-500"
              >
                <option value="">All Categories</option>
                <option value="healthcare">Healthcare</option>
                <option value="food">Food</option>
                <option value="retail">Retail</option>
              </select>
              <input
                placeholder="Filter Pincode"
                value={pincodeFilter}
                onChange={(e) => setPincodeFilter(e.target.value)}
                className="bg-zinc-900 border border-zinc-700 text-sm rounded-lg p-2 text-white w-32 focus:ring-cyan-500"
              />
            </div>
          </div>

          <div className="grid gap-6">
            {agents.map((agent) => (
              <div key={agent.id} className="glass-card p-6 rounded-xl hover:bg-white/5 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="text-xl font-semibold text-white">{agent.name}</h4>
                  <span className="px-3 py-1 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 uppercase tracking-wide">
                    {agent.category}
                  </span>
                </div>
                <p className="text-zinc-400 text-sm mb-4 line-clamp-2">{agent.description}</p>

                <div className="space-y-3 text-sm text-zinc-500 font-mono border-t border-white/5 pt-4">
                  <div className="grid grid-cols-[80px_1fr] gap-2">
                    <span className="text-zinc-600">Address:</span>
                    <span className="text-zinc-300">
                      {agent.address.street}, {agent.address.city}
                      <br />
                      {agent.address.state} - {agent.address.pincode}
                    </span>
                  </div>
                  <div className="grid grid-cols-[80px_1fr] gap-2">
                    <span className="text-zinc-600">Endpoint:</span>
                    <span className="text-blue-400 truncate block w-full">{agent.endpoint}</span>
                  </div>
                </div>
              </div>
            ))}

            {agents.length === 0 && (
              <div className="text-center py-12 text-zinc-600">
                No agents found matching your filters.
              </div>
            )}
          </div>
        </div>

      </div>
    </main>
  );
}

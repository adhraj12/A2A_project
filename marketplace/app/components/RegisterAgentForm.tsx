'use client';

import { useState } from 'react';

export default function RegisterAgentForm({ onSuccess }: { onSuccess?: () => void }) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        setLoading(true);
        setError('');

        const formData = new FormData(e.currentTarget);

        // Construct the structured data object
        const data = {
            name: formData.get('name'),
            category: formData.get('category'),
            description: formData.get('description'),
            endpoint: formData.get('endpoint'),
            address: {
                street: formData.get('street'),
                city: formData.get('city'),
                state: formData.get('state'),
                pincode: formData.get('pincode'),
                country: formData.get('country') || 'India',
            }
        };

        try {
            const res = await fetch('/api/agents', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.error || 'Failed to register agent');
            }

            e.currentTarget.reset();
            if (onSuccess) onSuccess();
        } catch (err: any) {
            setError(err.message || 'Something went wrong.');
        } finally {
            setLoading(false);
        }
    }

    return (
        <form onSubmit={handleSubmit} className="glass-card p-8 rounded-2xl w-full max-w-lg space-y-6">
            <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-cyan-300">
                Register New Agent
            </h2>

            <div className="space-y-2">
                <label className="text-sm text-zinc-400">Agent Name</label>
                <input
                    name="name"
                    required
                    placeholder="e.g. Pune Chemist"
                    className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
                />
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                    <label className="text-sm text-zinc-400">Category</label>
                    <select
                        name="category"
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50 [&>option]:text-black"
                    >
                        <option value="healthcare">Healthcare</option>
                        <option value="food">Food & Dining</option>
                        <option value="retail">Retail</option>
                        <option value="services">Services</option>
                    </select>
                </div>
                <div className="space-y-2">
                    <label className="text-sm text-zinc-400">Endpoint URL</label>
                    <input
                        name="endpoint"
                        required
                        type="url"
                        placeholder="https://..."
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
                    />
                </div>
            </div>

            {/* Structured Address Section */}
            <div className="space-y-4 pt-2">
                <label className="text-sm font-semibold text-zinc-300 border-b border-white/10 pb-1 block">Location Details</label>

                <div className="space-y-2">
                    <input
                        name="street"
                        required
                        placeholder="Street Address (Shop No, Building...)"
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <input
                        name="city"
                        required
                        placeholder="City"
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
                    />
                    <input
                        name="state"
                        required
                        placeholder="State"
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <input
                        name="pincode"
                        required
                        placeholder="Pincode"
                        pattern="[0-9]{6}"
                        title="6 digit pincode"
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
                    />
                    <input
                        name="country"
                        defaultValue="India"
                        placeholder="Country"
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
                    />
                </div>
            </div>

            <div className="space-y-2">
                <label className="text-sm text-zinc-400">Description</label>
                <textarea
                    name="description"
                    className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white h-24 focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
                />
            </div>

            {error && <p className="text-red-400 text-sm">{error}</p>}

            <button
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-medium py-3 rounded-lg transition-all active:scale-[0.98]"
            >
                {loading ? 'Registering...' : 'Register Agent'}
            </button>
        </form>
    );
}

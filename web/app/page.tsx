"use client";
import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { motion } from 'framer-motion';

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      // The fetch URL is relative because next.config.ts handles the routing
      const res = await fetch('/api/race-telemetry/2024/Bahrain/Q');
      const json = await res.json();
      setData(json);
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  // Merge data for the chart
  const getChartData = () => {
    if (!data || !data.data) return [];
    const masterTrace = data.data[0]?.telemetry || [];
    return masterTrace.map((point: any, index: number) => {
      const merged: any = { distance: point.Distance };
      data.data.forEach((car: any) => {
        if (car.telemetry[index]) merged[car.driver] = car.telemetry[index].Speed;
      });
      return merged;
    });
  };

  return (
    <div className="min-h-screen bg-[#0E1117] text-white p-6 font-mono">
      <header className="flex justify-between items-center mb-8 border-b border-gray-800 pb-4">
        <h1 className="text-2xl font-bold text-blue-500">RB20 <span className="text-white">TELEMETRY</span></h1>
        <button onClick={fetchData} className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition">
          {loading ? "CONNECTING..." : "LOAD DATA"}
        </button>
      </header>

      {loading && (
        <div className="flex flex-col items-center justify-center h-64">
          <motion.div 
            animate={{ rotate: 360 }} 
            transition={{ repeat: Infinity, duration: 1 }} 
            className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full mb-4" 
          />
          <p className="text-gray-400 text-xs animate-pulse">WAKING UP THE ENGINE (This may take 50s on free tier)...</p>
        </div>
      )}

      {data && (
        <div className="bg-[#161b22] p-4 rounded border border-gray-800 h-[500px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={getChartData()}>
              <XAxis dataKey="distance" stroke="#555" />
              <YAxis domain={[0, 360]} stroke="#555" />
              <Tooltip contentStyle={{ backgroundColor: '#000' }} />
              <Legend />
              {data.data.map((car: any) => (
                <Line 
                  key={car.driver} 
                  type="monotone" 
                  dataKey={car.driver} 
                  stroke={car.color || '#fff'} 
                  dot={false} 
                  strokeWidth={car.driver === 'VER' ? 3 : 1}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
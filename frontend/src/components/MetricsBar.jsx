import React from 'react';
import { Clock, Coins, Layers, Scissors, ShieldCheck, Zap } from 'lucide-react';

export default function MetricsBar({ result }) {
  if (!result) return null;

  const mistakesPruned = result.abandoned_mistakes?.length || 0;
  const silentActionsCount = result.steps?.filter(s => s.step_type === 'silent_action').length || 0;
  const validStepsCount = result.steps?.filter(s => s.is_in_recommended_path).length || 0;
  const isLive = result.source_mode === 'live_ai_inference';

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-lg px-4 py-2.5 mb-5 flex flex-wrap items-center justify-between gap-3 text-xs">
      {/* Left: Engine Mode Badge */}
      <div className="flex items-center space-x-2.5">
        <span className="text-slate-400 font-medium">Pipeline:</span>
        {isLive ? (
          <span className="inline-flex items-center space-x-1.5 px-2 py-0.5 rounded bg-indigo-950/60 text-indigo-300 border border-indigo-800/60 font-mono text-[11px]">
            <Zap className="w-3 h-3 text-indigo-400" />
            <span>Live Vision ({result.model_name})</span>
          </span>
        ) : (
          <span className="inline-flex items-center space-x-1.5 px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-mono text-[11px]">
            <ShieldCheck className="w-3 h-3 text-emerald-400" />
            <span>Deterministic Ground-Truth</span>
          </span>
        )}
      </div>

      {/* Right: Inline Performance & Extraction Metrics */}
      <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-slate-400">
        {/* Latency */}
        <div className="flex items-center space-x-1.5">
          <Clock className="w-3.5 h-3.5 text-slate-500" />
          <span>Latency:</span>
          <span className="font-mono text-slate-200 font-medium">
            {result.processing_time_sec != null ? `${result.processing_time_sec}s` : '--'}
          </span>
        </div>

        <span className="text-slate-700 hidden sm:inline">•</span>

        {/* Cost & Tokens */}
        <div className="flex items-center space-x-1.5">
          <Coins className="w-3.5 h-3.5 text-slate-500" />
          <span>Cost:</span>
          <span className="font-mono text-emerald-400 font-medium">
            {typeof result.variable_cost_usd === 'number' ? `$${result.variable_cost_usd.toFixed(5)}` : '$0.00000'}
          </span>
          <span className="text-slate-500 text-[11px]">({result.token_usage?.total_tokens?.toLocaleString() || 0} tok)</span>
        </div>

        <span className="text-slate-700 hidden sm:inline">•</span>

        {/* Steps Count */}
        <div className="flex items-center space-x-1.5">
          <Layers className="w-3.5 h-3.5 text-slate-500" />
          <span>Steps:</span>
          <span className="font-mono text-slate-200 font-medium">{validStepsCount}</span>
          {silentActionsCount > 0 && (
            <span className="text-purple-400 text-[11px]">({silentActionsCount} silent)</span>
          )}
        </div>

        <span className="text-slate-700 hidden sm:inline">•</span>

        {/* Mistakes Pruned */}
        <div className="flex items-center space-x-1.5">
          <Scissors className="w-3.5 h-3.5 text-slate-500" />
          <span>Pruned:</span>
          <span className={`font-mono font-medium ${mistakesPruned > 0 ? 'text-amber-400' : 'text-slate-400'}`}>
            {mistakesPruned} mistake{mistakesPruned !== 1 ? 's' : ''}
          </span>
        </div>
      </div>
    </div>
  );
}

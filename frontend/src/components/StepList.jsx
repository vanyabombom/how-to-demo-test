import React, { useState } from 'react';
import StepCard from './StepCard';
import { Filter, CheckCircle2, AlertOctagon, FileText, Check, ListOrdered } from 'lucide-react';

export default function StepList({ result, onSeekTimestamp, activeTime }) {
  const [showAllSteps, setShowAllSteps] = useState(false);

  if (!result) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center text-slate-500">
        <FileText className="w-8 h-8 mx-auto mb-2 opacity-30 text-slate-400" />
        <p className="text-xs font-mono">Select a recording or upload an MP4 stream to inspect how-to steps.</p>
      </div>
    );
  }

  const allSteps = result.steps || [];
  const displaySteps = showAllSteps
    ? allSteps
    : allSteps.filter((s) => s.is_in_recommended_path);

  const hasMistakes = allSteps.some((s) => s.step_type === 'corrected_mistake');

  return (
    <div className="space-y-3.5">
      {/* Target Guide Metadata Card */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-lg p-4 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
          <h2 className="text-sm font-semibold text-white tracking-tight">
            {result.guide_title}
          </h2>

          {/* Toggle for Clean Path vs Mistakes */}
          {hasMistakes && (
            <button
              onClick={() => setShowAllSteps(!showAllSteps)}
              className="flex items-center space-x-1.5 px-2.5 py-1 rounded text-xs font-mono bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
            >
              <Filter className="w-3 h-3 text-slate-400" />
              <span>{showAllSteps ? 'Showing all steps' : 'Filter mistakes'}</span>
            </button>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs font-mono text-slate-400">
          <div className="flex items-center space-x-1">
            <span className="text-slate-500">Operation:</span>
            <span className="text-slate-200">{result.target_operation}</span>
          </div>
          <span className="text-slate-700 hidden sm:inline">•</span>
          <div className="flex items-center space-x-1">
            <span className="text-slate-500">Target App:</span>
            <span className="text-slate-200">{result.app_detected}</span>
          </div>
        </div>

        {/* Decline Alert (Missing context / validation error) */}
        {result.declined_to_conclude && (
          <div className="mt-3 p-3 rounded-md bg-rose-950/30 border border-rose-900/50 text-xs flex items-start space-x-2.5">
            <AlertOctagon className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-rose-300 mb-0.5">Execution Incomplete / Prerequisite Missing</div>
              <p className="leading-relaxed text-rose-200/90 font-mono text-[11px]">{result.decline_reason}</p>
            </div>
          </div>
        )}

        {/* Final Success state confirmation */}
        {!result.declined_to_conclude && result.final_success_achieved && result.final_success_evidence && (
          <div className="mt-3 p-2.5 rounded-md bg-emerald-950/30 border border-emerald-900/50 text-emerald-300 text-xs flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span className="font-mono text-[11px]">{result.final_success_evidence}</span>
          </div>
        )}
      </div>

      {/* Ordered Steps List */}
      <div>
        <div className="flex items-center justify-between mb-2 px-1">
          <div className="flex items-center space-x-1.5 text-xs font-medium text-slate-400 uppercase tracking-wider font-mono">
            <ListOrdered className="w-3.5 h-3.5 text-slate-500" />
            <span>Ordered Step Sequence ({displaySteps.length})</span>
          </div>
          <span className="text-[11px] font-mono text-slate-500">
            Click timestamp to seek video
          </span>
        </div>

        {displaySteps.map((step) => {
          const isCurrent =
            activeTime >= step.timestamp_keyframe_sec - 1 &&
            activeTime <= step.timestamp_keyframe_sec + 2;

          return (
            <StepCard
              key={step.step_number}
              step={step}
              isActive={isCurrent}
              onSeek={onSeekTimestamp}
            />
          );
        })}
      </div>

      {/* Final Configuration Summary */}
      {result.final_settings_summary && Object.keys(result.final_settings_summary).length > 0 && (
        <div className="bg-slate-900/70 border border-slate-800 rounded-lg p-3.5">
          <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-semibold mb-2 flex items-center space-x-1.5">
            <Check className="w-3.5 h-3.5 text-emerald-400" />
            <span>Applied Parameter Configuration</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono">
            {Object.entries(result.final_settings_summary).map(([key, value]) => (
              <div
                key={key}
                className="p-2 rounded bg-slate-950/60 border border-slate-800 flex items-center justify-between gap-2"
              >
                <span className="text-slate-400 truncate">{key}</span>
                <span className="text-slate-200 font-medium truncate bg-slate-800/80 px-1.5 py-0.5 rounded border border-slate-700/60 text-[11px]">
                  {String(value)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

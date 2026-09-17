import React, { useRef, useEffect, useState } from 'react';
import { Play, Pause, RotateCcw, Volume2, VolumeX, Maximize2, Film } from 'lucide-react';

export default function VideoPlayer({ videoUrl, seekTime, steps = [], onTimeUpdate }) {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isMuted, setIsMuted] = useState(true);

  useEffect(() => {
    if (videoRef.current && typeof seekTime === 'number' && !isNaN(seekTime)) {
      videoRef.current.currentTime = seekTime;
      videoRef.current.play().catch(() => {});
      setIsPlaying(true);
    }
  }, [seekTime]);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.currentTime = 0;
      setCurrentTime(0);
      setIsPlaying(false);
    }
  }, [videoUrl]);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
      setIsPlaying(false);
    } else {
      videoRef.current.play().catch(() => {});
      setIsPlaying(true);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const cur = videoRef.current.currentTime;
      setCurrentTime(cur);
      if (onTimeUpdate) onTimeUpdate(cur);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration || 0);
    }
  };

  const handleSeek = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    const newTime = pos * duration;
    if (videoRef.current) {
      videoRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const formatTime = (sec) => {
    if (isNaN(sec) || !isFinite(sec)) return '00:00';
    const m = Math.floor(Math.max(0, sec) / 60);
    const s = Math.floor(Math.max(0, sec) % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  // Extract clean filename from URL
  const filename = videoUrl ? videoUrl.split('/').pop() : 'No stream loaded';

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden shadow-sm lg:sticky lg:top-20">
      {/* Player Topbar */}
      <div className="px-3.5 py-2 border-b border-slate-800/80 bg-slate-950/60 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2 text-slate-300 font-mono text-[11px] truncate">
          <Film className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          <span className="truncate">{filename}</span>
        </div>
        <div className="flex items-center space-x-2 text-[11px] font-mono text-slate-500 shrink-0">
          <span>{duration > 0 ? `${duration.toFixed(1)}s` : '--'}</span>
          <span className={`w-1.5 h-1.5 rounded-full ${isPlaying ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`} />
        </div>
      </div>

      {/* Video Viewport */}
      <div className="relative aspect-video bg-black flex items-center justify-center group">
        {videoUrl ? (
          <video
            ref={videoRef}
            src={videoUrl}
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
            onEnded={() => setIsPlaying(false)}
            muted={isMuted}
            playsInline
            className="w-full h-full object-contain cursor-pointer"
            onClick={togglePlay}
          />
        ) : (
          <div className="text-xs text-slate-500 font-mono">No video selected</div>
        )}

        {/* Play Overlay */}
        {!isPlaying && videoUrl && (
          <div
            onClick={togglePlay}
            className="absolute inset-0 flex items-center justify-center bg-black/40 cursor-pointer transition hover:bg-black/30"
          >
            <div className="w-12 h-12 rounded-full bg-slate-900/90 border border-slate-700/80 flex items-center justify-center text-slate-200 shadow-md transition hover:scale-105 hover:bg-slate-800">
              <Play className="w-5 h-5 ml-0.5 text-slate-200" />
            </div>
          </div>
        )}
      </div>

      {/* Scrubber & Controls */}
      <div className="p-3 bg-slate-950/90 border-t border-slate-800">
        {/* Timeline Bar with Markers */}
        <div
          onClick={handleSeek}
          className="relative w-full h-2 bg-slate-800/90 rounded cursor-pointer mb-2.5 group"
        >
          {/* Active Elapsed Fill */}
          <div
            className="absolute top-0 left-0 h-full bg-blue-500/90 rounded"
            style={{ width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%` }}
          />

          {/* Markers for Each Extracted Step */}
          {duration > 0 && steps.map((step) => {
            const stepPos = (step.timestamp_keyframe_sec / duration) * 100;
            let markerBg = 'bg-blue-400';
            if (step.step_type === 'silent_action') markerBg = 'bg-purple-400';
            if (step.step_type === 'corrected_mistake') markerBg = 'bg-amber-400';
            if (step.step_type === 'missing_step_gap') markerBg = 'bg-rose-400';

            return (
              <div
                key={step.step_number}
                title={`Step ${step.step_number}: ${step.title} (${step.timestamp_start})`}
                className={`absolute top-[-2px] w-1.5 h-3 rounded-xs ${markerBg} transform -translate-x-1/2 cursor-pointer transition hover:scale-150 z-10`}
                style={{ left: `${Math.min(99, Math.max(1, stepPos))}%` }}
                onClick={(e) => {
                  e.stopPropagation();
                  if (videoRef.current) {
                    videoRef.current.currentTime = step.timestamp_keyframe_sec;
                    videoRef.current.play().catch(() => {});
                    setIsPlaying(true);
                  }
                }}
              />
            );
          })}
        </div>

        {/* Controls Bar */}
        <div className="flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center space-x-2">
            <button
              onClick={togglePlay}
              className="p-1 rounded text-slate-300 hover:text-white transition"
              title={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </button>

            <button
              onClick={() => {
                if (videoRef.current) {
                  videoRef.current.currentTime = 0;
                  setCurrentTime(0);
                }
              }}
              className="p-1 rounded text-slate-400 hover:text-white transition"
              title="Restart"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>

            <span className="text-slate-600 font-mono text-[10px]">|</span>

            {/* Time Indicator */}
            <span className="font-mono text-slate-300 text-xs tracking-tight">
              {formatTime(currentTime)} <span className="text-slate-600">/</span> {formatTime(duration)}
            </span>
          </div>

          <div className="flex items-center space-x-2">
            {/* Audio Mute Toggle */}
            <button
              onClick={() => {
                if (videoRef.current) {
                  const nextMuted = !isMuted;
                  videoRef.current.muted = nextMuted;
                  setIsMuted(nextMuted);
                }
              }}
              className="p-1 rounded text-slate-400 hover:text-white transition"
              title={isMuted ? 'Unmute audio' : 'Mute audio'}
            >
              {isMuted ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
            </button>

            {/* Fullscreen */}
            <button
              onClick={() => {
                if (videoRef.current) {
                  if (videoRef.current.requestFullscreen) {
                    videoRef.current.requestFullscreen();
                  }
                }
              }}
              className="p-1 rounded text-slate-400 hover:text-white transition"
              title="Fullscreen"
            >
              <Maximize2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Legend */}
        {steps.length > 0 && (
          <div className="mt-2.5 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] font-mono text-slate-500">
            <span className="flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
              <span>Step</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
              <span>Silent</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              <span>Mistake</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
              <span>Gap</span>
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

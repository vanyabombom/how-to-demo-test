import React, { useState, useEffect } from 'react';
import { X, Copy, Check, Download, FileCode } from 'lucide-react';

export default function ExportModal({ isOpen, onClose, result }) {
  const [markdownText, setMarkdownText] = useState('');
  const [copied, setCopied] = useState(false);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (result && isOpen) {
      fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result)
      })
        .then((res) => res.json())
        .then((data) => setMarkdownText(data.markdown || ''))
        .catch((err) => console.error('Export error', err));
    }
  }, [result, isOpen]);

  if (!isOpen) return null;

  const handleCopy = () => {
    if (!markdownText) return;
    navigator.clipboard.writeText(markdownText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!markdownText) return;
    const title = result?.guide_title || 'how-to-guide';
    const safeTitle = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') || 'how-to-guide';
    const blob = new Blob([markdownText], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${safeTitle}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-xs flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-slate-900 border border-slate-700/80 rounded-lg max-w-2xl w-full p-5 shadow-xl relative flex flex-col max-h-[85vh]"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded"
          title="Close (Esc)"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-center space-x-2.5 mb-3.5">
          <div className="w-8 h-8 rounded bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <FileCode className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-white">Markdown Export</h3>
            <p className="text-xs text-slate-400 font-mono">Portable guide for GitHub, Notion, or internal wikis</p>
          </div>
        </div>

        {/* Code Viewport */}
        <div className="flex-1 overflow-auto bg-slate-950 border border-slate-800 rounded p-3.5 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed select-all">
          {markdownText || 'Generating documentation export...'}
        </div>

        <div className="pt-3.5 mt-3.5 border-t border-slate-800 flex items-center justify-between text-xs">
          <span className="text-slate-500 font-mono text-[11px]">
            Format: CommonMark with alerts
          </span>
          <div className="flex space-x-2">
            <button
              onClick={handleCopy}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-mono bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-mono font-medium bg-blue-600 hover:bg-blue-500 text-white transition"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download .md</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

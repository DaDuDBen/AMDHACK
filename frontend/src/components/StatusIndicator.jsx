export default function StatusIndicator({ status }) {
  const llmMode = status?.llm_mode || 'offline';

  const config = {
    claude: { dot: 'bg-emerald-400', label: '🟢 Online (Claude)', bg: 'bg-emerald-900/30 border-emerald-700/30' },
    groq: { dot: 'bg-emerald-400', label: '🟢 Online (Groq)', bg: 'bg-emerald-900/30 border-emerald-700/30' },
    ollama: { dot: 'bg-amber-400', label: '🟡 Local (Chemistry-Mistral)', bg: 'bg-amber-900/30 border-amber-700/30' },
    offline: { dot: 'bg-slate-400', label: '⚪ Offline (Rules Only)', bg: 'bg-slate-800/30 border-slate-600/30' },
  };

  const { dot, label, bg } = config[llmMode] || config.offline;

  return (
    <div className={`flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium ${bg}`}>
      <span className={`inline-block h-2 w-2 rounded-full ${dot} animate-pulse`} />
      <span className="text-slate-200">{label}</span>
    </div>
  );
}

export default function StatusIndicator({ status }) {
  const llmMode = status?.llm_mode || 'offline';
  const isClaude = llmMode === 'claude';

  return (
    <div className="rounded-full px-3 py-1 text-sm font-medium shadow-sm">
      <span className={isClaude ? 'text-emerald-700' : 'text-amber-700'}>
        {isClaude ? '🟢 Online (Claude)' : '🟡 Offline (Phi-3)'}
      </span>
    </div>
  );
}

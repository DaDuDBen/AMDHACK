export default function ExperimentHistory({ items }) {
  return (
    <div className="flex-1 overflow-y-auto rounded-lg border border-slate-200 bg-slate-50 p-3">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-600">Experiment History</h2>
      {items.length === 0 ? (
        <p className="text-sm text-slate-500">No experiments yet. Try the demo flow prompts.</p>
      ) : (
        <ul className="space-y-2">
          {items.map((item) => (
            <li key={item.id} className="rounded-md border border-slate-200 bg-white p-2">
              <p className="text-sm font-medium text-slate-800">{item.input}</p>
              <p className="text-xs text-slate-600">{item.summary}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

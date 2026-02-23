export default function SafetyWarningModal({ safety, onClose }) {
  if (!safety) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-slate-950/60 p-4">
      <div className="w-full max-w-xl rounded-xl bg-white p-6 shadow-xl">
        <h3 className="mb-2 text-lg font-semibold text-rose-700">⚠️ Safety Warning</h3>
        <p className="mb-2 text-sm text-slate-800"><strong>Reason:</strong> {safety.reason}</p>
        <p className="mb-4 text-sm text-slate-700">{safety.educational_note}</p>
        <p className="mb-4 text-xs uppercase tracking-wide text-slate-500">Severity: {safety.severity}</p>
        <button onClick={onClose} className="rounded-lg bg-teal-500 px-4 py-2 text-sm font-semibold text-white">
          Close
        </button>
      </div>
    </div>
  );
}

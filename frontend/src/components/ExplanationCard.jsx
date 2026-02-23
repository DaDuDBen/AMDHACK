export default function ExplanationCard({ explanation, unknownMessage, partialInfo }) {
  if (unknownMessage) {
    return (
      <section className="rounded-xl border border-amber-300 bg-amber-50 p-4">
        <h3 className="mb-2 text-base font-semibold text-amber-800">Reaction not in database yet</h3>
        <p className="mb-3 text-sm text-amber-900">{unknownMessage}</p>
        {partialInfo?.reactant_notes && (
          <ul className="list-disc space-y-1 pl-5 text-sm text-amber-900">
            {Object.entries(partialInfo.reactant_notes).map(([reactant, note]) => (
              <li key={reactant}><strong>{reactant}:</strong> {note}</li>
            ))}
          </ul>
        )}
      </section>
    );
  }

  if (!explanation) {
    return (
      <section className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-500">
        Run an experiment to view a Socratic explanation.
      </section>
    );
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4">
      <h3 className="mb-3 text-base font-semibold text-slate-800">Socratic Explanation</h3>
      <p className="mb-2 text-sm text-slate-700"><strong>What happened:</strong> {explanation.what_happened}</p>
      <p className="mb-2 text-sm text-slate-700"><strong>Think deeper:</strong> {explanation.socratic_question}</p>
      <p className="mb-2 text-sm text-slate-700"><strong>Concept:</strong> {explanation.key_concept}</p>
      <p className="mb-2 text-sm text-slate-700"><strong>NCERT:</strong> {explanation.ncert_reference}</p>
      <p className="text-sm text-slate-700"><strong>Fun fact:</strong> {explanation.fun_fact}</p>
    </section>
  );
}

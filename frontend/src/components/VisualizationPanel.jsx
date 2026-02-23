function assetUrl(animationAsset) {
  return animationAsset ? `/src/assets/animations/${animationAsset}` : null;
}

export default function VisualizationPanel({ loading, simulation, visualization }) {
  if (loading) {
    return (
      <section className="rounded-xl border border-slate-200 bg-white p-4">
        <div className="flex items-center gap-2 text-slate-700">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-teal-500 border-t-transparent" />
          Running virtual experiment...
        </div>
      </section>
    );
  }

  if (!simulation) {
    return (
      <section className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-500">
        Visualization, balanced equation, and reaction observations will appear here.
      </section>
    );
  }

  const animationSrc = assetUrl(visualization?.animation_asset);

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4">
      <h3 className="mb-3 text-base font-semibold text-slate-800">Simulation Result</h3>
      {animationSrc ? (
        <div className="mb-4 rounded-lg border border-slate-100 bg-slate-50 p-3 text-xs text-slate-600">
          Animation asset: {visualization.animation_asset}
          <div className="mt-1 break-all">{animationSrc}</div>
        </div>
      ) : null}

      <p className="mb-2 text-sm text-slate-800"><strong>Equation:</strong> {simulation.balanced_equation}</p>
      <p className="mb-2 text-sm text-slate-700"><strong>Thermodynamics:</strong> {simulation.thermodynamics}</p>
      <p className="mb-2 text-sm text-slate-700"><strong>Reactants:</strong> {simulation.reactants.join(', ')}</p>
      <p className="mb-2 text-sm text-slate-700"><strong>Products:</strong> {simulation.products.join(', ')}</p>
      <p className="mb-2 text-sm text-slate-700"><strong>Observations:</strong> {simulation.observations.join(', ')}</p>
      {visualization && (
        <p className="text-sm text-slate-700">
          <strong>Visual cues:</strong> intensity {visualization.intensity}, thermometer {visualization.show_thermometer ? visualization.thermometer_direction : 'off'}.
        </p>
      )}
    </section>
  );
}

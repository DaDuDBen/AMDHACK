import { useEffect, useMemo, useState } from 'react';
import ChatInput from './components/ChatInput.jsx';
import ExperimentHistory from './components/ExperimentHistory.jsx';
import ExplanationCard from './components/ExplanationCard.jsx';
import SafetyWarningModal from './components/SafetyWarningModal.jsx';
import StatusIndicator from './components/StatusIndicator.jsx';
import VisualizationPanel from './components/VisualizationPanel.jsx';
import { useExperiment } from './hooks/useExperiment.js';
import { getStatus } from './utils/api.js';

function summarizeResponse(result) {
  if (result?.is_blocked) {
    return 'Blocked by safety filter';
  }
  if (result?.is_unknown) {
    return 'Unknown reaction in local database';
  }
  if (result?.simulation?.balanced_equation) {
    return result.simulation.balanced_equation;
  }
  return 'Processed';
}

export default function App() {
  const [status, setStatus] = useState({ llm_mode: 'offline' });
  const [history, setHistory] = useState([]);
  const [showSafety, setShowSafety] = useState(false);
  const { loading, error, response, submitExperiment } = useExperiment();

  useEffect(() => {
    let mounted = true;
    getStatus()
      .then((payload) => {
        if (mounted) {
          setStatus(payload);
        }
      })
      .catch(() => {
        if (mounted) {
          setStatus({ llm_mode: 'offline' });
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (response?.is_blocked) {
      setShowSafety(true);
    }
  }, [response]);

  const handleSubmit = async (userInput) => {
    try {
      const result = await submitExperiment(userInput);
      setHistory((prev) => [
        {
          id: crypto.randomUUID(),
          input: userInput,
          summary: summarizeResponse(result)
        },
        ...prev
      ]);
    } catch {
      // error handled in hook state
    }
  };

  const unknownContent = useMemo(() => {
    if (!response?.is_unknown) {
      return { message: null, partialInfo: null };
    }
    return {
      message: response.message,
      partialInfo: response.partial_info
    };
  }, [response]);

  return (
    <main className="min-h-screen bg-slate-950 px-5 py-4 text-slate-100">
      <header className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">🧪 Prayog-Shala</h1>
          <p className="text-sm text-slate-300">Offline-capable AI virtual chemistry lab</p>
        </div>
        <StatusIndicator status={status} />
      </header>

      <section className="grid min-h-[82vh] grid-cols-1 gap-4 lg:grid-cols-5">
        <aside className="flex flex-col rounded-xl bg-white p-4 text-slate-900 lg:col-span-2">
          <ExperimentHistory items={history} />
          <div className="mt-3 text-xs text-slate-500">
            Demo prompts: “mix magnesium with hydrochloric acid”, “mix potassium with water”, “dissolve copper in ethanol”.
          </div>
          <ChatInput onSubmit={handleSubmit} loading={loading} />
        </aside>

        <section className="space-y-4 rounded-xl bg-white p-4 text-slate-900 lg:col-span-3">
          {error && (
            <div className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{error}</div>
          )}

          <VisualizationPanel
            loading={loading}
            simulation={response.simulation}
            visualization={response.visualization}
          />

          <ExplanationCard
            explanation={response.explanation}
            unknownMessage={unknownContent.message}
            partialInfo={unknownContent.partialInfo}
          />
        </section>
      </section>

      {showSafety && (
        <SafetyWarningModal
          safety={response.safety}
          onClose={() => setShowSafety(false)}
        />
      )}
    </main>
  );
}

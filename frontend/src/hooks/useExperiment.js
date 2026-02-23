import { useCallback, useState } from 'react';
import { runExperiment } from '../utils/api.js';

const INITIAL_STATE = {
  status: null,
  is_blocked: false,
  is_unknown: false,
  safety: null,
  reaction: null,
  visualization: null,
  explanation: null,
  parsed_input: null,
  message: null,
  partial_info: null
};

export function useExperiment() {
  const [response, setResponse] = useState(INITIAL_STATE);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const submitExperiment = useCallback(async (input) => {
    setLoading(true);
    setError(null);

    try {
      const result = await runExperiment(input);
      setResponse({ ...INITIAL_STATE, ...result });
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong while running the experiment.');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const resetExperiment = useCallback(() => {
    setResponse(INITIAL_STATE);
    setError(null);
    setLoading(false);
  }, []);

  return {
    loading,
    error,
    response,
    submitExperiment,
    resetExperiment
  };
}

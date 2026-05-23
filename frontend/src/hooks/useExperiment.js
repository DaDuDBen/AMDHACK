import { useCallback, useRef, useState } from 'react';
import { runExperiment } from '../utils/api.js';

const INITIAL_STATE = {
  status: null,
  is_blocked: false,
  is_unknown: false,
  is_followup: false,
  safety: null,
  simulation: null,
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
  // Track last successful simulation for follow-up context
  const lastSimulationRef = useRef(null);

  const submitExperiment = useCallback(async (userInput, sessionId = null) => {
    setLoading(true);
    setError(null);

    try {
      // Pass context from last successful simulation for follow-up questions
      const result = await runExperiment(userInput, sessionId, lastSimulationRef.current);
      setResponse({ ...INITIAL_STATE, ...result });

      // Store the simulation data for follow-up context
      if (result?.simulation && !result?.is_blocked && !result?.is_unknown) {
        lastSimulationRef.current = {
          reaction_id: result.simulation.reaction_id,
          balanced_equation: result.simulation.balanced_equation,
          reactants: result.simulation.reactants,
          products: result.simulation.products,
          observations: result.simulation.observations,
          thermodynamics: result.simulation.thermodynamics,
          // Include visualization data for context
          animation_type: result.visualization?.animation_asset?.replace('.json', '') || 'no_reaction',
          difficulty_level: 'class_10',
          ncert_reference: result.explanation?.ncert_reference || '',
          type: result.simulation.type || '',
        };
      }

      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong while running the experiment.');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearResult = useCallback(() => {
    setResponse(INITIAL_STATE);
    setError(null);
    lastSimulationRef.current = null;
  }, []);

  return {
    loading,
    error,
    response,
    submitExperiment,
    clearResult
  };
}

/**
 * Analysis API service.
 *
 * Provides TanStack Query mutation hook for feature analysis.
 *
 * Docs: https://tanstack.com/query/latest/docs/framework/react/guides/mutations
 */

import { useMutation } from '@tanstack/react-query';
import { apiPost } from '../lib/api';

// Types - mirror backend/src/nexus_api/models/analysis.py

export type RiskLevel = 'high' | 'medium' | 'low';

export interface ImpactedRepo {
  name: string;
  confidence: number;
  reasoning: string;
  modules: string[];
}

export interface RecommendedPerson {
  name: string;
  relevance: number;
  reasoning: string;
}

export interface Risk {
  type: RiskLevel;
  message: string;
}

export interface SuggestedStep {
  step: number;
  action: string;
  repository: string;
  reasoning: string;
}

export interface FeatureAnalysis {
  feature: string;
  impactedRepos: ImpactedRepo[];
  recommendedPeople: RecommendedPerson[];
  risks: Risk[];
  suggestedOrder: SuggestedStep[];
  additionalRecommendations: string[];
}

export interface AnalyzeFeatureRequest {
  description: string;
}

// API functions
async function analyzeFeature(
  request: AnalyzeFeatureRequest
): Promise<FeatureAnalysis> {
  return apiPost<FeatureAnalysis, AnalyzeFeatureRequest>(
    '/analysis',
    request
  );
}

// Hooks

/**
 * Mutation hook for analyzing a feature.
 *
 * @returns Mutation result with analyze function
 *
 * @example
 * const { mutate: analyze, data, isPending } = useAnalyzeFeature();
 * analyze({ description: 'Implement export feature' });
 */
export function useAnalyzeFeature() {
  return useMutation({
    mutationFn: analyzeFeature,
  });
}

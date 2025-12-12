/**
 * Repositories API service.
 *
 * Provides TanStack Query hooks for fetching repository data.
 *
 * Docs: https://tanstack.com/query/latest/docs/framework/react/overview
 */

import { useQuery } from '@tanstack/react-query';
import { apiGet } from '../lib/api';

// Types - mirror backend/src/nexus_api/models/repository.py

export type ActivityLevel = 'high' | 'medium' | 'low' | 'stale';

export type AlertType = 'warning' | 'danger' | 'info';

export interface Alert {
  type: AlertType;
  message: string;
}

export interface TopContributor {
  name: string;
  percentage: number;
}

export interface Hotspot {
  path: string;
  changes: number;
}

export interface Repository {
  id: string;
  name: string;
  description: string;
  lastCommit: string;
  totalCommits: number;
  contributors: number;
  activity: ActivityLevel;
  knowledgeConcentration: number;
  topContributors: TopContributor[];
  hotspots: Hotspot[];
  dependencies: string[];
  alerts: Alert[];
}

// Query keys
export const repositoryKeys = {
  all: ['repositories'] as const,
  detail: (id: string) => ['repositories', id] as const,
};

// API functions
async function fetchRepositories(): Promise<Repository[]> {
  return apiGet<Repository[]>('/repositories');
}

// Hooks

/**
 * Hook to fetch all repositories.
 *
 * @returns Query result with repositories list
 */
export function useRepositories() {
  return useQuery({
    queryKey: repositoryKeys.all,
    queryFn: fetchRepositories,
  });
}

/**
 * People API service.
 *
 * Provides TanStack Query hooks for fetching people data.
 *
 * Docs: https://tanstack.com/query/latest/docs/framework/react/overview
 */

import { useQuery } from '@tanstack/react-query';
import { apiGet } from '../lib/api';
import type { Alert, AlertType } from './repositories';

// Re-export shared types
export type { Alert, AlertType };

// Types - mirror backend/src/nexus_api/models/person.py

export interface PersonRepository {
  name: string;
  commits: number;
  lastActivity: string;
  expertise: number;
}

export interface Technology {
  name: string;
  level: number;
}

export interface Person {
  id: string;
  name: string;
  email: string;
  avatar: string;
  repositories: PersonRepository[];
  technologies: Technology[];
  domains: string[];
  recentActivity: number;
  alerts: Alert[];
}

// Query keys
export const peopleKeys = {
  all: ['people'] as const,
  detail: (id: string) => ['people', id] as const,
};

// API functions
async function fetchPeople(): Promise<Person[]> {
  return apiGet<Person[]>('/people');
}

// Hooks

/**
 * Hook to fetch all people.
 *
 * @returns Query result with people list
 */
export function usePeople() {
  return useQuery({
    queryKey: peopleKeys.all,
    queryFn: fetchPeople,
  });
}

/**
 * Services barrel export.
 *
 * Re-exports all API service hooks and types for convenient imports.
 *
 * @example
 * import { useRepositories, usePeople, useAnalyzeFeature } from '@/services';
 */

// Repositories
export {
  useRepositories,
  useRepository,
  repositoryKeys,
  type Repository,
  type TopContributor,
  type Hotspot,
  type ActivityLevel,
  type Alert,
  type AlertType,
} from './repositories';

// People
export {
  usePeople,
  usePerson,
  peopleKeys,
  type Person,
  type PersonRepository,
  type Technology,
} from './people';

// Analysis
export {
  useAnalyzeFeature,
  type FeatureAnalysis,
  type AnalyzeFeatureRequest,
  type ImpactedRepo,
  type RecommendedPerson,
  type Risk,
  type SuggestedStep,
  type RiskLevel,
} from './analysis';

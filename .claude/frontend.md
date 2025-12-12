# Frontend Development Guide

**React 18 / TypeScript / Vite**

Este guia contém todas as informações específicas para desenvolvimento do frontend. Sempre siga os princípios da constituição (`.specify/memory/constitution.md`) e o workflow TDD/BDD.

## Common Commands

```bash
# Setup and dependencies
cd frontend && pnpm install

# Development server (HMR on changes)
cd frontend
pnpm dev                 # Runs on http://localhost:8080

# Build
pnpm build               # Production build
pnpm build:dev           # Development build with source maps

# Code quality
pnpm lint                # ESLint

# Preview production build
pnpm preview
```

## Frontend Architecture

### Tech Stack

- **React 18** with TypeScript and strict mode
- **Vite** for build tooling (using SWC for fast refresh)
- **React Router** for client-side routing (v6)
- **TanStack Query** for data fetching and caching
- **shadcn/ui** for UI components (Radix UI + Tailwind CSS)
- **Tailwind CSS** for styling with custom theme
- **Zod** for runtime validation
- **React Hook Form** for form handling

### Component Organization

- `components/` - Feature components (3 dashboard components)
- `components/ui/` - shadcn/ui design system components (do not modify directly)
- `pages/` - Route components (Index is main dashboard, NotFound for 404)
- `services/` - API client functions grouped by domain (repositories, people, analysis)
- `lib/` - Shared utilities (`api.ts` for fetch wrapper, `utils.ts` for cn helper)

### Data Flow

1. Component uses TanStack Query hook (e.g., `useQuery`)
2. Query calls service function (e.g., `fetchRepositories()`)
3. Service uses `apiGet/apiPost` from `lib/api.ts`
4. API client calls backend at `VITE_API_URL` (defaults to `http://localhost:8000/api/v1`)
5. Response data flows back through query hook to component

### API Client Pattern

```typescript
// In services/*.ts
import { apiGet, apiPost } from '@/lib/api';

export async function fetchRepositories() {
  return apiGet<Repository[]>('/repositories');
}

// In components
import { useQuery } from '@tanstack/react-query';
import { fetchRepositories } from '@/services/repositories';

const { data, isLoading, error } = useQuery({
  queryKey: ['repositories'],
  queryFn: fetchRepositories,
});
```

### Environment Configuration

- `VITE_API_URL` - Backend API base URL (defaults to `http://localhost:8000/api/v1`)
- Set in `frontend/.env` for local development

**Example `frontend/.env`**:
```env
VITE_API_URL=http://localhost:8000/api/v1
```

### Routing

- All routes defined in `App.tsx`
- Current routes: `/` (Index page), `*` (NotFound)
- **Important**: Add custom routes ABOVE the catch-all `*` route

**Example**:
```typescript
<Routes>
  <Route path="/" element={<Index />} />
  <Route path="/dashboard" element={<Dashboard />} />
  {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
  <Route path="*" element={<NotFound />} />
</Routes>
```

## Frontend Standards

### Component Structure

- Use functional components with hooks (no class components)
- Co-locate types with components when component-specific
- Shared types in service files or separate `types/` directory

**Example Component**:
```typescript
import { useQuery } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { fetchRepositories } from '@/services/repositories';

interface RepositoryDashboardProps {
  title?: string;
}

export function RepositoryDashboard({ title = 'Repositories' }: RepositoryDashboardProps) {
  const { data: repositories, isLoading, error } = useQuery({
    queryKey: ['repositories'],
    queryFn: fetchRepositories,
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {repositories?.map((repo) => (
          <div key={repo.repositoryId}>{repo.name}</div>
        ))}
      </CardContent>
    </Card>
  );
}
```

### Styling

- Use Tailwind utility classes (prefer composition over custom CSS)
- Use `cn()` helper from `lib/utils.ts` for conditional class merging
- shadcn/ui components provide consistent design tokens

**Example with Conditional Styling**:
```typescript
import { cn } from '@/lib/utils';

export function Badge({ status }: { status: string }) {
  return (
    <span
      className={cn(
        'px-2 py-1 rounded-full text-sm',
        status === 'active' && 'bg-green-100 text-green-800',
        status === 'inactive' && 'bg-gray-100 text-gray-800'
      )}
    >
      {status}
    </span>
  );
}
```

### File Size

- Maximum 1000 lines for TSX/HTML files (constitution exception)
- Other files: 500 lines max

## Testing Strategy

### DevTools Smoke Testing (MANDATORY)

When adding a new frontend feature, always use Chrome DevTools to verify:

1. **UI Rendering**: Component displays correctly, no layout issues
2. **Network Tab**: API calls succeed, correct payloads sent/received
3. **Console**: No errors or warnings
4. **Responsive Behavior**: Test different screen sizes

### Future Test Framework

When frontend tests are implemented, follow TDD:
1. Write component test (commit: `test: add tests for [component]`)
2. Verify test fails
3. Implement component
4. Verify test passes
5. Commit implementation

## Adding a New Dashboard Feature (TDD Workflow)

1. **Write component tests** (when test framework added)
2. **Create service function** in `services/[domain].ts`
   ```typescript
   export async function fetchDomainData(): Promise<DomainData[]> {
     return apiGet<DomainData[]>('/domain');
   }
   ```
3. **Create component** in `components/[Feature].tsx`
4. **Use TanStack Query** for data fetching
   ```typescript
   const { data, isLoading, error } = useQuery({
     queryKey: ['domain-data'],
     queryFn: fetchDomainData,
   });
   ```
5. **Add route** in `App.tsx` if new page
6. **Test in DevTools**: Network, Console, UI responsiveness
7. **Commit implementation** (commit: `feat: add [feature] dashboard`)

## API Contract with Backend

**Field Naming**: Frontend expects `camelCase` fields from backend (not `snake_case`).

**Example Type Definition**:
```typescript
// In services/repositories.ts
export interface Repository {
  repositoryId: string;
  name: string;
  lastCommit: string;
  contributorCount: number;
  activityLevel: 'high' | 'medium' | 'low';
}

// Backend sends:
// {
//   "repositoryId": "...",
//   "lastCommit": "...",
//   "contributorCount": 42,
//   "activityLevel": "high"
// }
```

## Common Patterns

### TanStack Query with Error Handling

```typescript
import { useQuery } from '@tanstack/react-query';
import { toast } from 'sonner';

export function MyComponent() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['my-data'],
    queryFn: fetchMyData,
    onError: (error) => {
      toast.error(`Failed to load data: ${error.message}`);
    },
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorState message={error.message} />;

  return <DataDisplay data={data} />;
}
```

### Form with React Hook Form + Zod

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const formSchema = z.object({
  description: z.string().min(10, 'Description must be at least 10 characters'),
});

type FormData = z.infer<typeof formSchema>;

export function MyForm() {
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: { description: '' },
  });

  const onSubmit = (data: FormData) => {
    // Handle submission
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <input {...form.register('description')} />
      {form.formState.errors.description && (
        <span>{form.formState.errors.description.message}</span>
      )}
      <button type="submit">Submit</button>
    </form>
  );
}
```

### API POST with Mutation

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiPost } from '@/lib/api';
import { toast } from 'sonner';

export function useAnalyzeFeature() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (description: string) =>
      apiPost<AnalysisResult>('/analysis', { description }),
    onSuccess: (data) => {
      toast.success('Analysis complete!');
      queryClient.invalidateQueries({ queryKey: ['analysis'] });
    },
    onError: (error) => {
      toast.error(`Analysis failed: ${error.message}`);
    },
  });
}
```

### shadcn/ui Component Usage

```typescript
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export function FeatureCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Feature Title</CardTitle>
        <CardDescription>Feature description here</CardDescription>
      </CardHeader>
      <CardContent>
        <Badge>Active</Badge>
        <p>Card content</p>
      </CardContent>
      <CardFooter>
        <Button>Action</Button>
      </CardFooter>
    </Card>
  );
}
```

## Notes

- **Port**: Frontend dev server runs on `:8080` by default
- **API URL**: Defaults to `http://localhost:8000/api/v1` (configurable via `VITE_API_URL`)
- **Hot Module Replacement**: Vite provides instant HMR for fast development
- **shadcn/ui**: Do not modify components in `components/ui/` directly - they are generated
- **Path Alias**: Use `@/` for imports (e.g., `@/components/ui/button`)

## References

For global development standards:
@~/.claude/CLAUDE.md

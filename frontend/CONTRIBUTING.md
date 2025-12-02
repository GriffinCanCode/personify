# Contributing to Personify Frontend

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

### Prerequisites

- Node.js 20+
- npm 10+
- Git

### Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd personify/frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Start development server
npm run dev
```

## Development Workflow

### 1. Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - New features
- `fix/*` - Bug fixes
- `refactor/*` - Code refactoring

### 2. Making Changes

```bash
# Create a new branch
git checkout -b feature/my-new-feature

# Make your changes
# ...

# Run validation before committing
npm run validate
```

### 3. Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(chat): add message editing functionality
fix(upload): resolve file size validation issue
docs(readme): update installation instructions
```

### 4. Pull Request Process

1. Update your branch with latest `develop`
2. Run full validation suite: `npm run validate`
3. Push your changes
4. Create a PR with:
   - Clear title following commit convention
   - Description of changes
   - Screenshots/videos for UI changes
   - Link to related issues

## Code Quality Standards

### TypeScript

- Use strict TypeScript - no `any` types unless absolutely necessary
- Prefer `type` over `interface` for object types
- Use `const` assertions where appropriate
- Leverage utility types (`Partial`, `Pick`, `Omit`, etc.)

```typescript
// ✅ Good
type User = {
  id: string
  name: string
  email: string
}

const getUser = async (id: string): Promise<User> => {
  // ...
}

// ❌ Bad
const getUser = async (id: any): Promise<any> => {
  // ...
}
```

### React Components

- Use functional components with hooks
- Prefer named exports
- Keep components focused and single-responsibility
- Extract complex logic into custom hooks
- Use proper TypeScript types for props

```typescript
// ✅ Good
type ButtonProps = {
  label: string
  onClick: () => void
  variant?: 'primary' | 'secondary'
}

export const Button = ({ label, onClick, variant = 'primary' }: ButtonProps) => {
  return (
    <button onClick={onClick} className={cn('btn', `btn-${variant}`)}>
      {label}
    </button>
  )
}

// ❌ Bad
export const Button = (props: any) => {
  return <button onClick={props.onClick}>{props.label}</button>
}
```

### Styling

- Use Tailwind CSS utility classes
- Leverage the `cn()` utility for conditional classes
- Extract repeated patterns into components
- Use CSS variables for theme values

```typescript
// ✅ Good
<div className={cn(
  'rounded-lg p-4',
  isActive && 'bg-primary text-primary-foreground',
  className
)}>
  {children}
</div>

// ❌ Bad
<div className={`rounded-lg p-4 ${isActive ? 'bg-primary text-primary-foreground' : ''} ${className}`}>
  {children}
</div>
```

### Testing

#### Unit Tests (Vitest)

- Test business logic and utilities
- Test component behavior, not implementation
- Use Testing Library queries properly
- Mock external dependencies

```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen, userEvent } from '@/lib/test-utils'
import { Button } from './Button'

describe('Button', () => {
  it('calls onClick when clicked', async () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    await userEvent.click(screen.getByRole('button'))
    
    expect(handleClick).toHaveBeenCalledOnce()
  })
})
```

#### E2E Tests (Playwright)

- Test critical user flows
- Test across different browsers
- Use Page Object pattern for complex flows
- Keep tests independent

```typescript
import { test, expect } from '@playwright/test'

test('user can upload a file', async ({ page }) => {
  await page.goto('/upload')
  
  const fileInput = page.locator('input[type="file"]')
  await fileInput.setInputFiles('path/to/test-file.pdf')
  
  await expect(page.locator('text=Upload successful')).toBeVisible()
})
```

## Project Structure

```
frontend/
├── app/                  # Next.js App Router pages
│   ├── layout.tsx       # Root layout
│   └── page.tsx         # Home page
├── components/          # Reusable components
│   ├── ui/             # Base UI components
│   └── ...             # Feature components
├── lib/                # Utilities and helpers
│   ├── api.ts          # API client
│   ├── utils.ts        # Utilities
│   └── env.ts          # Environment config
├── types/              # TypeScript type definitions
├── e2e/                # Playwright E2E tests
├── __tests__/          # Unit tests
└── public/             # Static assets
```

## Available Commands

### Development
- `npm run dev` - Start dev server
- `npm run build` - Build for production
- `npm start` - Start production server

### Code Quality
- `npm run lint` - Run linters
- `npm run lint:fix` - Fix linting issues
- `npm run format` - Format code
- `npm run type-check` - Check TypeScript

### Testing
- `npm test` - Run unit tests (watch mode)
- `npm run test:coverage` - Generate coverage report
- `npm run test:e2e` - Run E2E tests
- `npm run test:e2e:ui` - Open Playwright UI

### Validation
- `npm run validate` - Run all checks (recommended before PR)

## Git Hooks

We use Husky for automated checks:

### Pre-commit
- Lints and formats staged files
- Runs automatically before each commit

### Pre-push
- Type checks entire codebase
- Runs automatically before push

If you need to bypass hooks (not recommended):
```bash
git commit --no-verify
```

## Performance Guidelines

### Code Splitting
- Use dynamic imports for large components
- Lazy load routes when appropriate

```typescript
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <Spinner />,
})
```

### React Performance
- Use `useMemo` and `useCallback` judiciously
- Avoid unnecessary re-renders
- Use React Query for data fetching

### Bundle Size
- Check bundle size impact: `npm run build`
- Keep third-party dependencies minimal
- Use tree-shakeable imports

```typescript
// ✅ Good
import { specific } from 'lodash-es'

// ❌ Bad
import _ from 'lodash'
```

## Accessibility

- Use semantic HTML
- Include proper ARIA labels
- Ensure keyboard navigation works
- Test with screen readers
- Maintain color contrast ratios

```typescript
// ✅ Good
<button
  type="button"
  aria-label="Close dialog"
  onClick={onClose}
>
  <X aria-hidden="true" />
</button>

// ❌ Bad
<div onClick={onClose}>
  <X />
</div>
```

## Getting Help

- Check existing issues and PRs
- Read the documentation
- Ask in team chat/discussions
- Create an issue for bugs or feature requests

## Code Review Process

All submissions require review. We use GitHub PRs for this:

1. Reviewer will check:
   - Code quality and style
   - Test coverage
   - Performance implications
   - Accessibility
   - Documentation

2. Address feedback promptly
3. Request re-review after changes
4. Maintain a constructive dialogue

## License

By contributing, you agree that your contributions will be licensed under the project's license.


# Personify Frontend

Modern Next.js frontend with comprehensive developer tooling.

## Developer Tooling (2025)

This project includes state-of-the-art developer tooling:

### Code Quality
- **Biome**: Ultra-fast linter, formatter, and import sorter (Rust-based)
- **ESLint**: Additional linting with Next.js and TypeScript rules
- **TypeScript**: Strict mode with enhanced compiler options

### Testing
- **Vitest**: Lightning-fast unit testing framework
- **Testing Library**: React component testing utilities
- **Playwright**: Multi-browser E2E testing

### Git Hooks
- **Husky**: Pre-commit and pre-push hooks
- **lint-staged**: Run linters only on staged files

### VS Code Integration
- Automatic formatting on save
- Import organization
- Tailwind CSS IntelliSense
- Vitest and Playwright extensions

## Getting Started

```bash
# Install dependencies
npm install

# Initialize git hooks
npm run prepare

# Start development server
npm run dev
```

## Available Scripts

### Development
- `npm run dev` - Start Next.js dev server
- `npm run build` - Build for production
- `npm start` - Start production server

### Code Quality
- `npm run lint` - Check code with ESLint & Biome
- `npm run lint:fix` - Auto-fix linting issues
- `npm run format` - Format code with Biome
- `npm run format:check` - Check formatting
- `npm run type-check` - Run TypeScript compiler

### Testing
- `npm test` - Run unit tests in watch mode
- `npm run test:ui` - Open Vitest UI
- `npm run test:coverage` - Generate coverage report
- `npm run test:e2e` - Run Playwright E2E tests
- `npm run test:e2e:ui` - Open Playwright UI
- `npm run test:e2e:debug` - Debug E2E tests

### Validation
- `npm run validate` - Run all checks (types, lint, tests)

## Project Structure

```
frontend/
├── app/              # Next.js 14 App Router
├── components/       # Reusable React components
├── lib/             # Utilities and API clients
├── e2e/             # Playwright E2E tests
├── __tests__/       # Vitest unit tests
├── .husky/          # Git hooks
└── .vscode/         # VS Code settings
```

## Code Style

This project uses:
- **Biome** for fast, consistent formatting and linting
- Single quotes for JavaScript
- 2 space indentation
- 100 character line width
- Trailing commas (ES5)
- Semicolons as needed (ASI)

## Testing Strategy

### Unit Tests (Vitest)
- Component behavior
- Utility functions
- Business logic
- Located in `__tests__/` or `*.test.tsx`

### E2E Tests (Playwright)
- User flows
- Integration scenarios
- Cross-browser testing
- Located in `e2e/`

## CI/CD Integration

The project is configured for CI/CD with:
- Automated linting and formatting checks
- Type checking
- Unit and E2E tests
- Coverage reports

Add this to your CI pipeline:
```bash
npm run validate
```

## VS Code Setup

Install recommended extensions:
1. Biome
2. ESLint
3. Tailwind CSS IntelliSense
4. Playwright
5. Vitest Explorer

The workspace is pre-configured for optimal DX.

## Performance

- **Biome**: 10-100x faster than ESLint/Prettier
- **Vitest**: 10x faster than Jest
- **Happy DOM**: Lightweight DOM implementation
- **Incremental TypeScript**: Fast type checking

## Contributing

1. Write tests for new features
2. Run `npm run validate` before committing
3. Git hooks will auto-format your code
4. Ensure all tests pass

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.3+
- **Styling**: Tailwind CSS + CSS Variables
- **State**: React Query (TanStack Query)
- **Components**: Radix UI
- **Testing**: Vitest + Playwright + Testing Library
- **Linting**: Biome + ESLint
- **Type Safety**: Strict TypeScript


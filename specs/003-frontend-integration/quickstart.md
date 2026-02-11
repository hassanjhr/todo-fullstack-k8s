# Quickstart Guide: Frontend Application

**Feature**: 003-frontend-integration
**Date**: 2026-02-07
**Audience**: Developers implementing the frontend

## Overview

This guide provides step-by-step instructions for setting up and developing the Next.js frontend application that integrates with the existing FastAPI backend.

## Prerequisites

### Required Software

- **Node.js**: v18.0.0 or higher
- **npm**: v9.0.0 or higher (comes with Node.js)
- **Git**: For version control
- **Code Editor**: VS Code recommended (with TypeScript support)

### Required Backend Services

- **FastAPI Backend**: Must be running on configured URL (default: http://localhost:8000)
- **Neon PostgreSQL**: Backend database must be accessible
- **Better Auth**: Authentication service must be functional

### Verify Backend is Running

```bash
# Check backend health
curl http://localhost:8000/health

# Expected response: {"status": "healthy"}
```

---

## Initial Setup

### 1. Create Next.js Project

```bash
# Navigate to project root
cd /path/to/hackathon_2_phase_2

# Create Next.js app with TypeScript and Tailwind
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir

# Navigate to frontend directory
cd frontend
```

**Configuration Options** (when prompted):
- ✅ TypeScript: Yes
- ✅ ESLint: Yes
- ✅ Tailwind CSS: Yes
- ✅ App Router: Yes
- ❌ src/ directory: No
- ✅ Import alias (@/*): Yes

### 2. Install Additional Dependencies

```bash
# No additional dependencies required for MVP
# Next.js, React, and Tailwind CSS are sufficient
```

### 3. Configure Environment Variables

Create `.env.local` file in `frontend/` directory:

```bash
# Create environment file
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
```

Create `.env.example` file for documentation:

```bash
# Create example file
cat > .env.example << 'EOF'
# Backend API base URL
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
```

**Important**: Add `.env.local` to `.gitignore` (should be there by default)

### 4. Verify Installation

```bash
# Start development server
npm run dev

# Expected output:
# - Local: http://localhost:3000
# - Ready in X ms
```

Open browser to http://localhost:3000 - you should see the default Next.js page.

---

## Project Structure Setup

### 1. Create Directory Structure

```bash
# From frontend/ directory
mkdir -p app/\(auth\)/signup
mkdir -p app/\(auth\)/signin
mkdir -p app/dashboard
mkdir -p components/auth
mkdir -p components/tasks
mkdir -p components/ui
mkdir -p components/layout
mkdir -p lib/api
mkdir -p lib/auth
mkdir -p lib/utils
mkdir -p types
```

### 2. Copy Type Definitions

```bash
# Copy types from contracts to frontend
cp ../specs/003-frontend-integration/contracts/types.ts types/index.ts
```

### 3. Create Placeholder Files

```bash
# Create empty files for implementation
touch app/\(auth\)/signup/page.tsx
touch app/\(auth\)/signin/page.tsx
touch app/dashboard/page.tsx
touch app/dashboard/layout.tsx
touch middleware.ts
touch components/auth/AuthForm.tsx
touch components/auth/SignOutButton.tsx
touch components/tasks/TaskForm.tsx
touch components/tasks/TaskList.tsx
touch components/tasks/TaskItem.tsx
touch components/ui/LoadingSpinner.tsx
touch components/ui/ErrorMessage.tsx
touch components/ui/Button.tsx
touch components/layout/Header.tsx
touch components/layout/Container.tsx
touch lib/api/client.ts
touch lib/api/auth.ts
touch lib/api/tasks.ts
touch lib/auth/token.ts
touch lib/auth/context.tsx
touch lib/auth/hooks.ts
touch lib/utils/validation.ts
touch lib/utils/errors.ts
```

---

## Development Workflow

### Phase 1: Authentication Foundation

**Goal**: Implement user authentication (signup, signin, signout)

**Steps**:
1. Implement token storage utilities (`lib/auth/token.ts`)
2. Create auth context and provider (`lib/auth/context.tsx`)
3. Create auth hooks (`lib/auth/hooks.ts`)
4. Build API client base (`lib/api/client.ts`)
5. Implement auth API functions (`lib/api/auth.ts`)
6. Create AuthForm component (`components/auth/AuthForm.tsx`)
7. Build signup page (`app/(auth)/signup/page.tsx`)
8. Build signin page (`app/(auth)/signin/page.tsx`)
9. Implement signout button (`components/auth/SignOutButton.tsx`)

**Testing**:
- User can sign up with valid credentials
- User can sign in with correct credentials
- Token is stored in localStorage
- Auth state persists across page refresh

### Phase 2: Route Protection

**Goal**: Protect dashboard routes and redirect unauthenticated users

**Steps**:
1. Implement Next.js middleware (`middleware.ts`)
2. Create auth guard hook (`lib/auth/hooks.ts` - useRequireAuth)
3. Build protected dashboard layout (`app/dashboard/layout.tsx`)
4. Update landing page with redirect logic (`app/page.tsx`)

**Testing**:
- Unauthenticated users redirected to /signin
- Authenticated users can access /dashboard
- Authenticated users redirected from /signin to /dashboard

### Phase 3: Task Management

**Goal**: Implement task CRUD operations

**Steps**:
1. Implement task API functions (`lib/api/tasks.ts`)
2. Create TaskForm component (`components/tasks/TaskForm.tsx`)
3. Create TaskList component (`components/tasks/TaskList.tsx`)
4. Create TaskItem component (`components/tasks/TaskItem.tsx`)
5. Build dashboard page (`app/dashboard/page.tsx`)
6. Implement optimistic updates

**Testing**:
- User can create tasks
- User can view all their tasks
- User can update task title
- User can toggle task completion
- User can delete tasks

### Phase 4: UI Polish

**Goal**: Create reusable UI components and responsive design

**Steps**:
1. Create Button component (`components/ui/Button.tsx`)
2. Create LoadingSpinner component (`components/ui/LoadingSpinner.tsx`)
3. Create ErrorMessage component (`components/ui/ErrorMessage.tsx`)
4. Create Header component (`components/layout/Header.tsx`)
5. Create Container component (`components/layout/Container.tsx`)
6. Add loading and error states to all pages
7. Implement responsive design with Tailwind breakpoints

**Testing**:
- All components render correctly
- Loading states display during API calls
- Error messages show for failures
- Layout is responsive (320px - 1920px)

---

## Running the Application

### Development Mode

```bash
# Start development server with hot reload
npm run dev

# Server runs on http://localhost:3000
```

### Production Build

```bash
# Build optimized production bundle
npm run build

# Start production server
npm start

# Server runs on http://localhost:3000
```

### Linting and Type Checking

```bash
# Run ESLint
npm run lint

# Type check with TypeScript
npx tsc --noEmit
```

---

## Testing the Integration

### Manual Testing Checklist

**Authentication Flow**:
```bash
# 1. Open http://localhost:3000
# 2. Click "Sign Up" or navigate to /signup
# 3. Enter email: test@example.com, password: password123
# 4. Submit form
# 5. Verify redirect to /signin with success message
# 6. Sign in with same credentials
# 7. Verify redirect to /dashboard
# 8. Refresh page - verify still authenticated
# 9. Click "Sign Out"
# 10. Verify redirect to /signin
```

**Task Management Flow**:
```bash
# 1. Sign in to application
# 2. Navigate to /dashboard
# 3. Enter task title "Test Task" and submit
# 4. Verify task appears in list
# 5. Click task to edit title
# 6. Update title to "Updated Task"
# 7. Verify title updates immediately
# 8. Toggle completion checkbox
# 9. Verify task shows as completed
# 10. Click delete button
# 11. Confirm deletion
# 12. Verify task removed from list
```

**Error Handling**:
```bash
# 1. Stop backend server
# 2. Try to sign in
# 3. Verify error message: "Connection failed"
# 4. Start backend server
# 5. Try to sign in with wrong password
# 6. Verify error message: "Invalid email or password"
# 7. Try to create task with empty title
# 8. Verify validation error: "Title is required"
```

### API Testing with curl

**Test Signup**:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

**Test Signin**:
```bash
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

**Test Get Tasks** (replace TOKEN with actual JWT):
```bash
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer TOKEN"
```

---

## Common Issues and Solutions

### Issue: "Cannot connect to backend"

**Symptoms**: API calls fail with network error

**Solutions**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check NEXT_PUBLIC_API_URL in `.env.local`
3. Verify CORS is configured on backend
4. Check browser console for CORS errors

### Issue: "401 Unauthorized on protected routes"

**Symptoms**: Redirected to signin even when logged in

**Solutions**:
1. Check token is stored in localStorage: Open DevTools → Application → Local Storage
2. Verify token format is correct (JWT string)
3. Check token expiration (decode JWT at jwt.io)
4. Verify Authorization header is sent: Open DevTools → Network → Request Headers

### Issue: "Tasks not displaying"

**Symptoms**: Dashboard shows loading spinner indefinitely

**Solutions**:
1. Check browser console for errors
2. Verify GET /tasks endpoint returns 200
3. Check response format matches Task[] type
4. Verify user_id filtering on backend

### Issue: "Styles not applying"

**Symptoms**: Tailwind classes not working

**Solutions**:
1. Verify Tailwind is configured: Check `tailwind.config.js`
2. Ensure globals.css imports Tailwind: `@tailwind base; @tailwind components; @tailwind utilities;`
3. Restart dev server: `npm run dev`
4. Clear Next.js cache: `rm -rf .next`

---

## Environment Configuration

### Development Environment

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production Environment

```bash
# .env.production
NEXT_PUBLIC_API_URL=https://api.production-domain.com
```

**Deployment Notes**:
- Set environment variables in hosting platform (Vercel, Netlify, etc.)
- Ensure HTTPS is enabled
- Configure CORS on backend to allow production frontend URL

---

## Code Quality Standards

### TypeScript

- Use strict mode: `"strict": true` in tsconfig.json
- Define types for all props and state
- Avoid `any` type - use `unknown` if type is truly unknown
- Use type guards for runtime type checking

### React Best Practices

- Use functional components with hooks
- Implement proper error boundaries
- Memoize expensive computations with useMemo
- Memoize callbacks with useCallback
- Use React.memo for expensive components

### Tailwind CSS

- Use utility classes directly in JSX
- Follow mobile-first responsive design
- Use Tailwind's spacing scale (4px increments)
- Avoid custom CSS unless absolutely necessary

### Code Organization

- One component per file
- Colocate related files (component + styles + tests)
- Use barrel exports (index.ts) for cleaner imports
- Keep components small and focused (< 200 lines)

---

## Performance Optimization

### Bundle Size

- Analyze bundle: `npm run build` and check output
- Lazy load routes with dynamic imports
- Tree-shake unused code
- Minimize dependencies

### Runtime Performance

- Use React.memo for expensive components
- Implement virtualization for long lists (if needed)
- Debounce search inputs
- Optimize images with Next.js Image component

### Network Performance

- Implement optimistic updates for better UX
- Cache API responses when appropriate
- Minimize API calls (batch when possible)
- Use loading states to prevent duplicate requests

---

## Debugging Tips

### Browser DevTools

**Console**: Check for JavaScript errors and warnings
**Network**: Inspect API requests and responses
**Application**: View localStorage, cookies, and cache
**React DevTools**: Inspect component tree and props

### Common Debug Commands

```bash
# Clear Next.js cache
rm -rf .next

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check TypeScript errors
npx tsc --noEmit

# Run linter
npm run lint
```

### Logging Best Practices

```typescript
// Development logging
if (process.env.NODE_ENV === 'development') {
  console.log('Debug info:', data);
}

// Never log sensitive data
// ❌ console.log('Token:', token);
// ✅ console.log('Token exists:', !!token);
```

---

## Next Steps

After completing the implementation:

1. **Run full test suite**: Complete manual testing checklist
2. **Performance audit**: Check bundle size and load times
3. **Security review**: Verify token handling and input sanitization
4. **Documentation**: Update README with setup instructions
5. **Demo preparation**: Prepare demo script for judges
6. **Deployment**: Deploy to production environment

---

## Additional Resources

### Documentation

- Next.js Docs: https://nextjs.org/docs
- React Docs: https://react.dev
- Tailwind CSS Docs: https://tailwindcss.com/docs
- TypeScript Docs: https://www.typescriptlang.org/docs

### Tools

- React DevTools: Browser extension for debugging React
- Tailwind CSS IntelliSense: VS Code extension for Tailwind
- ESLint: Code linting and formatting
- Prettier: Code formatting (optional)

### Backend Integration

- Refer to Spec-1 for backend API documentation
- Refer to Spec-2 for authentication flow details
- Check backend README for setup instructions

---

## Support

For issues or questions:
1. Check this quickstart guide
2. Review API contracts in `contracts/api-endpoints.md`
3. Check data models in `data-model.md`
4. Review architectural plan in `plan.md`
5. Consult backend documentation (Spec-1, Spec-2)

# Research: Frontend Application & Full-Stack Integration

**Feature**: 003-frontend-integration
**Date**: 2026-02-07
**Phase**: Phase 0 - Research & Technology Decisions

## Overview

This document captures research findings and technology decisions for building a Next.js frontend that integrates with existing FastAPI backend and Better Auth authentication system.

## Key Technology Decisions

### Decision 1: Next.js App Router vs Pages Router

**Decision**: Use Next.js App Router (v13+)

**Rationale**:
- Modern React patterns (Server Components, Suspense)
- Better file-based routing with layouts
- Improved performance with automatic code splitting
- Native support for loading and error states
- Aligns with Next.js 16+ requirement from spec

**Alternatives Considered**:
- **Pages Router**: Older, more stable, but lacks modern features
- **Create React App**: Simpler but requires manual routing setup
- **Vite + React Router**: Fast but more configuration needed

**Best Practices**:
- Use route groups `(auth)` for logical organization
- Implement layouts for shared UI and auth guards
- Leverage Server Components for static content
- Use Client Components only when needed (forms, interactivity)

### Decision 2: Token Storage Strategy

**Decision**: localStorage with React Context for token management

**Rationale**:
- Simple implementation suitable for hackathon demo
- Enables session persistence across page refreshes
- Easy to implement with React Context API
- No backend cookie handling required

**Alternatives Considered**:
- **HTTP-only cookies**: More secure but requires backend cookie support
- **sessionStorage**: More secure but loses auth on tab close
- **Memory only**: Most secure but requires re-login on refresh

**Security Considerations**:
- Vulnerable to XSS attacks if not properly sanitized
- Should implement Content Security Policy (CSP)
- Document security limitations
- Plan migration to HTTP-only cookies for production

**Best Practices**:
- Never log tokens to console
- Clear token on signout
- Validate token format before storage
- Implement token expiration handling

### Decision 3: State Management Approach

**Decision**: React Context for auth state, local component state for UI

**Rationale**:
- Built-in React feature, no external dependencies
- Sufficient for small application scope
- Simple to understand and maintain
- Avoids over-engineering

**Alternatives Considered**:
- **Redux**: Overkill for this scope, adds complexity
- **Zustand**: Lightweight but unnecessary for simple state
- **Jotai/Recoil**: Atomic state management, too complex for needs

**Best Practices**:
- Single AuthContext for global auth state
- Memoize context values to prevent unnecessary re-renders
- Use custom hooks (useAuth) for cleaner component code
- Keep UI state local to components when possible

### Decision 4: API Client Architecture

**Decision**: Centralized fetch wrapper with automatic token injection

**Rationale**:
- DRY principle - single place for API configuration
- Consistent error handling across all requests
- Automatic token injection for authenticated requests
- Easy to add interceptors or logging

**Alternatives Considered**:
- **Axios**: Popular but adds dependency, fetch is native
- **React Query**: Excellent for caching but overkill for scope
- **Direct fetch calls**: Simple but leads to code duplication

**Best Practices**:
- Base URL from environment variables
- Automatic JSON parsing
- Standardized error handling
- Request/response interceptors for logging
- Timeout handling for slow networks

### Decision 5: Form Validation Strategy

**Decision**: Client-side validation with HTML5 + custom JavaScript

**Rationale**:
- Immediate user feedback
- Reduces unnecessary API calls
- Native browser validation is fast
- Custom validation for business rules

**Alternatives Considered**:
- **React Hook Form**: Excellent library but adds dependency
- **Formik**: Popular but heavier than needed
- **Yup/Zod**: Schema validation, overkill for simple forms

**Best Practices**:
- Validate on blur for better UX
- Show errors inline below fields
- Disable submit button during validation
- Always validate on backend as well (defense in depth)

### Decision 6: Styling Approach

**Decision**: Tailwind CSS for utility-first styling

**Rationale**:
- Rapid development with utility classes
- Consistent design system out of the box
- Excellent responsive design utilities
- Small bundle size with purging
- Industry standard for modern web apps

**Alternatives Considered**:
- **CSS Modules**: More verbose, harder to maintain
- **Styled Components**: Runtime overhead, not needed
- **Plain CSS**: Too much boilerplate for rapid development

**Best Practices**:
- Use Tailwind's spacing scale (4px increments)
- Leverage responsive modifiers (sm:, md:, lg:)
- Create component classes for repeated patterns
- Use @apply sparingly (prefer utility classes)

### Decision 7: Error Handling Strategy

**Decision**: Centralized error handling with user-friendly messages

**Rationale**:
- Consistent error UX across application
- Maps technical errors to user-friendly messages
- Handles network failures gracefully
- Provides actionable feedback

**Error Mapping Strategy**:
- 401 → "Please sign in again" + redirect to /signin
- 403 → "You don't have permission to do that"
- 404 → "We couldn't find what you're looking for"
- 422 → Display validation errors from backend
- 500 → "Something went wrong, please try again"
- Network error → "Connection failed, check your internet"

**Best Practices**:
- Never show raw error messages to users
- Log detailed errors to console for debugging
- Provide retry options for transient failures
- Show loading states to prevent confusion

## Integration Research

### Backend API Contract (from Spec-1 and Spec-2)

**Authentication Endpoints**:
- `POST /auth/signup`: User registration
- `POST /auth/signin`: User authentication (returns JWT)
- `POST /auth/signout`: Optional logout endpoint

**Task Endpoints**:
- `GET /tasks`: Fetch user's tasks (requires auth)
- `POST /tasks`: Create task (requires auth)
- `PUT /tasks/:id`: Update task (requires auth)
- `DELETE /tasks/:id`: Delete task (requires auth)

**Authentication Flow**:
1. User signs in → Backend returns JWT token
2. Frontend stores token
3. Frontend includes token in Authorization header: `Bearer <token>`
4. Backend verifies token and extracts user_id
5. Backend filters all queries by user_id

**Assumptions Validated**:
- Backend uses RESTful conventions ✓
- Backend returns JSON responses ✓
- Backend accepts Bearer token in Authorization header ✓
- Backend handles token validation ✓
- Backend enforces user data isolation ✓

### Next.js Best Practices for Authentication

**Route Protection**:
- Use middleware.ts for server-side route protection
- Implement client-side guards for UX (loading states)
- Redirect unauthenticated users to /signin
- Redirect authenticated users away from /signin, /signup

**Token Management**:
- Store token in localStorage for persistence
- Load token on app initialization
- Clear token on signout or 401 response
- Validate token format before using

**Performance Optimization**:
- Use Server Components for static content
- Use Client Components for interactive elements
- Implement loading states with Suspense
- Lazy load components when appropriate

## Testing Strategy

### Manual Testing Checklist

**Authentication Flow**:
- [ ] User can sign up with valid email/password
- [ ] User cannot sign up with invalid email
- [ ] User cannot sign up with weak password
- [ ] User can sign in with correct credentials
- [ ] User cannot sign in with wrong credentials
- [ ] User stays signed in after page refresh
- [ ] User can sign out successfully

**Task Management**:
- [ ] User can create task with valid title
- [ ] User cannot create task with empty title
- [ ] User can view all their tasks
- [ ] User can update task title
- [ ] User can toggle task completion
- [ ] User can delete task with confirmation
- [ ] Changes persist after page refresh

**Route Protection**:
- [ ] Unauthenticated user redirected from /dashboard
- [ ] Authenticated user redirected from /signin
- [ ] Back button doesn't bypass protection

**Error Handling**:
- [ ] Network errors show friendly message
- [ ] 401 errors clear token and redirect
- [ ] Validation errors display inline
- [ ] API errors don't crash the app

**Responsive Design**:
- [ ] Works on mobile (320px width)
- [ ] Works on tablet (768px width)
- [ ] Works on desktop (1920px width)
- [ ] Touch targets are 44x44px minimum

### Browser Compatibility

**Target Browsers**:
- Chrome 90+ (primary)
- Firefox 88+ (secondary)
- Safari 14+ (secondary)
- Edge 90+ (secondary)

**Features Used**:
- Fetch API (widely supported)
- localStorage (widely supported)
- CSS Grid/Flexbox (widely supported)
- ES6+ JavaScript (transpiled by Next.js)

## Performance Considerations

### Bundle Size Optimization

**Strategies**:
- Tree-shaking unused code
- Code splitting by route
- Lazy loading components
- Minimize dependencies

**Target Metrics**:
- Initial bundle < 200KB gzipped
- Time to Interactive < 3 seconds
- First Contentful Paint < 1.5 seconds

### Network Optimization

**Strategies**:
- Minimize API calls (batch when possible)
- Implement optimistic updates
- Cache static assets
- Use compression (gzip/brotli)

**Target Metrics**:
- API response time < 500ms (backend responsibility)
- UI feedback < 100ms (frontend responsibility)

## Security Considerations

### XSS Prevention

**Strategies**:
- React's built-in XSS protection (escapes by default)
- Sanitize user input before display
- Use Content Security Policy headers
- Avoid dangerouslySetInnerHTML

### CSRF Prevention

**Strategies**:
- Backend validates JWT token (not cookies)
- No state-changing GET requests
- SameSite cookie attribute (if using cookies)

### Token Security

**Strategies**:
- Never expose token in URLs
- Never log token to console in production
- Clear token on signout
- Implement token expiration handling
- Use HTTPS in production

## Deployment Considerations

### Environment Configuration

**Development**:
- `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Hot reload enabled
- Source maps enabled

**Production**:
- `NEXT_PUBLIC_API_URL=https://api.production-domain.com`
- Minification enabled
- Source maps disabled
- HTTPS enforced

### Build Process

**Steps**:
1. Install dependencies: `npm install`
2. Build application: `npm run build`
3. Start production server: `npm start`

**Optimization**:
- Static page generation where possible
- Image optimization with Next.js Image
- Font optimization with Next.js Font

## Conclusion

All technology decisions are finalized and documented. No additional research required. Ready to proceed to Phase 1 (Design & Contracts).

**Key Takeaways**:
- Next.js App Router provides modern patterns for our needs
- localStorage + Context is sufficient for auth state management
- Centralized API client ensures consistency
- Tailwind CSS enables rapid UI development
- Manual testing will validate all requirements
- Security considerations are documented and will be implemented

**Next Steps**:
- Create data-model.md (Phase 1)
- Generate API contracts (Phase 1)
- Create quickstart.md (Phase 1)
- Update agent context (Phase 1)

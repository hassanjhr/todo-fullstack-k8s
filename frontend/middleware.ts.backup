import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Next.js Middleware for Route Protection
 * Protects routes that require authentication
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Get token from localStorage (client-side only)
  // Note: Middleware runs on server, so we can't access localStorage directly
  // We'll rely on client-side auth guards for now

  // Protected routes
  const protectedRoutes = ['/dashboard'];
  const authRoutes = ['/signin', '/signup'];

  const isProtectedRoute = protectedRoutes.some((route) => pathname.startsWith(route));
  const isAuthRoute = authRoutes.some((route) => pathname.startsWith(route));

  // For now, let client-side guards handle redirects
  // This middleware can be enhanced with cookie-based auth if needed

  return NextResponse.next();
}

/**
 * Configure which routes to run middleware on
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};

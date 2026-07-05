import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token')?.value
  const { pathname } = request.nextUrl

  // Identify path categories
  const isProtectedPath =
    pathname.startsWith('/dashboard') ||
    pathname.startsWith('/feed') ||
    pathname.startsWith('/simulation') ||
    pathname.startsWith('/reports') ||
    pathname.startsWith('/analytics') ||
    pathname.startsWith('/data') ||
    pathname === '/'

  const isAuthPath = pathname.startsWith('/login') || pathname.startsWith('/signup')

  // Enforce session access logic
  if (isProtectedPath) {
    if (!token) {
      const loginUrl = request.nextUrl.clone()
      loginUrl.pathname = '/login'
      return NextResponse.redirect(loginUrl)
    }
    
    // Redirect base path to the default dashboard route
    if (pathname === '/') {
      const dashboardUrl = request.nextUrl.clone()
      dashboardUrl.pathname = '/dashboard'
      return NextResponse.redirect(dashboardUrl)
    }
  }

  // Redirect authenticated users away from login/signup to dashboard
  if (isAuthPath && token) {
    const dashboardUrl = request.nextUrl.clone()
    dashboardUrl.pathname = '/dashboard'
    return NextResponse.redirect(dashboardUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/',
    '/dashboard/:path*',
    '/feed/:path*',
    '/simulation/:path*',
    '/reports/:path*',
    '/analytics/:path*',
    '/data/:path*',
    '/login',
    '/signup',
  ],
}

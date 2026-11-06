import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Rutas protegidas (Resto del sistema)
  if (pathname.startsWith('/dashboard') && !pathname.startsWith('/dashboard/login') && !pathname.startsWith('/dashboard/registro')) {
    const token = request.cookies.get('sarita-auth')?.value;
    if (!token) {
      return NextResponse.redirect(new URL('/dashboard/login', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*'],
};

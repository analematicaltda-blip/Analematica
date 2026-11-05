import { MetadataRoute } from 'next';
import { getPrestadores, getCategorias } from '@/services/api';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://sarita.travel';

  // Páginas estáticas
  const routes = [
    '',
    '/descubre',
    '/directorio',
    '/login',
    '/dashboard/registro',
  ].map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: 'daily' as const,
    priority: route === '' ? 1 : 0.8,
  }));

  // Páginas dinámicas de prestadores
  try {
    const prestadores = await getPrestadores();
    const prestadorRoutes = (prestadores || []).map((p: any) => ({
        url: `${baseUrl}/directorio/${p.id}`,
        lastModified: new Date(),
        changeFrequency: 'weekly' as const,
        priority: 0.6,
    }));

    return [...routes, ...prestadorRoutes];
  } catch (e) {
    return routes;
  }
}

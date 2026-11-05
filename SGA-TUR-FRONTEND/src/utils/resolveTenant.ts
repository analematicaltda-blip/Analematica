/**
 * Hallazgo 13: Sistema jerárquico de resolución de tenant.
 * Evita estados de carga infinita en el Sidebar.
 */

function getTenantFromSubdomain(): string | null {
  if (typeof window === 'undefined') return null;
  const host = window.location.hostname;
  const parts = host.split('.');

  // Ignorar localhost y IPs
  if (host === 'localhost' || host === '127.0.0.1' || /^(\d{1,3}\.){3}\d{1,3}$/.test(host)) {
    return null;
  }

  if (parts.length > 2) {
    return parts[0];
  }
  return null;
}

function getTenantFromHeader(): string | null {
  // En Next.js cliente, esto es limitado, pero se puede simular si se inyecta
  return null;
}

export function resolveTenant(): string {
  if (typeof window === 'undefined') return 'dev_tenant';

  const subdomainTenant = getTenantFromSubdomain();
  if (subdomainTenant) return subdomainTenant;

  const headerTenant = getTenantFromHeader();
  if (headerTenant) return headerTenant;

  const localTenant = localStorage.getItem('tenant');
  if (localTenant) return localTenant;

  return 'dev_tenant';
}

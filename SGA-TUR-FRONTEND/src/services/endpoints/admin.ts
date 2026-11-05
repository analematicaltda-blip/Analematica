import httpClient from '../index';

export const adminEndpoints = {
  getIntelligenceProposals: () => httpClient.get('/admin/intelligence/proposals/'),
  runAnalysis: () => httpClient.post('/admin/intelligence/proposals/run_analysis/'),
  approveProposal: (id: string) => httpClient.post(`/admin/intelligence/proposals/${id}/approve/`),
  executeProposal: (id: string) => httpClient.post(`/admin/intelligence/proposals/${id}/execute/`),
  getAuditLogs: () => httpClient.get('/api/audit-logs/'),
};

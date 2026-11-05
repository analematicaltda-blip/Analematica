'use client';

import useSWR from 'swr';
import { adminEndpoints } from '@/services/endpoints/admin';

const fetcher = (fn: () => Promise<any>) => fn().then(res => res.data);

export function useIntelligenceApi() {
  const { data, error, isLoading, mutate } = useSWR('admin_proposals', () => adminEndpoints.getIntelligenceProposals().then(res => res.data));

  const runAnalysis = async () => {
    await adminEndpoints.runAnalysis();
    mutate();
  };

  const approveProposal = async (id: string) => {
    await adminEndpoints.approveProposal(id);
    mutate();
  };

  const executeProposal = async (id: string) => {
    await adminEndpoints.executeProposal(id);
    mutate();
  };

  return {
    proposals: data?.results || [],
    isLoading,
    isError: error,
    runAnalysis,
    approveProposal,
    executeProposal
  };
}

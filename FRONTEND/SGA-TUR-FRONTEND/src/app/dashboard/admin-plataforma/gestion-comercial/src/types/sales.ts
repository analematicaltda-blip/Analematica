
// Corresponds to the Opportunity model in the Django backend
export interface Opportunity {
    id: number;
    name: string;
    stage: 'new' | 'contacted' | 'proposal' | 'negotiation' | 'won' | 'lost';
    value: number;
    // Add other fields from the Django model as needed for the frontend
    // For example:
    company_name: string;
    last_updated: string;
    // It's good practice to mirror the backend model closely
    // but only include what the frontend component actually needs.
}

// Keep other sales-related types here for better organization
export interface Seller {
    id: string;
    name: string;
    avatarUrl: string;
}

export type PipelineStage = 'new' | 'contacted' | 'proposal' | 'negotiation' | 'won' | 'lost';

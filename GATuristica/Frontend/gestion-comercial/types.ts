

import type React from 'react';

export enum AppView {
  COMMUNICATION = 'communication',
  RESPONSES = 'responses',
  AI_STUDIO = 'ai_studio',
  AUTOMATION = 'automation',
  SETTINGS = 'settings',
  ADMIN = 'admin',
  FUNNELS = 'funnels',
  PLAYBOOKS = 'playbooks',
  ADMIN_PANEL = 'admin_panel',
}

export interface ChatMessage {
  role: 'user' | 'model' | 'tool';
  parts: { text: string }[];
}

export interface PlaybookSection {
    title: string;
    content: string;
}
export interface Playbook {
    title: string;
    macro_flow: string[];
    sections: PlaybookSection[];
    tech_stack: {
        name: string;
        tool: string;
        icon: React.FC<{className?: string}>;
    }[];
}

export type PipelineStage = 'new' | 'contacted' | 'proposal' | 'negotiation' | 'won' | 'lost';

export interface Interaction {
    id: string;
    type: 'message' | 'call' | 'email' | 'meeting';
    date: string;
    notes: string;
    platform?: string; // e.g., 'WhatsApp', 'Facebook'
}

export interface Contact {
    id: string;
    name: string;
    role: string;
    email: string;
    phone: string;
}

export interface Quote {
    id: string;
    number: string;
    date: string;
    amount: number;
    status: 'draft' | 'sent' | 'accepted' | 'rejected';
    paid?: boolean; // Added for sales cycle completion
}

export interface Task {
    id:string;
    title: string;
    dueDate: string;
    completed: boolean;
}

export interface Seller {
    id: string;
    name: string;
    avatarUrl?: string;
}

// --- SUPPORT TYPES ---
export type TicketStatus = 'new' | 'in-progress' | 'resolved';
export type TicketPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface TicketMessage {
    id: string;
    author: string; // "Customer" or agent's name
    authorAvatarUrl?: string;
    text: string;
    timestamp: string;
    type: 'reply' | 'internal-note';
}

export interface Ticket {
    id: string;
    subject: string;
    customerId: number;
    status: TicketStatus;
    priority: TicketPriority;
    category: string;
    assigneeId?: string; // Seller ID
    createdAt: string;
    slaExpiresAt: string;
    conversation: TicketMessage[];
    satisfactionRating?: number; // Added for CSAT
}

export interface KnowledgeBaseArticle {
    id: string;
    title: string;
    category: string;
    excerpt: string;
}

export interface Customer {
    id: number;
    name: string;
    company: string;
    avatarUrl: string;
    socials: { [key: string]: string };
    priority: 'high' | 'medium' | 'low';
    tags: string[];
    pipelineStage: PipelineStage;
    opportunityValue: number;
    assignedTo: string; // Seller ID
    lastUpdated: string; // ISO date string for inactivity check
    interactions: Interaction[];
    contacts: Contact[];
    quotes: Quote[];
    tasks: Task[];
    tickets: Ticket[];
}

// --- MARKETING TYPES ---
export interface Segment {
  id: string;
  name: string;
  contactCount: number;
  criteria: string; // e.g., "Priority is high AND stage is negotiation"
}

export interface CampaignAnalytics {
    id: string;
    name: string;
    channel: string;
    sent: number;
    openRate: number;
    clickRate: number;
    conversions: number;
    date: string;
}

export interface MarketingChannel {
    id: 'email' | 'whatsapp' | 'sms' | 'mms' | 'facebook' | 'instagram' | 'x' | 'tiktok' | 'youtube' | 'twitch';
    name: string;
    icon: React.FC<{className?: string}>;
    status: 'connected' | 'disconnected';
    category: 'messaging' | 'social';
}

export interface EmailTemplateProductCard {
    id: string;
    imageUrl: string;
    description: string;
    price: string;
    ctaUrl: string;
    ctaText: string;
}

export interface EmailTemplate {
    header: {
        logoUrl: string;
        menuItems: { text: string; url: string }[];
    };
    body: {
        title: string;
        subtitle: string;
        products: EmailTemplateProductCard[];
    };
    footer: {
        companyName: string;
        address: string;
        phone: string;
        email: string;
    };
}


// --- INTEGRATION TYPES ---
export type IntegrationCategory = 'ads' | 'communication' | 'social' | 'erp';
export type IntegrationStatus = 'connected' | 'disconnected';

export interface Integration {
  id: string;
  name: string;
  category: IntegrationCategory;
  status: IntegrationStatus;
}

// --- ADMIN & ANALYTICS TYPES ---
export type Role = 'Admin' | 'Vendedor' | 'Soporte' | 'Marketing';
export type Permission = 'view_financials' | 'export_data' | 'manage_users' | 'delete_contacts';

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  avatarUrl: string;
  permissions: Permission[];
}

export interface AuditLog {
  id: string;
  userName: string;
  userAvatarUrl: string;
  action: string;
  timestamp: string;
}
// --- AI STUDIO & SCHEDULER ---
export type PlatformID = 'facebook' | 'instagram' | 'tiktok' | 'youtube' | 'x';
export type SelectedPlatforms = { [key in PlatformID]?: string[] };

export interface ContentToSchedule {
    contentUrl: string;
    selectedPlatforms: SelectedPlatforms;
}


export interface GroundingChunk {
  web?: {
    uri: string;
    title: string;
  };
  maps?: {
    uri: string;
    title: string;
    placeAnswerSources?: {
      reviewSnippets: {
        uri: string;
        text: string;
      }[];
    };
  };
}

export type LLMProvider = 'gemini' | 'ollama';

// --- NEW FUNNEL & BLOCK HIERARCHY (V2) ---

export interface CadenaTurismo {
  id: string;
  nombre: string;
  logo?: string;
  color_primario: string;
  color_secundario: string;
}

export interface Categoria {
  id: string;
  cadenaId: string;
  nombre: string;
  icon?: React.FC<{className?: string}> | string;
}

export interface Subcategoria {
  id: string;
  categoriaId: string;
  nombre: string;
  descripcion?: string;
}

export interface LandingPage {
  id: string;
  subcategoriaId: string;
  nombre: string;
  dominio?: string;
  publicada: boolean;
  funnels: Funnel[];
}

export type FunnelPageType = 'offer' | 'thankyou' | 'upsell' | 'downsell';

export interface FunnelPage {
    id: string;
    name: string;
    path: string; // e.g., '/oferta-especial'
    type: FunnelPageType;
    blocks: Block[];
    metaTitle?: string;
    metaDescription?: string;
}

export interface Funnel {
  id: string;
  landingPageId: string;
  name: string;
  pages: FunnelPage[];
  isTemplate?: boolean;
  thumbnailUrl?: string;
  theme: ThemeSettings;
}

// Block Model based on the new JSON schema
export type LandingPageBlockType = 'header' | 'hero' | 'services' | 'video' | 'gallery' | 'slider' | 'form' | 'cta' | 'footer' | 'custom' | 'testimonials' | 'pricing' | 'faq' | 'featureGrid' | 'countdown' | 'text' | 'logos' | 'html' | 'socialShare' | 'embed';

export type PropValue = string | number | boolean | object | Array<string | object> | null;
export type PropType = 'string' | 'longtext' | 'html' | 'array:image' | 'array:string' | 'array:object' | 'object' | 'number' | 'boolean' | 'color' | 'icon' | 'url' | 'image';

export interface BlockProp {
  value: PropValue;
  type: PropType;
  label: string;
  options?: any; 
  category: 'content' | 'style' | 'setting';
}

export interface BlockProps {
  [key: string]: BlockProp;
}

export interface ResponsiveOverrides {
  stack?: boolean;
  hidden?: boolean;
  props?: Partial<BlockProps>;
}

export interface ResponsiveSettings {
  desktop: { overrides: ResponsiveOverrides };
  tablet: { overrides: ResponsiveOverrides };
  mobile: { overrides: ResponsiveOverrides };
}

export interface BlockStyles {
    padding: { top: number; right: number; bottom: number; left: number };
    backgroundColor: string;
    textColor: string;
    textAlign: 'left' | 'center' | 'right';
}

export interface Block {
  id: string;
  template_id?: string | null;
  type: LandingPageBlockType;
  name: string;
  order: number;
  locked: boolean;
  props: BlockProps;
  styles: BlockStyles; // ADDED FOR STYLE MANAGEMENT
  responsive: ResponsiveSettings;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface ThemeSettings {
    font: {
        headings: string;
        body: string;
    };
    colors: {
        primary: string;
        secondary: string;
        accent: string;
        text: string;
    }
}
export interface Asset {
    id: string;
    url: string;
    name: string;
    type: 'image' | 'video';
}


declare global {
  interface AIStudio {
      hasSelectedApiKey: () => Promise<boolean>;
      openSelectKey: () => Promise<void>;
  }

  interface Window {
    aistudio?: AIStudio;
    webkitAudioContext: typeof AudioContext;
  }
}
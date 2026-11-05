import api from './api';

export interface SocialConversation {
  id: string;
  conversation_type: 'direct' | 'group' | 'public_room' | 'private_room';
  title: string;
  entry_fee?: string;
  is_adult_only?: boolean;
  created_by: string | null;
  created_at: string;
  updated_at: string;
  memberships: Array<{
    id: string;
    conversation: string;
    user: string;
    is_admin: boolean;
    joined_at: string;
    last_seen_at: string;
  }>;
}

export interface SocialMessage {
  id: string;
  conversation: string;
  sender: string;
  message_type: 'text' | 'emoji' | 'file' | 'voice' | 'gift';
  content: string;
  is_deleted: boolean;
  created_at: string;
  attachments: Array<{
    id: string;
    attachment_type: 'image' | 'video' | 'file' | 'audio';
    file_url: string;
    mime_type: string;
    size_bytes: number;
    uploaded_at: string;
  }>;
}

export interface SocialProfileMedia {
  id: string;
  media_type: 'image' | 'video';
  media_url: string;
  order: number;
}

export interface SocialPreference {
  id: string;
  user: string;
  bio: string;
  interests: string[];
  preferred_languages: string[];
  preferred_destinations: string[];
  is_dating_active?: boolean;
  presentation_photo?: string;
  presentation_video?: string;
  media_gallery?: SocialProfileMedia[];
  visibility_enabled: boolean;
  updated_at: string;
}

export interface SocialGiftCatalog {
  id: string;
  code: string;
  name: string;
  description: string;
  price: string;
  icon_url: string;
  active: boolean;
}

export interface SocialGiftTransaction {
  id: string;
  sender: string;
  receiver: string;
  gift: string;
  conversation: string | null;
  amount: string;
  status: 'pending' | 'completed' | 'failed';
  external_reference: string;
  created_at: string;
  processed_at: string | null;
}

export const listSocialConversations = async (): Promise<SocialConversation[]> => {
  const { data } = await api.get('/social/conversations/');
  return data?.results ?? data ?? [];
};

export const createSocialConversation = async (payload: {
  conversation_type?: 'direct' | 'group' | 'public_room' | 'private_room';
  title?: string;
  entry_fee?: number;
  is_adult_only?: boolean;
}): Promise<SocialConversation> => {
  const { data } = await api.post('/social/conversations/', payload);
  return data;
};

export const joinSocialConversation = async (conversationId: string) => {
  const { data } = await api.post(`/social/conversations/${conversationId}/join/`);
  return data;
};

export const addSocialMember = async (conversationId: string, user_id: string) => {
  const { data } = await api.post(`/social/conversations/${conversationId}/add_member/`, { user_id });
  return data;
};

export const listSocialMessages = async (conversationId: string): Promise<SocialMessage[]> => {
  const { data } = await api.get('/social/messages/', { params: { conversation_id: conversationId } });
  return data?.results ?? data ?? [];
};

export const sendSocialMessage = async (payload: {
  conversation: string;
  message_type?: 'text' | 'emoji' | 'file' | 'voice' | 'gift';
  content: string;
}): Promise<SocialMessage> => {
  const { data } = await api.post('/social/messages/', payload);
  return data;
};

export const listSocialGiftCatalog = async (): Promise<SocialGiftCatalog[]> => {
  const { data } = await api.get('/social/gift-catalog/');
  return data?.results ?? data ?? [];
};

export const sendSocialGift = async (payload: {
  receiver_id: string;
  gift_id: string;
  conversation_id?: string;
}): Promise<SocialGiftTransaction> => {
  const { data } = await api.post('/social/gift-transactions/send_gift/', payload);
  return data;
};

export const listSocialGiftTransactions = async (): Promise<SocialGiftTransaction[]> => {
  const { data } = await api.get('/social/gift-transactions/');
  return data?.results ?? data ?? [];
};

export const listSocialSuggestions = async (): Promise<SocialPreference[]> => {
  const { data } = await api.get('/social/preferences/suggestions/');
  return data?.results ?? data ?? [];
};

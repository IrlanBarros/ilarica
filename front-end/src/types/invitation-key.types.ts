export interface InvitationKeyBase {
  key: string;
  issued_to_email: string;
  expires_at: string;
  is_used: boolean;
  is_expired: boolean;
}

export interface InvitationKey extends InvitationKeyBase {
  id: string;
  used_by_user_id: string | null;
}

export interface InvitationKeyCreate {
  key: string;
  issued_to_email: string;
  expires_at: string;
  is_used?: boolean;
  is_expired?: boolean;
}

export interface InvitationKeyUpdate {
  key?: string | null;
  issued_to_email?: string | null;
  expires_at?: string | null;
  is_used?: boolean | null;
  is_expired?: boolean | null;
}
// web/src/api/chat.ts
export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  // add more fields if your API returns them
}

const RAW_BASE =
  (typeof import.meta !== 'undefined' && import.meta.env?.VITE_CHAT_API_BASE) ||
  'http://mental-health-prod-v2.eba-cxhtfs2h.us-east-1.elasticbeanstalk.com';

export const CHAT_API_BASE = RAW_BASE.replace(/\/$/, '');

const CHAT_API_URL = `${CHAT_API_BASE}/chat/chat-sessions/`;
const CHAT_MESSAGE_URL = `${CHAT_API_BASE}/chat/chat-message/`;


export async function fetchChatSessions(): Promise<ChatSession[]> {
  const response = await fetch(CHAT_API_URL, {
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`HTTP ${response.status} on ${CHAT_API_URL}: ${text.slice(0, 120)}`);
  }

  const data = await response.json();
  return data as ChatSession[];
}

export interface ChatReply {
  response: string;
  session_id: string | null;
  language?: string;
}

export async function sendMessageToAPI(message: string, sessionId: string | null, language: string): Promise<ChatReply> {
  const response = await fetch(CHAT_MESSAGE_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      language,
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`HTTP ${response.status}: ${text}`);
  }

  return response.json() as Promise<ChatReply>;
}

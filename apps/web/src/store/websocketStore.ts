'use client';

import { create } from 'zustand';

interface NotificationItem {
  id: string;
  category: string;
  title: string;
  message: string;
  read_at: string | null;
  created_at: string;
}

interface WebSocketState {
  socket: WebSocket | null;
  status: 'connecting' | 'connected' | 'disconnected';
  activeUsers: string[];
  notifications: NotificationItem[];
  jobProgress: Record<string, { stage: string; status: string; error_message?: string }>;
  connect: (token: string, workspaceId: string) => void;
  disconnect: () => void;
  broadcast: (data: Record<string, unknown>) => void;
}

let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
let reconnectAttempts = 0;

export const useWebSocketStore = create<WebSocketState>((set, get) => ({
  socket: null,
  status: 'disconnected',
  activeUsers: [],
  notifications: [],
  jobProgress: {},

  connect: (token, workspaceId) => {
    // 1. Clear any existing connections
    const currentSocket = get().socket;
    if (currentSocket) {
      currentSocket.close();
    }
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout);
    }

    set({ status: 'connecting' });
    
    // Construct secure or standard websocket URI
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.NEXT_PUBLIC_API_URL 
      ? new URL(process.env.NEXT_PUBLIC_API_URL).host
      : 'localhost:8000';
      
    const url = `${protocol}//${host}/api/v1/collaboration/ws?token=${token}&workspace_id=${workspaceId}`;
    
    const socket = new WebSocket(url);

    socket.onopen = () => {
      reconnectAttempts = 0;
      set({ socket, status: 'connected' });
      console.log('WebSocket connected to workspace:', workspaceId);
    };

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const { event: eventName, data } = payload;
        
        switch (eventName) {
          case 'presence':
            set({ activeUsers: data.active_users || [] });
            break;
          case 'notification_received':
            set((state) => ({
              notifications: [data, ...state.notifications]
            }));
            break;
          case 'job_progress':
            set((state) => ({
              jobProgress: {
                ...state.jobProgress,
                [data.job_id]: {
                  stage: data.stage,
                  status: data.status,
                  error_message: data.error_message
                }
              }
            }));
            break;
          default:
            // Forward event via standard DOM custom event for context components (e.g. comments page)
            if (typeof window !== 'undefined') {
              const domEvent = new CustomEvent(`ws:${eventName}`, { detail: data });
              window.dispatchEvent(domEvent);
            }
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    socket.onclose = () => {
      set({ socket: null, status: 'disconnected' });
      // Implement exponential backoff reconnection
      reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
      console.log(`WebSocket closed. Reconnecting in ${delay}ms...`);
      reconnectTimeout = setTimeout(() => {
        get().connect(token, workspaceId);
      }, delay);
    };

    socket.onerror = (err) => {
      console.error('WebSocket error:', err);
    };
  },

  disconnect: () => {
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout);
    }
    const socket = get().socket;
    if (socket) {
      socket.close();
    }
    set({ socket: null, status: 'disconnected', activeUsers: [] });
  },

  broadcast: (data) => {
    const socket = get().socket;
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(data));
    } else {
      console.warn('Cannot send websocket message: Socket is not open.');
    }
  }
}));

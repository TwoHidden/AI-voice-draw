import { useState, useEffect, useRef, useCallback } from 'react';
import type { CanvasState, WSMessage } from '../types';

interface UseWebSocketOptions {
  url: string;
  onStateUpdate?: (state: CanvasState) => void;
  onAsrResult?: (text: string) => void;
  onOptimizeResult?: (result: import('../types').OptimizeResult) => void;
  onError?: (msg: string) => void;
}

export function useWebSocket({ url, onStateUpdate, onAsrResult, onOptimizeResult, onError }: UseWebSocketOptions) {
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const heartbeatRef = useRef<ReturnType<typeof setInterval> | undefined>(undefined);
  const retryCountRef = useRef(0);

  // 用 ref 保存最新回调，避免 useCallback 依赖链问题
  const callbacksRef = useRef({ onStateUpdate, onAsrResult, onOptimizeResult, onError });
  callbacksRef.current = { onStateUpdate, onAsrResult, onOptimizeResult, onError };

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      retryCountRef.current = 0;
      console.log('WebSocket 已连接');

      // 心跳
      heartbeatRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000);
    };

    ws.onmessage = (event) => {
      try {
        const msg: WSMessage = JSON.parse(event.data);
        const { onStateUpdate, onAsrResult, onOptimizeResult, onError } = callbacksRef.current;
        switch (msg.type) {
          case 'state_update':
            const data = msg.data as any;
            onStateUpdate?.({
              shapes: data.shapes || [],
              selectedId: data.selected_id ?? null,
            });
            break;
          case 'asr_result':
            onAsrResult?.(msg.data as string);
            break;
          case 'optimize_result':
            onOptimizeResult?.(msg.data as import('../types').OptimizeResult);
            break;
          case 'error':
            onError?.(msg.data as string);
            break;
          case 'pong':
            // 心跳响应，连接正常
            break;
        }
      } catch (e) {
        console.error('消息解析失败:', e);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      clearInterval(heartbeatRef.current);
      console.log('WebSocket 断开');

      // 指数退避重连（3s, 6s, 12s, 最大 30s）
      const delay = Math.min(3000 * Math.pow(2, retryCountRef.current), 30000);
      retryCountRef.current++;
      reconnectTimerRef.current = setTimeout(connect, delay);
    };

    ws.onerror = () => {
      setConnected(false);
      clearInterval(heartbeatRef.current);
    };
  }, [url]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimerRef.current);
      clearInterval(heartbeatRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const sendText = useCallback((text: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'text', data: text }));
    }
  }, []);

  const sendAudio = useCallback((blob: Blob) => {
    const ws = wsRef.current;
    if (ws?.readyState === WebSocket.OPEN) {
      blob.arrayBuffer().then(buf => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(buf);
        }
      });
    }
  }, []);

  return { connected, sendText, sendAudio };
}

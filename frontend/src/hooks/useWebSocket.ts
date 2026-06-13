import { useState, useEffect, useRef, useCallback } from 'react';
import type { CanvasState, ShapeResponse, WSMessage } from '../types';

interface UseWebSocketOptions {
  url: string;
  onStateUpdate?: (state: CanvasState) => void;
  onAsrResult?: (text: string) => void;
  onError?: (msg: string) => void;
}

function convertShape(s: ShapeResponse) {
  return {
    ...s,
    fill: s.fill,
    stroke: s.stroke,
  };
}

export function useWebSocket({ url, onStateUpdate, onAsrResult, onError }: UseWebSocketOptions) {
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>(undefined);
  const heartbeatRef = useRef<ReturnType<typeof setInterval>>(undefined);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
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
        switch (msg.type) {
          case 'state_update':
            const data = msg.data as any;
            onStateUpdate?.({
              shapes: (data.shapes || []).map(convertShape),
              selectedId: data.selected_id ?? null,
            });
            break;
          case 'asr_result':
            onAsrResult?.(msg.data as string);
            break;
          case 'error':
            onError?.(msg.data as string);
            break;
        }
      } catch (e) {
        console.error('消息解析失败:', e);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      clearInterval(heartbeatRef.current);
      console.log('WebSocket 断开，3秒后重连...');
      reconnectTimerRef.current = setTimeout(connect, 3000);
    };

    ws.onerror = () => {
      setConnected(false);
    };
  }, [url, onStateUpdate, onAsrResult, onError]);

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
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      blob.arrayBuffer().then(buf => wsRef.current?.send(buf));
    }
  }, []);

  return { connected, sendText, sendAudio };
}

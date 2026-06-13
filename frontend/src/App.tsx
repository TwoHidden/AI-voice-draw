import { useState, useCallback } from 'react';
import Canvas from './components/Canvas';
import VoicePanel from './components/VoicePanel';
import StatusPanel from './components/StatusPanel';
import { useWebSocket } from './hooks/useWebSocket';
import { useExport } from './hooks/useExport';
import type { CanvasState, OptimizeResult } from './types';
import './App.css';

const WS_URL = `ws://${window.location.hostname}:8000/ws`;

export default function App() {
  const [canvasState, setCanvasState] = useState<CanvasState>({ shapes: [], selectedId: null });
  const [asrResult, setAsrResult] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const [error, setError] = useState<string>('');
  const [optimizeResults, setOptimizeResults] = useState<OptimizeResult[]>([]);

  const handleStateUpdate = useCallback((state: CanvasState) => {
    setCanvasState(state);
    setIsProcessing(false);
    setHistory(prev => [...prev, `操作完成，当前 ${state.shapes.length} 个图形`]);
  }, []);

  const handleAsrResult = useCallback((text: string) => {
    setAsrResult(text);
    setHistory(prev => [...prev, `语音识别: ${text}`]);
  }, []);

  const handleError = useCallback((msg: string) => {
    setError(msg);
    setIsProcessing(false);
    setTimeout(() => setError(''), 3000);
  }, []);

  const { connected, sendText, sendAudio } = useWebSocket({
    url: WS_URL,
    onStateUpdate: handleStateUpdate,
    onAsrResult: handleAsrResult,
    onOptimizeResult: (result) => {
      setOptimizeResults(prev => [...prev.slice(-4), result]); // 保留最近5条
    },
    onError: handleError,
  });

  const { exportSVG, exportPNG } = useExport();

  const handleSendText = useCallback((text: string) => {
    setIsProcessing(true);
    setHistory(prev => [...prev, `发送指令: ${text}`]);
    sendText(text);
  }, [sendText]);

  const handleSendAudio = useCallback((blob: Blob) => {
    setIsProcessing(true);
    sendAudio(blob);
  }, [sendAudio]);

  return (
    <div className="app">
      {/* 错误提示 */}
      {error && <div className="error-bar">{error}</div>}

      {/* 头部 */}
      <header className="app-header">
        <h1>AI 语音绘图工具</h1>
        <div className="header-controls">
          <span className={`status ${connected ? 'online' : 'offline'}`}>
            {connected ? '🟢 已连接' : '🔴 未连接'}
          </span>
          <button onClick={exportSVG} className="export-btn">导出 SVG</button>
          <button onClick={exportPNG} className="export-btn">导出 PNG</button>
        </div>
      </header>

      {/* 主内容 */}
      <main className="app-main">
        <div className="canvas-area">
          <Canvas
            shapes={canvasState.shapes}
            selectedId={canvasState.selectedId}
            onSelect={(id) => setCanvasState(prev => ({ ...prev, selectedId: id }))}
          />
        </div>
        <div className="sidebar">
          <VoicePanel
            onSendText={handleSendText}
            onSendAudio={handleSendAudio}
            isProcessing={isProcessing}
            asrResult={asrResult}
            connected={connected}
            optimizeResults={optimizeResults}
          />
          <StatusPanel
            shapes={canvasState.shapes}
            selectedId={canvasState.selectedId}
            history={history}
          />
        </div>
      </main>
    </div>
  );
}

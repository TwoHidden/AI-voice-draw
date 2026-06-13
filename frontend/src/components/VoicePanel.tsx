import React, { useState } from 'react';
import { useVoice } from '../hooks/useVoice';
import type { OptimizeResult } from '../types';

interface VoicePanelProps {
  onSendText: (text: string) => void;
  onSendAudio: (blob: Blob) => void;
  isProcessing: boolean;
  asrResult?: string;
  connected?: boolean;
  optimizeResults?: OptimizeResult[];
}

export default function VoicePanel({ onSendText, onSendAudio, isProcessing, asrResult, connected, optimizeResults = [] }: VoicePanelProps) {
  const [textInput, setTextInput] = useState('');
  const [showOptimize, setShowOptimize] = useState(true);
  const { isRecording, startRecording, stopRecording } = useVoice({ onAudioData: onSendAudio });

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (textInput.trim()) {
      onSendText(textInput.trim());
      setTextInput('');
    }
  };

  return (
    <div className="voice-panel">
      {/* ASR 结果显示 */}
      {asrResult && (
        <div className="asr-result">
          <span className="label">语音识别：</span>
          <span>{asrResult}</span>
        </div>
      )}

      {/* 语音按钮 */}
      <div className="voice-controls">
        <button
          className={`voice-btn ${isRecording ? 'recording' : ''}`}
          onClick={() => isRecording ? stopRecording() : startRecording()}
          disabled={isProcessing}
        >
          {isRecording ? '🔴 点击停止' : '🎤 点击说话'}
        </button>
        {isProcessing && <span className="processing">处理中...</span>}
      </div>

      {/* 文本输入 */}
      <form onSubmit={handleTextSubmit} className="text-input-form">
        <input
          type="text"
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          placeholder="或输入文字指令..."
          disabled={isProcessing}
        />
        <button type="submit" disabled={isProcessing || !textInput.trim()}>
          发送
        </button>
      </form>

      {/* 优化过程面板 */}
      {optimizeResults.length > 0 && (
        <div className="optimize-panel">
          <div className="optimize-header" onClick={() => setShowOptimize(!showOptimize)}>
            📝 优化过程 {showOptimize ? '▼' : '▶'}
          </div>
          {showOptimize && (
            <div className="optimize-content">
              {optimizeResults.map((r, i) => (
                <div key={i} className="optimize-item">
                  <div className="optimize-row">
                    <span className="optimize-label">🎙️ 原始语音:</span>
                    <span className="optimize-value">"{r.original}"</span>
                  </div>
                  <div className="optimize-row">
                    <span className="optimize-label">⚡ 规则预处理:</span>
                    <span className="optimize-value">"{r.rule_processed}"</span>
                  </div>
                  {r.used_llm && (
                    <div className="optimize-row">
                      <span className="optimize-label">🤖 AI 优化:</span>
                      <span className="optimize-value">"{r.final}"</span>
                    </div>
                  )}
                  <div className="optimize-meta">
                    <span className={`confidence ${r.confidence >= 0.7 ? 'high' : 'low'}`}>
                      置信度: {Math.round(r.confidence * 100)}%
                    </span>
                    <span className={`method ${r.used_llm ? 'llm' : 'rule'}`}>
                      {r.used_llm ? 'AI 优化' : '规则引擎'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

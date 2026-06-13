import React, { useState } from 'react';
import { useVoice } from '../hooks/useVoice';

interface VoicePanelProps {
  onSendText: (text: string) => void;
  onSendAudio: (blob: Blob) => void;
  isProcessing: boolean;
  asrResult?: string;
}

export default function VoicePanel({ onSendText, onSendAudio, isProcessing, asrResult }: VoicePanelProps) {
  const [textInput, setTextInput] = useState('');
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
          onMouseDown={startRecording}
          onMouseUp={stopRecording}
          onMouseLeave={stopRecording}
          onTouchStart={startRecording}
          onTouchEnd={stopRecording}
          onTouchCancel={stopRecording}
          disabled={isProcessing}
        >
          {isRecording ? '🔴 录音中...' : '🎤 按住说话'}
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
    </div>
  );
}

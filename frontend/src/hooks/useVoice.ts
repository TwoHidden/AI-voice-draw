import { useState, useRef, useCallback } from 'react';

interface UseVoiceOptions {
  onAudioData?: (data: Blob) => void;
}

function getSupportedMimeType(): string | undefined {
  const types = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg;codecs=opus'];
  return types.find(t => MediaRecorder.isTypeSupported(t));
}

export function useVoice({ onAudioData }: UseVoiceOptions = {}) {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startTimeRef = useRef(0);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mimeType = getSupportedMimeType();
      if (!mimeType) {
        console.error('浏览器不支持任何音频录制格式');
        stream.getTracks().forEach(t => t.stop());
        return;
      }

      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const duration = Date.now() - startTimeRef.current;
        const blob = new Blob(chunksRef.current, { type: mimeType });

        // 最短录音保护：少于 500ms 的录音不发送
        if (duration < 500 || blob.size < 100) {
          console.warn('录音太短，已忽略');
        } else {
          onAudioData?.(blob);
        }
        stream.getTracks().forEach(t => t.stop());
        streamRef.current = null;
      };

      mediaRecorder.start();
      startTimeRef.current = Date.now();
      setIsRecording(true);
    } catch (err) {
      console.error('麦克风访问失败:', err);
      setIsRecording(false);
      streamRef.current?.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
  }, [onAudioData]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  }, []);

  return { isRecording, startRecording, stopRecording };
}

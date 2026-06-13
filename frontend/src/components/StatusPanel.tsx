import React from 'react';
import type { Shape } from '../types';

interface StatusPanelProps {
  shapes: Shape[];
  selectedId: string | null;
  history: string[];
}

export default function StatusPanel({ shapes, selectedId, history }: StatusPanelProps) {
  const selectedShape = shapes.find(s => s.id === selectedId);

  return (
    <div className="status-panel">
      {/* 图形统计 */}
      <div className="stats">
        <h3>画布状态</h3>
        <p>图形数量：{shapes.length}</p>
        {selectedShape && (
          <div className="selected-info">
            <p>选中：{selectedShape.type}</p>
            <p>位置：({Math.round(selectedShape.x)}, {Math.round(selectedShape.y)})</p>
            <p>大小：{Math.round(selectedShape.width)} × {Math.round(selectedShape.height)}</p>
            <p>颜色：<span style={{ color: selectedShape.fill }}>{selectedShape.fill}</span></p>
            {selectedShape.text && <p>文本：{selectedShape.text}</p>}
          </div>
        )}
      </div>

      {/* 操作历史 */}
      <div className="history">
        <h3>操作历史</h3>
        {history.length === 0 ? (
          <p className="empty">暂无操作</p>
        ) : (
          <ul>
            {history.slice(-10).reverse().map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

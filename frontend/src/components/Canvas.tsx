import React from 'react';
import type { Shape, ShapeType } from '../types';

interface CanvasProps {
  shapes: Shape[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
}

/** 根据类型渲染 SVG 图形 */
function renderShape(shape: Shape, isSelected: boolean, onSelect: () => void) {
  const strokeColor = isSelected ? '#FFD700' : shape.stroke;
  const strokeWidth = isSelected ? 3 : 2;

  const commonProps = {
    key: shape.id,
    onClick: (e: React.MouseEvent) => { e.stopPropagation(); onSelect(); },
    style: { cursor: 'pointer' },
  };

  switch (shape.type) {
    case 'rect':
      return (
        <g {...commonProps}>
          <rect
            x={shape.x} y={shape.y}
            width={shape.width} height={shape.height}
            fill={shape.fill} stroke={strokeColor} strokeWidth={strokeWidth}
            rx={4}
            transform={shape.rotation ? `rotate(${shape.rotation} ${shape.x + shape.width/2} ${shape.y + shape.height/2})` : undefined}
          />
          {shape.text && (
            <text
              x={shape.x + shape.width/2} y={shape.y + shape.height/2}
              textAnchor="middle" dominantBaseline="central"
              fontSize={14} fill="#333"
            >{shape.text}</text>
          )}
        </g>
      );

    case 'circle':
      const r = Math.min(shape.width, shape.height) / 2;
      return (
        <g {...commonProps}>
          <circle
            cx={shape.x + shape.width/2} cy={shape.y + shape.height/2} r={r}
            fill={shape.fill} stroke={strokeColor} strokeWidth={strokeWidth}
          />
          {shape.text && (
            <text
              x={shape.x + shape.width/2} y={shape.y + shape.height/2}
              textAnchor="middle" dominantBaseline="central"
              fontSize={14} fill="#333"
            >{shape.text}</text>
          )}
        </g>
      );

    case 'ellipse':
      return (
        <g {...commonProps}>
          <ellipse
            cx={shape.x + shape.width/2} cy={shape.y + shape.height/2}
            rx={shape.width/2} ry={shape.height/2}
            fill={shape.fill} stroke={strokeColor} strokeWidth={strokeWidth}
          />
          {shape.text && (
            <text
              x={shape.x + shape.width/2} y={shape.y + shape.height/2}
              textAnchor="middle" dominantBaseline="central"
              fontSize={14} fill="#333"
            >{shape.text}</text>
          )}
        </g>
      );

    case 'triangle':
      const cx = shape.x + shape.width / 2;
      const points = `${cx},${shape.y} ${shape.x},${shape.y + shape.height} ${shape.x + shape.width},${shape.y + shape.height}`;
      return (
        <g {...commonProps}>
          <polygon
            points={points}
            fill={shape.fill} stroke={strokeColor} strokeWidth={strokeWidth}
          />
          {shape.text && (
            <text
              x={cx} y={shape.y + shape.height * 0.6}
              textAnchor="middle" dominantBaseline="central"
              fontSize={14} fill="#333"
            >{shape.text}</text>
          )}
        </g>
      );

    case 'diamond':
      const dcx = shape.x + shape.width / 2;
      const dcy = shape.y + shape.height / 2;
      const dpoints = `${dcx},${shape.y} ${shape.x + shape.width},${dcy} ${dcx},${shape.y + shape.height} ${shape.x},${dcy}`;
      return (
        <g {...commonProps}>
          <polygon
            points={dpoints}
            fill={shape.fill} stroke={strokeColor} strokeWidth={strokeWidth}
          />
          {shape.text && (
            <text
              x={dcx} y={dcy}
              textAnchor="middle" dominantBaseline="central"
              fontSize={14} fill="#333"
            >{shape.text}</text>
          )}
        </g>
      );

    case 'line':
      return (
        <g {...commonProps}>
          <line
            x1={shape.x} y1={shape.y}
            x2={shape.x + shape.width} y2={shape.y + shape.height}
            stroke={shape.stroke} strokeWidth={strokeWidth}
          />
        </g>
      );

    case 'arrow':
      const arrowId = `arrow-${shape.id}`;
      return (
        <g {...commonProps}>
          <defs>
            <marker id={arrowId} markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill={shape.stroke} />
            </marker>
          </defs>
          <line
            x1={shape.x} y1={shape.y}
            x2={shape.x + shape.width} y2={shape.y + shape.height}
            stroke={shape.stroke} strokeWidth={strokeWidth}
            markerEnd={`url(#${arrowId})`}
          />
        </g>
      );

    default:
      return null;
  }
}

export default function Canvas({ shapes, selectedId, onSelect }: CanvasProps) {
  return (
    <svg
      width="100%" height="100%"
      viewBox="0 0 800 600"
      style={{ background: '#fff', border: '1px solid #ddd', borderRadius: 8 }}
      onClick={() => onSelect(null)}
    >
      {shapes.map(shape =>
        renderShape(shape, shape.id === selectedId, () => onSelect(shape.id))
      )}
    </svg>
  );
}

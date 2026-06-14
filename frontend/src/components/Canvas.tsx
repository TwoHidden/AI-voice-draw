import React from 'react';
import type { Shape } from '../types';

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

    case 'star': {
      const scx = shape.x + shape.width / 2;
      const scy = shape.y + shape.height / 2;
      const outerR = Math.min(shape.width, shape.height) / 2;
      const innerR = outerR * 0.4;
      const starPoints: string[] = [];
      for (let i = 0; i < 5; i++) {
        // 外顶点
        const outerAngle = (i * 72 - 90) * Math.PI / 180;
        starPoints.push(`${scx + outerR * Math.cos(outerAngle)},${scy + outerR * Math.sin(outerAngle)}`);
        // 内顶点
        const innerAngle = ((i * 72 + 36) - 90) * Math.PI / 180;
        starPoints.push(`${scx + innerR * Math.cos(innerAngle)},${scy + innerR * Math.sin(innerAngle)}`);
      }
      return (
        <g {...commonProps}>
          <polygon
            points={starPoints.join(' ')}
            fill={shape.fill} stroke={strokeColor} strokeWidth={strokeWidth}
          />
          {shape.text && (
            <text
              x={scx} y={scy}
              textAnchor="middle" dominantBaseline="central"
              fontSize={14} fill="#333"
            >{shape.text}</text>
          )}
        </g>
      );
    }

    case 'curve': {
      const startX = shape.x;
      const startY = shape.y + shape.height;
      const endX = shape.x + shape.width;
      const endY = shape.y + shape.height;
      const controlX = shape.x + shape.width / 2;
      const controlY = shape.y;
      return (
        <g {...commonProps}>
          <path
            d={`M ${startX} ${startY} Q ${controlX} ${controlY} ${endX} ${endY}`}
            fill="none" stroke={shape.stroke} strokeWidth={strokeWidth}
          />
        </g>
      );
    }

    case 'hexagon': {
      const hcx = shape.x + shape.width / 2;
      const hcy = shape.y + shape.height / 2;
      const hr = Math.min(shape.width, shape.height) / 2;
      const hexPoints: string[] = [];
      for (let i = 0; i < 6; i++) {
        const angle = (i * 60 - 90) * Math.PI / 180;
        hexPoints.push(`${hcx + hr * Math.cos(angle)},${hcy + hr * Math.sin(angle)}`);
      }
      return (
        <g {...commonProps}>
          <polygon
            points={hexPoints.join(' ')}
            fill={shape.fill} stroke={strokeColor} strokeWidth={strokeWidth}
          />
          {shape.text && (
            <text
              x={hcx} y={hcy}
              textAnchor="middle" dominantBaseline="central"
              fontSize={14} fill="#333"
            >{shape.text}</text>
          )}
        </g>
      );
    }

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

/** 图形类型 */
export type ShapeType = 'rect' | 'circle' | 'ellipse' | 'triangle' | 'diamond' | 'line' | 'arrow' | 'star' | 'curve' | 'hexagon';

/** 操作类型 */
export type OperationType = 'create' | 'delete' | 'move' | 'resize' | 'setColor' | 'setText' | 'undo' | 'redo';

/** 颜色类型 */
export type ColorType = 'red' | 'blue' | 'green' | 'yellow' | 'black' | 'white' | 'purple' | 'orange';

/** 图形属性 */
export interface Shape {
  id: string;
  type: ShapeType;
  x: number;
  y: number;
  width: number;
  height: number;
  fill: string;
  stroke: string;
  text: string;
  rotation: number;
}

/** 画布状态 */
export interface CanvasState {
  shapes: Shape[];
  selectedId: string | null;
}

/** 服务端响应的图形（snake_case） */
export interface ShapeResponse {
  id: string;
  type: ShapeType;
  x: number;
  y: number;
  width: number;
  height: number;
  fill: string;
  stroke: string;
  text: string;
  rotation: number;
}

/** 服务端响应的画布状态 */
export interface CanvasStateResponse {
  shapes: ShapeResponse[];
  selected_id: string | null;
}

/** 指令解析结果 */
export interface ParsedCommand {
  operation: OperationType;
  shape_type?: ShapeType;
  target_id?: string;
  properties: Record<string, unknown>;
}

/** WebSocket 消息类型 */
export interface WSMessage {
  type: 'text' | 'audio' | 'state_update' | 'error' | 'asr_result' | 'pong' | 'agent_response';
  data: string | CanvasStateResponse;
}

# LLM Agent Function Calling 实施计划

## 任务清单

- [ ] **任务 1**: 创建 `backend/app/tools.py`
  - 定义 TOOLS_SCHEMA（OpenAI function calling 格式）
  - 定义颜色映射表
  - 实现 `execute_tool_calls()` 函数

- [ ] **任务 2**: 创建 `backend/app/agent.py`
  - 实现 `Agent` 类
  - 实现 `process()` 方法：调用 LLM with tools
  - 处理 tool_calls 返回结果
  - 构建 system prompt（含画布状态）

- [ ] **任务 3**: 修改 `backend/app/main.py`
  - 移除 optimizer 和 parser 的导入
  - 添加 agent 的导入
  - 修改 `_process_and_execute()` 调用 agent
  - 处理多 tool_calls 的情况

- [ ] **任务 4**: 修改 `backend/app/executor.py`
  - 添加 `get_state_summary()` 方法返回画布状态摘要
  - 添加工具调用接口（供 agent 调用）

- [ ] **任务 5**: 清理废弃文件
  - 删除 `backend/app/optimizer.py`
  - 删除 `backend/app/parser.py`
  - 更新相关测试

- [ ] **任务 6**: 修改前端适配
  - 移除 optimizeResults 相关代码
  - 添加 agentResponse 显示（可选）
  - 更新 useWebSocket hook

- [ ] **任务 7**: 测试验证
  - 测试基本创建指令
  - 测试复杂组合指令
  - 测试口语化表达
  - 测试指代消解

- [ ] **任务 8**: 提交代码并推送
  - git add 所有修改
  - git commit
  - git push origin main

## 依赖关系

```
任务1 → 任务2 → 任务3 → 任务4 → 任务5 → 任务6 → 任务7 → 任务8
```

## 预计时间

- 任务 1-2: 30 分钟
- 任务 3-4: 20 分钟
- 任务 5-6: 15 分钟
- 任务 7-8: 15 分钟
- 总计: ~80 分钟

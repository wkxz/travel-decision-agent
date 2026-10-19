const zh = {
  // Header
  "app.title": "出行决策助手",
  "app.subtitle": "帮你找到附近同时有指定品牌的商场，并算清距离",

  // Empty state
  "empty.title": "出行决策助手",
  "empty.hint": "告诉我你在哪里、想找哪几个品牌，我会搜索附近商场、逐个核对品牌门店，并给出最近的选择。数据来自高德地图实时检索。",
  "empty.features": "高德地图检索 · 会话记忆 · Agent Tools",

  // Chat input
  "chat.placeholder": "发消息…  ⏎ 发送 · Shift+⏎ 换行",
  "chat.hint": "由 OpenAI Agents SDK + EdgeOne Makers + 高德地图驱动",

  // Preset questions
  "preset.1": "我在北京朝阳合生汇附近，想找一个同时有倍轻松和西町村屋的商场。",
  "preset.2": "我在上海静安寺附近，想找一个同时有星巴克和优衣库的商场，走路能到吗？",

  // Tool indicators
  "tool.geocode": "位置解析",
  "tool.malls": "商场搜索",
  "tool.brand": "品牌核对",
  "tool.distance": "距离测算",

  // Status & errors
  "status.error": "⚠️ 请求失败，请检查后端服务是否启动。",
  "status.stopped": "⏹ *已停止生成*",
  "status.backendError": "⚠️ 后端中断请求失败，服务端可能仍在运行。",

  // Debug panel
  "debug.title": "传输流",
  "debug.events": "事件",
  "debug.clear": "清除",
  "debug.empty": "等待 SSE 事件...",
  "debug.emptyHint": "发送消息后，所有原始后端数据将在此处显示。",

  // Conversation sidebar
  "sidebar.label": "会话列表",
  "sidebar.title": "会话",
  "sidebar.newChat": "新建聊天",
  "sidebar.loading": "正在加载会话...",
  "sidebar.loadMore": "加载更多",
  "sidebar.loadingMore": "加载中...",
  "sidebar.emptyTitle": "暂无会话",
  "sidebar.emptyHint": "点击「新建聊天」开始第一段对话。",
  "sidebar.delete": "删除会话",
  "sidebar.deleteConfirm": "确定要永久删除这个会话吗？此操作不可恢复。",

  // Aria labels (button hover/screen-reader)
  "aria.send": "发送",
  "aria.clearHistory": "清除历史",
  "aria.stopGeneration": "停止生成",

  // Language toggle
  "lang.switch": "English",

  // ─── Floating bottom-right action badges ─────────────────────────────
  "floatingLink.deploy": "一键部署",
  "floatingLink.github": "GitHub",
} as const;

export default zh;

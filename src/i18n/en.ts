const en = {
  // Header
  "app.title": "Travel Decision Assistant",
  "app.subtitle": "Find nearby malls that carry all the brands you want, with real distances",

  // Empty state
  "empty.title": "Travel Decision Assistant",
  "empty.hint": "Tell me where you are and which brands you need. I'll search nearby malls, verify each brand store one by one, and recommend the closest match. Data comes from live AMap queries.",
  "empty.features": "AMap Search · Session Memory · Agent Tools",

  // Chat input
  "chat.placeholder": "Type a message...  ⏎ Send · Shift+⏎ Newline",
  "chat.hint": "Powered by OpenAI Agents SDK + EdgeOne Makers + AMap",

  // Preset questions
  "preset.1": "I'm near Hopson One in Chaoyang, Beijing. Find a mall that has both Breo and Xiding Village House.",
  "preset.2": "I'm near Jing'an Temple in Shanghai. Find a mall with both Starbucks and Uniqlo, and is it walkable?",

  // Tool indicators
  "tool.geocode": "Geocode",
  "tool.malls": "Mall search",
  "tool.brand": "Brand check",
  "tool.distance": "Distance",

  // Status & errors
  "status.error": "Request failed. Please check if the backend service is running.",
  "status.stopped": "⏹ *Generation stopped*",
  "status.backendError": "Backend abort request failed. The server may still be running.",

  // Debug panel
  "debug.title": "Trace",
  "debug.events": "events",
  "debug.clear": "Clear",
  "debug.empty": "Waiting for SSE events...",
  "debug.emptyHint": "After sending a message, all raw backend data will be displayed here.",

  // Conversation sidebar
  "sidebar.label": "Conversation list",
  "sidebar.title": "Chats",
  "sidebar.newChat": "New chat",
  "sidebar.loading": "Loading conversations...",
  "sidebar.loadMore": "Load more",
  "sidebar.loadingMore": "Loading...",
  "sidebar.emptyTitle": "No conversations yet",
  "sidebar.emptyHint": "Click \"New chat\" to start your first conversation.",
  "sidebar.delete": "Delete conversation",
  "sidebar.deleteConfirm": "Permanently delete this conversation? This cannot be undone.",

  // Aria labels (button hover/screen-reader)
  "aria.send": "Send",
  "aria.clearHistory": "Clear history",
  "aria.stopGeneration": "Stop generation",

  // Language toggle
  "lang.switch": "中文",

  // ─── Floating bottom-right action badges ─────────────────────────────
  "floatingLink.deploy": "Deploy",
  "floatingLink.github": "GitHub",
} as const;

export default en;

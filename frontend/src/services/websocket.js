/**
 * ==========================================================
 * MetricGuard — WebSocket Service  (websocket.js)
 * ==========================================================
 *
 * Phase 15: Unified AIOps Dashboard
 *
 * Native WebSocket client for real-time alert streaming.
 * Connects to ws://localhost:8000/ws/alerts with auto-reconnect.
 */

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/alerts';

const RECONNECT_INTERVAL = 3000;  // ms
const MAX_RECONNECT_ATTEMPTS = 20;

/**
 * Create a managed WebSocket connection with auto-reconnect.
 *
 * @param {function} onMessage  - Callback invoked with parsed alert JSON
 * @param {function} onStatus   - Callback invoked with connection status string
 * @returns {{ close: function }} - Object with a close method to tear down
 */
export function createAlertWebSocket(onMessage, onStatus) {
  let ws = null;
  let reconnectAttempts = 0;
  let closed = false;

  function connect() {
    if (closed) return;

    onStatus?.('connecting');
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      reconnectAttempts = 0;
      onStatus?.('connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage?.(data);
      } catch {
        // If not JSON, pass raw text
        onMessage?.({ raw: event.data });
      }
    };

    ws.onclose = () => {
      onStatus?.('disconnected');
      if (!closed && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        setTimeout(connect, RECONNECT_INTERVAL);
      }
    };

    ws.onerror = () => {
      onStatus?.('error');
      if (ws) {
        try {
          ws.close();
        } catch {
          /* ignore error during closing */
        }
      }
    };
  }

  connect();

  return {
    close() {
      closed = true;
      if (ws) {
        ws.close();
        ws = null;
      }
    },
  };
}

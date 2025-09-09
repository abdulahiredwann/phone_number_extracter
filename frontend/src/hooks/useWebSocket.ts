import { useEffect, useRef, useState } from "react";

interface WebSocketMessage {
  type: string;
  task_id: string;
  status?: string;
  progress?: number;
  current_frame?: number;
  total_frames?: number;
  message?: string;
  error_message?: string;
  phone_numbers_count?: number;
}

export const useWebSocket = (taskId: string | null) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!taskId) return;

    const wsUrl = `ws://localhost:8000/ws/task/${taskId}/`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log("🔌 WebSocket connected");
      setIsConnected(true);
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        console.log("📨 WebSocket message:", data);
        setLastMessage(data);
      } catch (err) {
        console.error("❌ Error parsing WebSocket message:", err);
      }
    };

    ws.onclose = () => {
      console.log("🔌 WebSocket disconnected");
      setIsConnected(false);
    };

    ws.onerror = (error) => {
      console.error("❌ WebSocket error:", error);
      setError("WebSocket connection failed");
      setIsConnected(false);
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, [taskId]);

  const sendMessage = (message: any) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    }
  };

  return {
    socket,
    isConnected,
    lastMessage,
    error,
    sendMessage,
  };
};

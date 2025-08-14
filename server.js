import { WebSocketServer } from "ws";
import http from "http";
import { URL } from "url";

const server = http.createServer((req, res) => {
  res.writeHead(200);
  res.end("WebSocket server running __");
});

const wss = new WebSocketServer({ noServer: true });

// Store clients by path and ID
const clients = {
  echo: new Map(),
  reverse: new Map(),
};

wss.on("connection", (ws, request) => {
  const url = new URL(request.url, `http://${request.headers.host}`);
  const path = url.pathname.slice(1);
  const clientId = url.searchParams.get("id");

  if (!clientId) {
    ws.close(1008, "Missing client ID");
    return;
  }
  if (!clients[path]) {
    ws.close(1008, "Invalid path");
    return;
  }

  clients[path].set(clientId, ws);
  console.log(`Client ${clientId} connected on /${path}`);

  ws.on("message", (msg) => {
    msg = msg.toString();

    // Format: "targetId:message"
    const [targetId, message] = msg.includes(":")
      ? msg.split(/:(.*)/) // split at first colon
      : [null, msg];

    if (targetId && clients[path].has(targetId)) {
      clients[path].get(targetId).send(message);
    } else {
      // Broadcast to others
      for (const [id, client] of clients[path]) {
        if (client !== ws) client.send(msg);
      }
    }
  });

  ws.on("close", () => {
    clients[path].delete(clientId);
    console.log(`Client ${clientId} disconnected from /${path}`);
  });
});

server.on("upgrade", (request, socket, head) => {
  wss.handleUpgrade(request, socket, head, (ws) => {
    wss.emit("connection", ws, request);
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));

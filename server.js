import { WebSocketServer } from "ws";
import http from "http";

const server = http.createServer((req, res) => {
  res.writeHead(200);
  res.end("WebSocket server running");
});

const wss = new WebSocketServer({ noServer: true });

const echoClients = new Set();
const reverseClients = new Set();

wss.on("connection", (ws, request) => {
  const path = request.url;
  const clientsSet = path === "/echo" ? echoClients : reverseClients;
  const otherSet = path === "/echo" ? reverseClients : echoClients;

  clientsSet.add(ws);

  ws.on("message", (msg) => {
    for (const c of clientsSet) if (c !== ws) c.send(msg);
    for (const c of otherSet) c.send(msg);
  });

  ws.on("close", () => clientsSet.delete(ws));
});

server.on("upgrade", (request, socket, head) => {
  wss.handleUpgrade(request, socket, head, (ws) => {
    wss.emit("connection", ws, request);
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));
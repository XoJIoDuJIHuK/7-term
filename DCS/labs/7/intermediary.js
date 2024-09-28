const dgram = require('dgram');
const fs = require('fs');
const { ServerInfo, getSendAppendix, parseMessage } = require('./config');

const intermediaryIP = '127.0.0.1';
const intermediaryPort = 5555;
const coordinatorFile = 'coordinator.txt';
const logFile = 'intermediary.log';
const server = dgram.createSocket('udp4');
const mockClients = [
  new ServerInfo('127.0.0.1', '6000'),
  new ServerInfo('127.0.0.1', '6001'),
  new ServerInfo('127.0.0.1', '6002'),
  new ServerInfo('127.0.0.1', '6003'),
  new ServerInfo('127.0.0.1', '6004'),
]

function getCoordinator() {
  return new ServerInfo(...fs.readFileSync(coordinatorFile, 'utf8').split(' '));
}

function passMessage(sender, msg) {
  const coordinatorInfo = getCoordinator();
  server.send(
    getSendAppendix(new ServerInfo(intermediaryIP, intermediaryPort)) + msg,
    coordinatorInfo.port,
    coordinatorInfo.host
  );
  log(`Request from ${sender} forwarded to coordinator ${coordinatorInfo}`);
}

server.on('message', (msg, rinfo) => {
  msg = msg.toString();
  const [sender, message] = parseMessage(msg);
  if (sender.Equals(getCoordinator())) {
    log(`Got message back from coordinator: ${message}`);
  } else {
    passMessage(new ServerInfo(rinfo.address, rinfo.port), msg);
  }
});

server.bind(intermediaryPort, intermediaryIP, () => {
  log(`Intermediary Server running at ${intermediaryIP}:${intermediaryPort}`);
});

setInterval(() => {
  sender = mockClients[Math.floor(Math.random() * mockClients.length)];
  log(`Mocking client ${sender} request to ${getCoordinator()}`);
  passMessage(sender, 'TIME_REQUEST');
}, 2000);

function log(message) {
  console.log(message);
  fs.appendFileSync(logFile, message + '\n');
}
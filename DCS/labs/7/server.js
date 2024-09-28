const dgram = require('dgram');
const fs = require('fs');
const { serverIPs, ServerInfo, getSendAppendix, parseMessage } = require('./config');
const serverIndex = parseInt(process.argv[2]);
const serverInfo = serverIPs[serverIndex];
const coordinatorFile = 'coordinator.txt';

let coordinatorRequestFailCount = 0;
let coordinatorIsAlive = true;
let electionLargerServerResponsed = false;
let becomeCoordinatorTimeout = undefined;
let currentCoordinator = undefined;

function getServerIndex(host, port) {
    const serverInQuestion = new ServerInfo(host, port);
    for (let i = 0; i < serverIPs.length; i++) {
        if (serverInQuestion.Equals(serverIPs[i])) {
            return i;
        }
    }
    throw new Error(`No server found: ${serverInQuestion}`);
}

const server = dgram.createSocket('udp4');

server.on('message', (msg, rinfo) => {
  const [sender, message] = parseMessage(msg);
  console.log(`Got message ${message} from ${sender.host}:${sender.port}`);

  if (message === 'TIME_REQUEST') {
    const currentTime = new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '');
    const formattedTime = `${currentTime.split(' ')[0].replace(/-/g, '')}:${currentTime.split(' ')[1]}`;
    server.send(getSendAppendix(serverInfo) + formattedTime, sender.port, sender.host);
  } else if (message === 'COORDINATOR_CHECK') {
    server.send(getSendAppendix(serverInfo) + 'I_AM_ALIVE', sender.port, sender.host);
  } else if (message === 'I_AM_ALIVE') {
    coordinatorRequestFailCount = 0;
    coordinatorIsAlive = true;
    if (getServerIndex(sender.host, sender.port) < serverIndex) {
      becomeCoordinator();
    }
  } else if (message === 'ELECTION') {
    if (getServerIndex(sender.host, sender.port) > serverIndex) {
        clearTimeout(becomeCoordinatorTimeout);
    } else {
        server.send(getSendAppendix(serverInfo) + 'OK', sender.port, sender.host);
        initiateElection();
    }
  } else if (message === 'OK') {
    electionLargerServerResponsed = true;
  } else if (message === 'I_AM_COORDINATOR') {
    currentCoordinator = serverIPs[getServerIndex(sender.host, sender.port)];
    coordinatorRequestFailCount = 0;
  } else if (message === 'INIT') {
    const senderIndex = getServerIndex(sender.host, sender.port);
    if (!currentCoordinator || senderIndex > getServerIndex(
      currentCoordinator.host, currentCoordinator.port
    )) {
      currentCoordinator = serverIPs[senderIndex];
    }
  }
});

server.bind(serverInfo.port, serverInfo.host, () => {
  console.log(`UDP Time Server running at ${serverInfo.host}:${serverInfo.port}`);
  runInitSequence();
  setTimeout(checkCoordinator, 5000);
});

function runInitSequence() {
  const initInterval = setInterval(() => {
    for (let s of serverIPs) {
      server.send(getSendAppendix(serverInfo) + 'INIT', s.port, s.host);
    }
  }, 500);
  setTimeout(() => { clearInterval(initInterval); }, 4000);
}

function becomeCoordinator() {
  currentCoordinator = serverIPs[serverIndex];
    fs.writeFileSync(coordinatorFile, `${serverInfo.host} ${serverInfo.port}`);// для удобства представим, что адрес текущего координатора заносится в файл вручную
    for (let s of serverIPs) {
        if (!s.Equals(serverInfo)) {
            server.send(getSendAppendix(serverInfo) + 'I_AM_COORDINATOR', s.port, s.host);
        }
    }
    console.log(`I am the new coordinator: ${serverInfo}`);
}

function checkCoordinator() {
  setInterval(() => {
    // const coordinatorInfo = new ServerInfo(...fs.readFileSync(coordinatorFile, 'utf8').split(' '));
    const coordinatorInfo = currentCoordinator;
    console.log(`Got coordinator info ${coordinatorInfo}`);
    if (!coordinatorInfo.Equals(serverInfo)) {
      const client = dgram.createSocket('udp4');
      console.log(`Sending request to coordinator`);
      coordinatorIsAlive = false;
      client.send(getSendAppendix(serverInfo) + 'COORDINATOR_CHECK', coordinatorInfo.port, coordinatorInfo.host, (err) => {
        setTimeout(() => {
          if (coordinatorRequestFailCount >= 2) {
            console.log('Coordinator did not response for 3 times');
            initiateElection();
            return;
          } else if (!coordinatorIsAlive) {
            coordinatorRequestFailCount++;
          }
        }, 1000)
        client.close();
      });
    }
  }, 5000);
}

function initiateElection() {
  console.log(`Initiating election`);
  const largerServers = serverIPs.slice(serverIndex + 1);

  largerServers.forEach((el) => {
    console.log(`Sending ELECTION to ${el}`);
    server.send(getSendAppendix(serverInfo) + 'ELECTION', el.port, el.host);
  });

  becomeCoordinatorTimeout = setTimeout(() => {
    if (!electionLargerServerResponsed) {
      becomeCoordinator();
    }
    electionLargerServerResponsed = false;
  }, 3000);
}
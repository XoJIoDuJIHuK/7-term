class ServerInfo {
    constructor(host, port) {
        this.host = host;
        this.port = port;
    }

    Equals = another => this.host == another.host && this.port == another.port;
    toString = () => `${this.host}:${this.port}`;
}

module.exports.serverIPs = [
    new ServerInfo('127.0.0.1', '5000'),
    new ServerInfo('127.0.0.1', '5001'),
    new ServerInfo('127.0.0.1', '5002'),
    new ServerInfo('127.0.0.1', '5003'),
    new ServerInfo('127.0.0.1', '5004'),
    new ServerInfo('127.0.0.1', '5005'),
    new ServerInfo('127.0.0.1', '5006'),
];

module.exports.ServerInfo = ServerInfo;
module.exports.getSendAppendix =  (serverInfo) => `${serverInfo.host} ${serverInfo.port}|`;
module.exports.parseMessage = (msg) => {
  const [senderData, message] = msg.toString().split('|');
  const sender = new ServerInfo(...senderData.split(' '));
  return [sender, message];
}
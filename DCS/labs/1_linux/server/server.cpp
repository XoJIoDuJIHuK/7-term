#include <iostream>
#include <cstring>
#include <cstdlib>
#include <ctime>
#include <vector>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <climits>

using namespace std;

struct client_request {
    char cmd[5];
    int curvalue;
};

struct server_response {
    char cmd[5];
    int correction;
};

int main() {
    int serverSocket;
    struct sockaddr_in serverAddr, clientAddr;
    socklen_t clientAddrSize = sizeof(clientAddr);
    char recvBuf[1024];
    int recvLen;
    int max_correction = LONG_LONG_MIN;
    int min_correction = LONG_LONG_MAX;

    vector<int> corrections;

    serverSocket = socket(AF_INET, SOCK_DGRAM, 0);
    if (serverSocket < 0) {
        cerr << "Socket creation failed." << endl;
        return 1;
    }

    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(8888);

    if (bind(serverSocket, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        cerr << "Bind failed." << endl;
        close(serverSocket);
        return 1;
    }

    cout << "Server is running..." << endl;

    int requestCount = 0;

    while (true) {
        client_request req;
        server_response res;
        
        int bytes_received = recvfrom(
            serverSocket,
            reinterpret_cast<char*>(&req),
            sizeof(req),
            0,
            reinterpret_cast<struct sockaddr*>(&clientAddr),
            &clientAddrSize
        );

        if (bytes_received < 0) {
            cerr << "recvfrom failed." << endl;
            close(serverSocket);
            return 1;
        }

        if (strncmp(req.cmd, "SYNC", 4) != 0) {
            cerr << "Invalid command received: " << req.cmd << endl;
            close(serverSocket);
            return 2;
        }

        time_t server_time = clock();
        std::cout << "Server time: " << server_time << std::endl;
        int correction = server_time - req.curvalue;
        res.correction = correction;
        strncpy(res.cmd, "SYNC", 4);

        int bytes_sent = sendto(serverSocket, reinterpret_cast<char*>(&res), sizeof(res), 0, reinterpret_cast<struct sockaddr*>(&clientAddr), clientAddrSize);

        if (bytes_sent < 0) {
            cerr << "sendto failed." << endl;
            close(serverSocket);
            return 3;
        }

        requestCount++;
        corrections.push_back(correction);
        double averageCorrection = 0;
        for (int c : corrections) {
            averageCorrection += c;
        }
        averageCorrection /= corrections.size();
        max_correction = max(max_correction, correction);
        min_correction = min(min_correction, correction);

        cout << "Client IP: " << inet_ntoa(clientAddr.sin_addr)
            << ", #: " << requestCount
            << ", corr: " << correction
            << ", avg corr: " << averageCorrection
            << ", max: " << max_correction
            << ", min: " << min_correction
            << endl;
    }

    close(serverSocket);
    return 0;
}

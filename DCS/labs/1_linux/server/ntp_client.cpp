#include <iostream>
#include <cstring>
#include <thread>
#include <chrono>
#include <ctime>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <stdexcept>
#include <climits>

#define SERVER_PORT 2000
#define SYNC_INTERVAL_MS 1000

struct GETSINCHRO {
    uint64_t mTime;
};

struct SETSINCHRO {
    long long corrTime;
};

uint64_t GetLocalUnixTime() {
    return std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();
}

int main() {
    std::string IP;
    std::cout << "Enter server IP: ";
    std::cin >> IP;
    int Tcs[] = {1000, 3000, 6000, 8000, 10000, 12000, 14000};

    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    for (int i = 0; i < 7; i++) {
        int TC = Tcs[i];
        std::cout << "=====Starting measurement " << TC << " ms=====" << std::endl;
        long long maxcorr = 0, mincorr = UINT64_MAX;
        long long mcorr = 0;
        long long mCcOs = 0;

        long long ClientTime = 0;
        int clientSocket;

        try {
            if ((clientSocket = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
                throw std::runtime_error("Failed to create socket: " + std::string(strerror(errno)));
            }

            struct sockaddr_in serverParameters;
            serverParameters.sin_family = AF_INET;
            serverParameters.sin_port = htons(SERVER_PORT);
            if (inet_pton(AF_INET, IP.c_str(), &serverParameters.sin_addr) <= 0) {
                throw std::runtime_error("Invalid address: " + std::string(strerror(errno)));
            }

            GETSINCHRO gs;
            SETSINCHRO ss;
            ss.corrTime = 0;
            gs.mTime = 0;

            if (sendto(clientSocket, (char*)&gs, sizeof(gs), 0, (struct sockaddr*)&serverParameters, sizeof(serverParameters)) < 0) {
                throw std::runtime_error("Failed to send data: " + std::string(strerror(errno)));
            }

            socklen_t server_len = sizeof(serverParameters);
            if (recvfrom(clientSocket, (char*)&ss, sizeof(ss), 0, (struct sockaddr*)&serverParameters, &server_len) < 0) {
                throw std::runtime_error("Failed to receive data: " + std::string(strerror(errno)));
            }

            ClientTime = ss.corrTime;
            std::cout << "Initial correction: " << ss.corrTime << std::endl << std::endl;

            for (int i = 0; i < 10; ++i) {
                std::this_thread::sleep_for(std::chrono::milliseconds(TC));

                ClientTime = gs.mTime = ClientTime + TC;
                gs.mTime = ClientTime;
                if (sendto(clientSocket, (char*)&gs, sizeof(gs), 0, (struct sockaddr*)&serverParameters, sizeof(serverParameters)) < 0) {
                    throw std::runtime_error("Failed to send data: " + std::string(strerror(errno)));
                }

                if (recvfrom(clientSocket, (char*)&ss, sizeof(ss), 0, (struct sockaddr*)&serverParameters, &server_len) < 0) {
                    throw std::runtime_error("Failed to receive data: " + std::string(strerror(errno)));
                }

                long long localUnixTime = GetLocalUnixTime();
                std::cout << "Received correction: " << ss.corrTime << " ms" << std::endl;
                ClientTime = ClientTime + ss.corrTime;
                mcorr += ss.corrTime;
                mCcOs += (ClientTime - localUnixTime);
                maxcorr = std::max(maxcorr, ss.corrTime);
                mincorr = std::min(mincorr, ss.corrTime);

                std::cout << "Cc - OS = " << ClientTime - localUnixTime << std::endl;
                std::cout << std::endl;
            }

            std::cout << "Average correction: " << mcorr / 10.0 << std::endl;
            std::cout << "Average Client - Local time: " << mCcOs / 10.0 << std::endl;
            std::cout << "Max correction: " << maxcorr << std::endl;
            std::cout << "Min correction: " << mincorr << std::endl << std::endl;

            if (close(clientSocket) < 0) {
                throw std::runtime_error("Failed to close socket: " + std::string(strerror(errno)));
            }
        } catch (const std::runtime_error& e) {
            std::cerr << "Error: " << e.what() << std::endl;
        }
    }

    return 0;
}

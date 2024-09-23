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
#include <pthread.h>
#include <stdexcept>

#define NTP_PORT 123
#define SERVER_PORT 2000
#define SYNC_INTERVAL_MS 10000

struct GETSINCHRO {
    uint64_t mTime;
};

struct SETSINCHRO {
    long long corrTime;
};

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
uint64_t lastSync = 0;

uint64_t GetLocalUnixTime() {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

void* SyncGlobalUnixTime(void* lpar) {
    while (true)
    {
        int sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
        if (sockfd < 0) {
            std::cerr << "Error creating socket\n";
            return nullptr;
        }

        struct sockaddr_in serverAddr;
        memset(&serverAddr, 0, sizeof(serverAddr));
        serverAddr.sin_family = AF_INET;
        serverAddr.sin_port = htons(NTP_PORT);
        if (inet_pton(AF_INET, "129.6.15.28", &serverAddr.sin_addr) <= 0) {
            std::cerr << "Invalid NTP server IP\n";
            close(sockfd);
            return nullptr;
        }

        unsigned char packet[48]={ 0x01B, 0, 0, 0, 0, 0, 0, 0, 0 }; // Легкий запрос на NTP (версия 3, клиентский режим)

        if (sendto(sockfd, packet, sizeof(packet), 0, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
            std::cerr << "Error sending packet to NTP server\n";
            close(sockfd);
            return nullptr;
        }

        unsigned long buf[1024];
        socklen_t addrLen = sizeof(serverAddr);
        struct sockaddr saddr;
        socklen_t saddr_l = sizeof (saddr);
        if (recvfrom(sockfd, buf, 48, 0, &saddr, &saddr_l) < 0) {
            std::cerr << "Error receiving packet from NTP server\n";
            close(sockfd);
            return nullptr;
        }

        close(sockfd);

        uint64_t ntpTime = ntohl((time_t)buf[4]);
        ntpTime -= 2208988800U;
        ntpTime *= 1000;

        GETSINCHRO* syncData = (GETSINCHRO*)lpar;
        pthread_mutex_lock(&mutex);
        lastSync = GetLocalUnixTime();
        syncData->mTime = ntpTime;
        pthread_mutex_unlock(&mutex);

        std::cout << "NTP ms: " << ntpTime << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(SYNC_INTERVAL_MS));
    }

    return nullptr;
}

int main() {
    std::cout << "NTP Server running on port " << SERVER_PORT << std::endl;

    pthread_t sync_thread;
    GETSINCHRO sync_data;

    if (pthread_create(&sync_thread, nullptr, SyncGlobalUnixTime, &sync_data) != 0) {
        std::cerr << "Failed to create synchronization thread" << std::endl;
        return 1;
    }

    int server_socket;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_addr_len = sizeof(client_addr);
    SETSINCHRO response_data;

    if ((server_socket = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        std::cerr << "Failed to create server socket: " << strerror(errno) << std::endl;
        return 1;
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    server_addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(server_socket, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        std::cerr << "Failed to bind server socket: " << strerror(errno) << std::endl;
        close(server_socket);
        return 1;
    }

    while (true) {
        GETSINCHRO client_data;
        if (recvfrom(server_socket, &client_data, sizeof(client_data), 0, (struct sockaddr*)&client_addr, &client_addr_len) < 0) {
            std::cerr << "Failed to receive client data: " << strerror(errno) << std::endl;
            continue;
        }

        pthread_mutex_lock(&mutex);
        int32_t delta = GetLocalUnixTime() - lastSync;
        response_data.corrTime = sync_data.mTime + delta - client_data.mTime;
        std::cout << "CORR " << response_data.corrTime << std::endl;
        pthread_mutex_unlock(&mutex);

        if (sendto(server_socket, &response_data, sizeof(response_data), 0, (struct sockaddr*)&client_addr, sizeof(client_addr)) < 0) {
            std::cerr << "Failed to send response data: " << strerror(errno) << std::endl;
        }
    }

    close(server_socket);
    pthread_join(sync_thread, nullptr);
    pthread_mutex_destroy(&mutex);
    return 0;
}

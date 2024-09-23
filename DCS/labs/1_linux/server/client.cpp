#include <iostream>
#include <cstring>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <stdexcept>
#include <thread>
#include <chrono>

struct client_request {
    char cmd[5];
    int curvalue;
};

struct server_response {
    char cmd[5];
    int correction;
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <server_ip> <delay_ms>" << std::endl;
        return 1;
    }

    int sock;
    struct sockaddr_in server_addr;
    socklen_t server_addr_len = sizeof(server_addr);

    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        std::cerr << "Failed to create socket: " << strerror(errno) << std::endl;
        return 1;
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(8888);

    if (inet_pton(AF_INET, argv[1], &server_addr.sin_addr) <= 0) {
        std::cerr << "Invalid address: " << argv[1] << std::endl;
        close(sock);
        return 1;
    }

    int Cc = 0;
    int Tc = 1000;
    try {
        Tc = std::stoi(argv[2]);
        if (Tc <= 0) {
            throw std::out_of_range("Delay must be a positive integer.");
        }
    }
    catch (const std::exception& e) {
        std::cerr << "Invalid delay value: " << argv[2] << ". Error: " << e.what() << std::endl;
        close(sock);
        return 1;
    }

    client_request req;
    server_response res;

    for (int i = 0; i < 10; ++i) {
        strncpy(req.cmd, "SYNC", 5);
        req.curvalue = Cc;
        std::cout << "Cc: " << Cc << std::endl;

        ssize_t bytes_sent = sendto(
            sock,
            &req,
            sizeof(req),
            0,
            reinterpret_cast<struct sockaddr*>(&server_addr),
            server_addr_len
        );
        if (bytes_sent < 0) {
            std::cerr << "sendto failed: " << strerror(errno) << std::endl;
            close(sock);
            return 1;
        }

        ssize_t bytes_received = recvfrom(
            sock,
            &res,
            sizeof(res),
            0,
            reinterpret_cast<struct sockaddr*>(&server_addr),
            &server_addr_len
        );
        if (bytes_received < 0) {
            std::cerr << "recvfrom failed: " << strerror(errno) << std::endl;
            close(sock);
            return 1;
        }

        std::cout << "Received correction: " << res.correction << std::endl;

        Cc += res.correction;

        std::this_thread::sleep_for(std::chrono::milliseconds(Tc));
    }

    close(sock);
    return 0;
}

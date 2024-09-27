#include <iostream>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
using namespace std;

#define PORT 8080

struct CA {
    char ipaddr[15]; 
    char resource[20]; 
    enum STATUS {NOINIT, INIT, ENTER, LEAVE, WAIT} status;
};

CA ca;

void handleRequest(char* ret, char* buffer) {
    if (strcmp(buffer, "EnterCA") == 0) {
        if (ca.status == CA::ENTER) {
            strcpy(ret, "WAIT");
        } else {
            ca.status = CA::ENTER;
            strcpy(ret, "ENTER");
        }
    } else if (strcmp(buffer, "LeaveCA") == 0) {
        ca.status = CA::LEAVE;
        strcpy(ret, "LEAVE");
    }
    
    cout << "Current CA status: " << ca.status << endl;
}

int main() {
    int server_fd;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);

    ca.status = CA::NOINIT;
    
    server_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (server_fd < 0) {
        cerr << "Socket creation failed." << endl;
        return 1;
    }

    // Настройки сокета
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        cerr << "Bind failed." << endl;
        close(server_fd);
        return 1;
    }

    while (true) {
        struct sockaddr_in clientAddr;
        socklen_t clientAddrSize = sizeof(clientAddr);
        char buffer[1024] = {0};

        cout << "Waiting for clients...\n";
        int bytes_received = recvfrom(
            server_fd,
            buffer,
            1024,
            0,
            reinterpret_cast<struct sockaddr*>(&clientAddr),
            &clientAddrSize
        );
        if (bytes_received < 0) {
            cerr << "recvfrom failed." << endl;
            close(server_fd);
            return 1;
        }
        
        char* ret = new char[6];
        memset(ret, (char)0, 6);
        handleRequest(ret, buffer);

        int bytes_sent = sendto(
            server_fd,
            ret,
            strlen(ret),
            0,
            reinterpret_cast<struct sockaddr*>(&clientAddr),
            clientAddrSize
        );
        if (bytes_sent < 0) {
            cerr << "sendto failed." << endl;
            close(server_fd);
            return 3;
        };
        delete[] ret;
    }

    return 0;
}

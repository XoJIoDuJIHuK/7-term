#include <iostream>
#include <chrono>
#include <thread>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <fstream>
using namespace std;

#define PORT 8080

void writeToFile(const char* filename, const char* client_id) {
    ofstream file;
    file.open(filename, ios_base::app);
    for (int i = 0; i < 5; ++i) {
        this_thread::sleep_for(chrono::seconds(5));
        auto now = chrono::system_clock::to_time_t(chrono::system_clock::now());
        file << client_id << " timestamp: " << ctime(&now);
        cout << client_id << " timestamp: " << ctime(&now);
    }
    file.close();
}

int main(int argc, char const *argv[]) {
    int sock = 0, valread;
    struct sockaddr_in serv_addr;
    char buffer[1024] = {0};
    
    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        cout << "\n Socket creation error \n";
        return -1;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);
    
    // Преобразование адреса
    if(inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0) {
        cout << "\nInvalid address/ Address not supported \n";
        return -1;
    }

    do {
        // Запрос на вход в секцию
        sendto(sock, "EnterCA", strlen("EnterCA"), 0, (struct sockaddr *)&serv_addr, sizeof(serv_addr));
        valread = read(sock, buffer, 1024);
        cout << "Received from coordinator: " << buffer << endl;
        this_thread::sleep_for(chrono::seconds(2));
    } while (strcmp(buffer, "WAIT") == 0);

    if (strcmp(buffer, "ENTER") == 0) {
        writeToFile("shared_file.txt", argv[1]);
        
        // Завершение записи и выход из секции
        sendto(sock, "LeaveCA", strlen("LeaveCA"), 0, (struct sockaddr *)&serv_addr, sizeof(serv_addr));
    } else {
        cout << "ERROR: " << buffer << endl;
    }

    close(sock);
    return 0;
}

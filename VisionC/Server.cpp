
#include "Server.h"

int sock() {
    WSADATA wsaData;
    int iResult;
    char str[1024];
    // Initialize Winsock
    iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (iResult != 0) {
        sprintf_s(str, sizeof(str), "WSAStartup failed: %d\n", iResult);
        OutputDebugStringA(str);
        return 1;
    }

    struct addrinfo* result = NULL, * ptr = NULL, hints;

    ZeroMemory(&hints, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_protocol = IPPROTO_TCP;
    hints.ai_flags = AI_PASSIVE;

    // Resolve the local address and port to be used by the server
    iResult = getaddrinfo(NULL, DEFAULT_PORT, &hints, &result);
    if (iResult != 0) {
        sprintf_s(str, sizeof(str), "getaddrinfo failed: %d\n", iResult);
        OutputDebugStringA(str);
        WSACleanup();
        return 2;
    }

    SOCKET ListenSocket = socket(result->ai_family, result->ai_socktype, result->ai_protocol);
    if (ListenSocket == INVALID_SOCKET) {
        sprintf_s(str, sizeof(str), "Error at socket(): %ld\n", WSAGetLastError());
        OutputDebugStringA(str);
        freeaddrinfo(result);
        WSACleanup();
        return 3;
    }
    iResult = bind(ListenSocket, result->ai_addr, (int)result->ai_addrlen);
    if (iResult == SOCKET_ERROR) {
        sprintf_s(str, sizeof(str), "bind failed with error: %d\n", WSAGetLastError());
        OutputDebugStringA(str);
        freeaddrinfo(result);
        closesocket(ListenSocket);
        WSACleanup();
        return 4;
    }
    freeaddrinfo(result);

    sprintf_s(str, sizeof(str), "Begining listen\n");
    OutputDebugStringA(str);
    if (listen(ListenSocket, SOMAXCONN) == SOCKET_ERROR) {
        sprintf_s(str, sizeof(str), "Listen failed with error: %ld\n", WSAGetLastError());
        OutputDebugStringA(str);
        closesocket(ListenSocket);
        WSACleanup();
        return 5;
    }
    SOCKET ClientSocket = accept(ListenSocket, NULL, NULL);
    if (ClientSocket == INVALID_SOCKET) {
        sprintf_s(str, sizeof(str), "accept failed: %d\n", WSAGetLastError());
        OutputDebugStringA(str);
        closesocket(ListenSocket);
        WSACleanup();
        return 6;
    }

    char recvbuf[DEFAULT_BUFLEN];

    float data[2] = { 0,0 };
    char msgType;
    int iSendResult = 0;
    int recvbuflen = DEFAULT_BUFLEN;
    sprintf_s(str, sizeof(str), "Begining recv\n");
    OutputDebugStringA(str);
    struct RecMessage messageBuffer;
    do {

        iResult = recv(ClientSocket, recvbuf, recvbuflen, 0);
        if (iResult > 0) {
            sprintf_s(str, sizeof(str), "Bytes received: %d %s\n", iResult, recvbuf);
            OutputDebugStringA(str);

            memcpy(&messageBuffer, recvbuf, sizeof(RecMessage));

            INPUT inputs[1] = {};
            switch (messageBuffer.msgType) {
                case 'A': // cursor pos update
                    sprintf_s(str, sizeof(str), "cursor update %ld %f %f\n", messageBuffer.handUpdate.flags, messageBuffer.handUpdate.mouseX, messageBuffer.handUpdate.mouseY);
                    OutputDebugStringA(str);
                    inputs[0].type = INPUT_MOUSE;
                    inputs[0].mi.dwFlags = messageBuffer.handUpdate.flags;
                    DWORD dx = 65535 - (int)(messageBuffer.handUpdate.mouseX * 65535);
                    DWORD dy = (long)(messageBuffer.handUpdate.mouseY * 65535);
                    sprintf_s(str, sizeof(str), "%ld %ld", dx, dy);
                    OutputDebugStringA(str);
                    inputs[0].mi.dx = 65535 - (long)(messageBuffer.handUpdate.mouseX * 65535);
                    inputs[0].mi.dy = (long)(messageBuffer.handUpdate.mouseY * 65535);
                    SendInput(1, inputs, sizeof(INPUT));
                    //SetCursorPos(1980 - (int)(data[0] * 1980), (int)(data[1] * 1080));
                    break;
            }

            // Echo the buffer back to the sender
            //iSendResult = send(ClientSocket, recvbuf, iResult, 0);
            if (iSendResult == SOCKET_ERROR) {
                sprintf_s(str, sizeof(str), "send failed: %d\n", WSAGetLastError());
                OutputDebugStringA(str);
                closesocket(ClientSocket);
                WSACleanup();
                return 7;
            }
            sprintf_s(str, sizeof(str), "Bytes sent: %d\n", iSendResult);
        }
        else if (iResult == 0)
            sprintf_s(str, sizeof(str), "Connection closing...\n");
        else {
            sprintf_s(str, sizeof(str), "recv failed: %d %d\n", iResult, WSAGetLastError());
            OutputDebugStringA(str);
            closesocket(ClientSocket);
            WSACleanup();
            return 8;
        }
        //std::this_thread::sleep_for(std::chrono::milliseconds(333));
    } while (1);
    return 0;
}
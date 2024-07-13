#pragma once
#include <winsock2.h>
#include <ws2tcpip.h>
#include <stdio.h>
#include<chrono>
#include <thread>
#include <iostream>
#include <vector>
#include <windows.h>
#pragma comment(lib, "Ws2_32.lib")


#define MAX_LOADSTRING 100
#define DEFAULT_PORT "27015"
#define DEFAULT_BUFLEN 512

int sock();
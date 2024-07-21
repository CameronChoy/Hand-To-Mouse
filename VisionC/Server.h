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

#ifdef __GNUC__
#define PACK( __Declaration__ ) __Declaration__ __attribute__((__packed__))
#endif

#ifdef _MSC_VER
#define PACK( __Declaration__ ) __pragma( pack(push, 1) ) __Declaration__ __pragma( pack(pop))
#endif


#define MAX_LOADSTRING 100
#define DEFAULT_PORT "27015"
#define DEFAULT_BUFLEN 512

PACK(struct RecMessage {
	unsigned char msgType;
	union {
		struct {
			DWORD flags;
			float mouseX;
			float mouseY;
		} handUpdate;
	};
});

int sock();
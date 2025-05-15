#include "XPLMPlugin.h"
#include "XPLMDataAccess.h"
#include "XPLMProcessing.h"
#include <winsock2.h>
#include <ws2tcpip.h>
#include <cstring>
#include <string>

#pragma comment(lib, "Ws2_32.lib")

SOCKET udpSocket;
XPLMDataRef throttleRef;

extern "C" {

PLUGIN_API int XPluginStart(char* outName, char* outSig, char* outDesc) {
    strcpy(outName, "ThrottleUDPPlugin");
    strcpy(outSig, "sree.f35.throttle");
    strcpy(outDesc, "Receives throttle data from Raspberry Pi via UDP");

    throttleRef = XPLMFindDataRef("sim/flightmodel/engine/ENGN_thro[0]");

    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) return 0;

    udpSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpSocket == INVALID_SOCKET) return 0;

    sockaddr_in serverAddr = {};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(49005);
    serverAddr.sin_addr.s_addr = INADDR_ANY;

    if (bind(udpSocket, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) return 0;

    XPLMRegisterFlightLoopCallback([](float, float, int, void*) -> float {
        char buffer[256] = {};
        sockaddr_in fromAddr;
        int fromLen = sizeof(fromAddr);

        int bytes = recvfrom(udpSocket, buffer, sizeof(buffer), MSG_DONTWAIT, (sockaddr*)&fromAddr, &fromLen);
        if (bytes > 0) {
            try {
                float throttle = std::stof(buffer);
                XPLMSetDataf(throttleRef, throttle);
            } catch (...) {}
        }

        return -1.0f;
    }, 1.0f, nullptr);

    return 1;
}

PLUGIN_API void XPluginStop() {
    XPLMUnregisterFlightLoopCallback([](float, float, int, void*) -> float { return 1.0f; }, nullptr);
    closesocket(udpSocket);
    WSACleanup();
}

PLUGIN_API void XPluginDisable() {}
PLUGIN_API int XPluginEnable() { return 1; }
PLUGIN_API void XPluginReceiveMessage(XPLMPluginID, int, void*) {}

}
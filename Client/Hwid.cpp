#include "hwid.h"
#include <iostream>
#include <sstream>
#include <iomanip>
#include <windows.h>
#include <comdef.h>
#include <Wbemidl.h>
#include <openssl/sha.h>

#pragma comment(lib, "wbemuuid.lib")

std::string getWMIProperty(const std::string& query, const std::string& property) {
    std::string result;
    HRESULT hres;
    hres = CoInitializeEx(0, COINIT_MULTITHREADED);
    if (FAILED(hres)) {
        return result;
    }
    hres = CoInitializeSecurity(
        NULL,
        -1,
        NULL,
        NULL,
        RPC_C_AUTHN_LEVEL_DEFAULT,
        RPC_C_IMP_LEVEL_IMPERSONATE,
        NULL,
        EOAC_NONE,
        NULL
    );
    if (FAILED(hres)) {
        CoUninitialize();
        return result;
    }
    IWbemLocator* pLoc = NULL;
    hres = CoCreateInstance(
        CLSID_WbemLocator,
        NULL,
        CLSCTX_INPROC_SERVER,
        IID_IWbemLocator,
        (LPVOID*)&pLoc
    );
    if (FAILED(hres)) {
        CoUninitialize();
        return result;
    }
    IWbemServices* pSvc = NULL;
    hres = pLoc->ConnectServer(
        _bstr_t(L"ROOT\\CIMV2"),
        NULL,
        NULL,
        0,
        NULL,
        0,
        0,
        &pSvc
    );
    if (FAILED(hres)) {
        pLoc->Release();
        CoUninitialize();
        return result;
    }
    hres = CoSetProxyBlanket(
        pSvc,
        RPC_C_AUTHN_WINNT,
        RPC_C_AUTHZ_NONE,
        NULL,
        RPC_C_AUTHN_LEVEL_CALL,
        RPC_C_IMP_LEVEL_IMPERSONATE,
        NULL,
        EOAC_NONE
    );
    if (FAILED(hres)) {
        pSvc->Release();
        pLoc->Release();
        CoUninitialize();
        return result;
    }
    IEnumWbemClassObject* pEnumerator = NULL;
    hres = pSvc->ExecQuery(
        bstr_t("WQL"),
        bstr_t(query.c_str()),
        WBEM_FLAG_FORWARD_ONLY | WBEM_FLAG_RETURN_IMMEDIATELY,
        NULL,
        &pEnumerator
    );
    if (FAILED(hres)) {
        pSvc->Release();
        pLoc->Release();
        CoUninitialize();
        return result;
    }

    IWbemClassObject* pclsObj = NULL;
    ULONG uReturn = 0;

    while (pEnumerator) {
        HRESULT hr = pEnumerator->Next(WBEM_INFINITE, 1, &pclsObj, &uReturn);
        if (0 == uReturn) {
            break;
        }

        VARIANT vtProp;
        hr = pclsObj->Get(bstr_t(property.c_str()), 0, &vtProp, 0, 0);
        if (SUCCEEDED(hr)) {
            result = _bstr_t(vtProp.bstrVal);
            VariantClear(&vtProp);
        }

        pclsObj->Release();
    }

    // Cleanup
    pSvc->Release();
    pLoc->Release();
    pEnumerator->Release();
    CoUninitialize();

    return result;
}

std::string getHWID() {
    std::string cpuSerial = getWMIProperty("SELECT * FROM Win32_Processor", "ProcessorId");
    std::string gpuSerial = getWMIProperty("SELECT * FROM Win32_VideoController", "PNPDeviceID");
    std::string motherboardSerial = getWMIProperty("SELECT * FROM Win32_BaseBoard", "SerialNumber");
    std::ostringstream oss;
    oss << cpuSerial << gpuSerial << motherboardSerial;
    std::string combined_info = oss.str();
    unsigned char digest[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(combined_info.c_str()), combined_info.size(), digest);
    std::ostringstream sha256_oss;
    for (int i = 0; i < SHA256_DIGEST_LENGTH; ++i) {
        sha256_oss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(digest[i]);
    }

    return sha256_oss.str();
}

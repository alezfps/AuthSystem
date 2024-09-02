#include <iostream>
#include <string>
#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include <memory>
#include "Hwid.h"

using json = nlohmann::json;

size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

class CurlWrapper {
public:
    CurlWrapper() {
        curl_global_init(CURL_GLOBAL_DEFAULT);
        curl = curl_easy_init();
        if (!curl) {
            throw std::runtime_error("Failed to initialize CURL");
        }
    }

    ~CurlWrapper() {
        if (curl) {
            curl_easy_cleanup(curl);
        }
        curl_global_cleanup();
    }

    CURL* get() const { return curl; }

private:
    CURL* curl;
};

std::string send_post_request(const std::string& url, const nlohmann::json& data) {
    CurlWrapper curlWrapper;
    CURL* curl = curlWrapper.get();

    std::string read_buffer;
    struct curl_slist* headers = NULL;
    headers = curl_slist_append(headers, "Content-Type: application/json");

    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data.dump().c_str());
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &read_buffer);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 10L);

    CURLcode res = curl_easy_perform(curl);
    if (res != CURLE_OK) {
        std::cerr << "CURL error: " << curl_easy_strerror(res) << std::endl;
        curl_slist_free_all(headers);
        return "";
    }

    long http_code = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
    if (http_code != 200) {
        std::cerr << "HTTP error: " << http_code << std::endl;
    }

    curl_slist_free_all(headers);
    return read_buffer;
}

int main(int argc, char* argv[]) {
    std::string server_url = "http://localhost:5000";

    if (argc > 1) {
        server_url = argv[1];
    }

    std::string key;
    std::string hwid = getHWID();
    std::cout << "HWID: " << hwid << std::endl;
    std::cout << "Enter key: ";
    std::cin >> key;

    json request_data = {
        {"key", key},
        {"hwid", hwid}
    };

    try {
        std::string response = send_post_request(server_url + "/claim_key", request_data);
        json response_json = json::parse(response);

        if (response_json.contains("error")) {
            std::cerr << "Error: " << response_json["error"] << std::endl;
        }
        else {
            std::cout << "Key for product: " << response_json["product"] << std::endl;
            std::cout << "Expires at: " << response_json["expires_at"] << std::endl;
        }
    }
    catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
    }
    return 0;
}

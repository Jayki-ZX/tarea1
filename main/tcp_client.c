/* BSD Socket API Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <string.h>
#include <sys/param.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_netif.h"
#include "protocol_examples_common.h"
#include "addr_from_stdin.h"
#include "lwip/err.h"
#include "lwip/sockets.h"
#include <math.h>
#include <stdlib.h>
#include "esp_mac.h"
#include "esp_sleep.h"
#include "packeting.c"

//Funcion de fragmentacion a usar para el protocolo 2
int TCP_send_frag(int sock, char transportLayer, char protocolo)
{
    //Parte el mensaje (payload) en trozos de 1000 btyes y los manda por separado, esperando un OK con cada trozo
    printf("Sending!\n");
    char *payload = mensaje(protocolo, transportLayer);
    int payloadLen = messageLength(protocolo) - 1;
    char rx_buffer[128];

    for (int i = 0; i < payloadLen; i += PACK_LEN)
    {

        // Generamos el siguiente trozo
        int size = fmin(PACK_LEN, payloadLen - i);
        char *pack = malloc(size);
        memcpy(pack, &(payload[i]), size);

        //Enviamos el trozo
        int err = send(sock, pack, size, 0);
        free(pack);
        if (err < 0)
        {
            ESP_LOGE(TAG, "Error occurred during sending: errno %d", errno);
        }

        // wait for confirmation
        int len = recv(sock, rx_buffer, sizeof(rx_buffer) - 1, 0);
        // Error occurred during receiving
        if (len < 0)
        {
            //En caso de error abortamos
            ESP_LOGE(TAG, "recv failed: errno %d", errno);
            break;
        }
        else
        {
            rx_buffer[len] = 0;
            char OK_r = rx_buffer[0];
            if (!OK_r)
            {
                ESP_LOGE(TAG, "Server error in fragmented send.");
                free(payload);
                return -1;
            }
        }
    }
    //el último mensaje es solo un \0 para avisarle al server que terminamos
    int err = send(sock, "\0", 1, 0);

    free(payload);

    return err;
}




#if defined(CONFIG_EXAMPLE_IPV4)
#define HOST_IP_ADDR CONFIG_EXAMPLE_IPV4_ADDR
#elif defined(CONFIG_EXAMPLE_IPV6)
#define HOST_IP_ADDR CONFIG_EXAMPLE_IPV6_ADDR
#else
#define HOST_IP_ADDR ""
#endif

#define PORT CONFIG_EXAMPLE_PORT

static const char *TAG = "example";
static const char *payload = "Message from ESP32 ";

static void tcp_client_task(void *pvParameters)
{
    char rx_buffer[128];
    char host_ip[] = HOST_IP_ADDR;
    int addr_family = 0;
    int ip_protocol = 0;

    while (1) {
#if defined(CONFIG_EXAMPLE_IPV4)
        struct sockaddr_in dest_addr;
        dest_addr.sin_addr.s_addr = inet_addr(host_ip);
        dest_addr.sin_family = AF_INET;
        dest_addr.sin_port = htons(PORT);
        addr_family = AF_INET;
        ip_protocol = IPPROTO_IP;
#elif defined(CONFIG_EXAMPLE_IPV6)
        struct sockaddr_in6 dest_addr = { 0 };
        inet6_aton(host_ip, &dest_addr.sin6_addr);
        dest_addr.sin6_family = AF_INET6;
        dest_addr.sin6_port = htons(PORT);
        dest_addr.sin6_scope_id = esp_netif_get_netif_impl_index(EXAMPLE_INTERFACE);
        addr_family = AF_INET6;
        ip_protocol = IPPROTO_IPV6;
#elif defined(CONFIG_EXAMPLE_SOCKET_IP_INPUT_STDIN)
        struct sockaddr_storage dest_addr = { 0 };
        ESP_ERROR_CHECK(get_addr_from_stdin(PORT, SOCK_STREAM, &ip_protocol, &addr_family, &dest_addr));
#endif
        int sock =  socket(addr_family, SOCK_STREAM, ip_protocol);
        if (sock < 0) {
            ESP_LOGE(TAG, "Unable to create socket: errno %d", errno);
            break;
        }
        ESP_LOGI(TAG, "Socket created, connecting to %s:%d", host_ip, PORT);

        int err = connect(sock, (struct sockaddr *)&dest_addr, sizeof(struct sockaddr_in6));
        if (err != 0) {
            ESP_LOGE(TAG, "Socket unable to connect: errno %d", errno);
            break;
        }
        ESP_LOGI(TAG, "Successfully connected");

        //while (1) {
        //Solo hace envio de 5 paquetes para pruebas
        for (int i = 0; i < 5; i++) {
            // Recibe de parte del server, la indicacion de cual de los protocolos usar y que transport layer
            solicitud_buffer = malloc(2);
            int len = recv(sock, solicitud_buffer, sizeof(solicitud_buffer) - 1, 0);
            char protocol = solicitud_buffer[0];
            char transportLayer = solicitud_buffer[1];
            // char 1 byte
            //char* msg = mensaje(PROTOCOL1, T_TCP);
            //int MSG_SIZE = messageLength(PROTOCOL1);

            // memcpy((void*) c, (void*) &d, 1);
            // Si no se estan usando strings, no hay que usar caracter de termino '\0'
            //c[8] = '\0';
            //payload = c;
            //Si el protocolo es 4, envia el mensaje por fragmentos, sino lo envia completo
            if (protocol == 4){
                int err = TCP_send_frag(sock, transportLayer, protocol);
                if (err < 0) {
                    ESP_LOGE(TAG, "Error occurred during sending: errno %d", errno);
                    break;
                }
            }
            else{
                int err = send(sock, mensaje(protocol, transportLayer), messageLength(protocol), 0);
                if (err < 0) {
                    ESP_LOGE(TAG, "Error occurred during sending: errno %d", errno);
                    break;
                }
            }
            //int err = send(sock, msg, MSG_SIZE, 0);
            //entrar en modo deep sleep por 60 segundos
            //esp_deep_sleep_start();

            int len = recv(sock, rx_buffer, sizeof(rx_buffer) - 1, 0);
            // Error occurred during receiving
            if (len < 0) {
                ESP_LOGE(TAG, "recv failed: errno %d", errno);
                break;
            }
            // Data received
            else {
                rx_buffer[len] = 0; // Null-terminate whatever we received and treat like a string
                ESP_LOGI(TAG, "Received %d bytes from %s:", len, host_ip);
                ESP_LOGI(TAG, "%s", rx_buffer);
            }

            vTaskDelay(2000 / portTICK_PERIOD_MS);
        }

        if (sock != -1) {
            ESP_LOGE(TAG, "Shutting down socket and restarting...");
            shutdown(sock, 0);
            close(sock);
        }
    }
    vTaskDelete(NULL);
}

void app_main(void)
{
    esp_sleep_enable_timer_wakeup(60000000);
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    /* This helper function configures Wi-Fi or Ethernet, as selected in menuconfig.
     * Read "Establishing Wi-Fi or Ethernet Connection" section in
     * examples/protocols/README.md for more information about this function.
     */
    ESP_ERROR_CHECK(example_connect());

    xTaskCreate(tcp_client_task, "tcp_client", 4096, NULL, 5, NULL);
}

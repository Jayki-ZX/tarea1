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

//Generacion de datos
float floatrand(float min, float max){
    return min + (float)rand()/(float)(RAND_MAX/(max-min));
}

//Accelerometer sensor
//accx
float* acc_sensor_acc_x(){
    float* arreglo = malloc(sizeof(float)*2000);
    for(int i = 0; i < 2000; i++){
        arreglo[i] = 2*sin(2*M_PI*0.001*i);
    }
    return arreglo;
}
//accy 
float* acc_sensor_acc_y(){
    float* arreglo = malloc(sizeof(float)*2000);
    for(int i = 0; i < 2000; i++){
        arreglo[i] = 3*cos(2*M_PI*0.001*i);
    }
    return arreglo;
}
//acc z
float* acc_sensor_acc_z(){
    float* arreglo = malloc(sizeof(float)*2000);
    for(int i = 0; i < 2000; i++){
        arreglo[i] = 10*sin(2*M_PI*0.001*i);
    }
    return arreglo;
}

//THPC sensor
//temp
char THPC_sensor_temp(){
    char n =(char) 5 + (rand() %25);
    return n;
}

//hum
char THPC_sensor_hum(){
    return (char)floatrand(30.0, 80.0);
}

//pres
int THPC_sensor_pres(){
    return (rand() % 200) + 1000;
}

float THPC_sensor_co(){
    return floatrand(30, 200);
}

//Battery level
unsigned char batt_sensor(){
    return (unsigned char) (rand() % 100);
}

//Accelerometer kpi
float Accelerometer_kpi_amp_x(){
    return floatrand(0.0059, 0.12);
}
float Accelerometer_kpi_frec_x(){
    return floatrand(29.0, 31.0);
}
float Accelerometer_kpi_amp_y(){
    return floatrand(0.0041, 0.11);
}
float Accelerometer_kpi_frec_y(){
    return floatrand(59.0, 61.0);
}
float Accelerometer_kpi_amp_z(){
    return floatrand(0.008, 0.15);
}
float Accelerometer_kpi_frec_z(){
    return floatrand(89.0, 91.0);
}

float Accelerometer_kpi_RMS(){
    float ampx = Accelerometer_kpi_amp_x();
    float ampy = Accelerometer_kpi_amp_y();
    float ampz = Accelerometer_kpi_amp_z();
    return sqrt(pow(ampx,2) + pow(ampy,2) + pow(ampz,2));
}
//Empaquetamiento 
unsigned short lengmsg[6] = {2, 6, 16, 20, 44, 12016};
unsigned short dataLength(char protocol){
    return lengmsg[ (unsigned int) protocol]-1;
}

//Empaquetamiento del header
//transport layer 0 es tcp y 1 es udp
char* header(char protocol, char transportLayer){
	char* head = malloc(12);
    uint8_t* MACaddrs = malloc(6);
	esp_efuse_mac_get_default(MACaddrs);
    memcpy((void*) &(head[0]), (void*) MACaddrs, 2);
	memcpy((void*) &(head[2]), (void*) MACaddrs, 6);
    head[8]= transportLayer;
	head[9]= protocol;
	unsigned short dataLen = dataLength(protocol);
	memcpy((void*) &(head[10]), (void*) &dataLen, 2);
	free(MACaddrs);
	return head;
}

//Empaquetamiento del mensaje
// Arma un paquete para el protocolo 0
char* dataprotocol0(){
    
    char* msg = malloc(dataLength(1)); //6
    msg[0] = 1;
    char batt = batt_sensor();
    msg[1] = batt;
    int t = 0; //Este es el timestamp
    memcpy((void*) &(msg[1]), (void*) &t, 4);
    return msg;
}

// Arma un paquete segun el protocolo 1
char* dataprotocol1(){
    char* msg = malloc(dataLength(2)); //16
    //1 byte
    msg [0] = 1;
    //1 byte
    float batt = batt_sensor();
    msg[1] = batt;
    //4 bytes
    int t = 0;
    memcpy((void*) &(msg[2]), (void*) &t, 4);
    //1 byte
    char temp = THPC_sensor_temp();
    msg[6] = temp;
    //4 bytes
    float press = THPC_sensor_pres();
    memcpy((void*) &(msg[7]), (void*) &press, 4);
    //1 byte
    char hum = THPC_sensor_hum();
    msg[11] = hum;
    //4 bytes
    float co = THPC_sensor_co();
    memcpy((void*) &(msg[12]), (void*) &co, 4);
    return msg;
}

// Arma un paquete segun el protocolo 2
char* dataprotocol2(){
    char* msg = malloc(dataLength(2)); //16
    //1 byte
    msg [0] = 1;
    //1 byte
    float batt = batt_sensor();
    msg[1] = batt;
    //4 bytes
    int t = 0;
    memcpy((void*) &(msg[2]), (void*) &t, 4);
    //1 byte
    char temp = THPC_sensor_temp();
    msg[6] = temp;
    //4 bytes
    float press = THPC_sensor_pres();
    memcpy((void*) &(msg[7]), (void*) &press, 4);
    //1 byte
    char hum = THPC_sensor_hum();
    msg[11] = hum;
    //4 bytes
    float co = THPC_sensor_co();
    memcpy((void*) &(msg[12]), (void*) &co, 4);
    //4 bytes
    float rms = Accelerometer_kpi_RMS();
    memcpy((void*) &(msg[16]), (void*) &rms, 4);
    return msg;
}

// Arma un paquete segun el protocolo 3
char* dataprotocol3(){
    char* msg = malloc(dataLength(2)); //16
    //1 byte
    msg [0] = 1;
    //1 byte
    float batt = batt_sensor();
    msg[1] = batt;
    //4 bytes
    int t = 0;
    memcpy((void*) &(msg[2]), (void*) &t, 4);
    //1 byte
    char temp = THPC_sensor_temp();
    msg[6] = temp;
    //4 bytes
    float press = THPC_sensor_pres();
    memcpy((void*) &(msg[7]), (void*) &press, 4);
    //1 byte
    char hum = THPC_sensor_hum();
    msg[11] = hum;
    //4 bytes
    float co = THPC_sensor_co();
    memcpy((void*) &(msg[12]), (void*) &co, 4);
    //4 bytes
    float rms = Accelerometer_kpi_RMS();
    memcpy((void*) &(msg[16]), (void*) &rms, 4);
    //4 bytes
    float ampx = Accelerometer_kpi_amp_x();
    memcpy((void*) &(msg[20]), (void*) &ampx, 4);
    //4 bytes
    float frecx = Accelerometer_kpi_frec_x();
    memcpy((void*) &(msg[20]), (void*) &frecx, 4);
    //4 bytes
    float ampy = Accelerometer_kpi_amp_y();
    memcpy((void*) &(msg[20]), (void*) &ampy, 4);
    //4 bytes
    float frecy = Accelerometer_kpi_frec_y();
    memcpy((void*) &(msg[20]), (void*) &frecy, 4);
    //4 bytes
    float ampz = Accelerometer_kpi_amp_z();
    memcpy((void*) &(msg[20]), (void*) &ampz, 4);
    //4 bytes
    float frecz = Accelerometer_kpi_frec_z();
    memcpy((void*) &(msg[20]), (void*) &frecz, 4);
    return msg;
}
// Arma un paquete segun el protocolo 4
//TODO
//char* dataprotocol4(){
//    return;
//}

unsigned short messageLength(char protocol){
    int headerLength = 12;
    return 1+headerLength+dataLength(protocol);
}

//Empaqueta mensaje
char* mensaje (char protocol, char transportLayer){
	char* mnsj = malloc(messageLength(protocol));
	mnsj[messageLength(protocol)-1]= '\0';
	char* hdr = header(protocol, transportLayer);
	char* data;
	switch (protocol) {
		case 0:
			data = dataprotocol0();
			break;
		case 1:
			data = dataprotocol1();
			break;
		case 2:
			data = dataprotocol2();
			break;
        case 3:
			data = dataprotocol3();
			break;
        //case 4:
		//	data = dataprotocol4();
		//	break;
		default:
			data = dataprotocol0();
			break;
	}
	memcpy((void*) mnsj, (void*) hdr, 12);
	memcpy((void*) &(mnsj[12]), (void*) data, dataLength(protocol));
    memcpy((void*) mnsj, (void*) data, dataLength(protocol));
	free(hdr);
	free(data);
	return mnsj;
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
            // char 1 byte
            int MSG_SIZE = 8;
            char* c = malloc(MSG_SIZE);
            int d = 28;
            int e = 32;
            //memcpy(c, &a, 4);
            memcpy((void*) c, (void*) &d, 4);
            memcpy((void*) &(c[4]), (void*) &e, 4);

            ESP_LOGI("print", "c is: %d", sizeof(c));
            // memcpy((void*) c, (void*) &d, 1);
            // Si no se estan usando strings, no hay que usar caracter de termino '\0'
            //c[8] = '\0';
            //payload = c;
            int err = send(sock, c, MSG_SIZE, 0);
            ESP_LOGI("print", "c is: %d", sizeof(c));
            free(c);
            if (err < 0) {
                ESP_LOGE(TAG, "Error occurred during sending: errno %d", errno);
                break;
            }

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

#include <math.h>
#include <stdlib.h>
#include "esp_system.h"
#include "esp_mac.h"
#include "esp_log.h"

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
    char n =(char) 5 + (rand() %26);
    return n;
}

//hum
char THPC_sensor_hum(){
    return (char)floatrand(30.0, 80.0);
}

//pres
int THPC_sensor_pres(){
    return (rand() % 201) + 1000;
}

float THPC_sensor_co(){
    return floatrand(30, 200);
}

//Battery level
unsigned char batt_sensor(){
    return (unsigned char) (rand() % 101);
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
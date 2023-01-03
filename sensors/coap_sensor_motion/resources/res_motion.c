#include "contiki.h"
#include "coap-engine.h"
#include <string.h>
#include "time.h"
#include "os/dev/leds.h"
#include "sys/etimer.h"

/* Log configuration */
#include "sys/log.h"
#define LOG_MODULE "motion sensor"
#define LOG_LEVEL LOG_LEVEL_DBG
#define EVENT_INTERVAL 40

static bool isClosed = false;
static bool isActive = false;
static int opening = 90;

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
static void res_event_handler(void);


EVENT_RESOURCE(motion_sensor,
"title=\"Motion sensor: ?POST/PUT\";obs",
res_get_handler, //--> handler
NULL,
NULL,
NULL,
res_event_handler); //--> handler invoke auto  every time the state of resource change

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset)
{

    int length;

    char msg[300];


    if(isActive==true && opening<90){
        opening= (rand()%(90-10+1))+10;
    }else if(isActive==false){
        opening = 0;
    }
    if(isClosed==1){
        isActive=true;
    }else if (isClosed==0){
        isActive=false;
    }
    char value1 = isActive == 1 ? 'T': 'N';
    char value2 = isClosed == 1 ? 'T': 'N';
    strcpy(msg,"{\"closed\":\"");
    strncat(msg,&value2,1);
    strcat(msg,"\", \"active\":\"");
    strncat(msg,&value1,1);
    strcat(msg,"\", \"opening\":\"");
    char degree[400];
    sprintf(degree, "%d", opening);
    strcat(msg,degree);
    strcat(msg,"\"}");
    length = strlen(msg);
    memcpy(buffer, (uint8_t *)msg, length);

    printf("MSG detection send : %s\n", msg);
    coap_set_header_content_format(response, TEXT_PLAIN);
    coap_set_header_etag(response, (uint8_t *)&length, 1);
    coap_set_payload(response, (uint8_t *)buffer, length);
}


static void res_event_handler(void){
    srand(time(NULL));
    int random_v = rand() % 2;

    bool newClosed = isClosed;
    if(random_v == 0){
        newClosed=!isClosed;
    }

    if(newClosed != isClosed){
        isClosed = newClosed;
        // Notify all the observers
        coap_notify_observers(&motion_sensor);
    }
}
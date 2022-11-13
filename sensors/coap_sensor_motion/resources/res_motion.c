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
#define EVENT_INTERVAL 30

static bool isClosed = false;
static bool isActive = false;
static int opening = 90;

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
static void res_event_handler(void);


EVENT_RESOURCE(motion_sensor, //--> name
"title=\"Motion sensor: ?POST/PUT\";obs",   //---> descriptor (obs significa che è osservabile)
res_get_handler, //--> handler
NULL,
NULL,
NULL,
res_event_handler); //--> handler invoke auto  every time the state of resource change

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset)
{
    // Create a JSON message with the detected presence value and led value
    // In both the resources the get_handler return the current sensor values
    int length;

    char msg[300];
    // T = true
    // N = negative

    if(isActive==true && opening<90){
        opening=opening+10;
    }else if(isActive==false){
            opening = 90;
    }
    if(isClosed==1){
        isActive=true;
    }else if (isClosed==0){
        isActive=false;
    }
    char active = isActive == 1 ? 'T': 'N';
    char closed = isClosed == 1 ? 'T': 'N';
    strcpy(msg,"{\"isClosed\":\"");
    strncat(msg,&closed,1);
    strcat(msg,"\", \"info\":\"");
    strncat(msg,&active,1);
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

static void res_event_handler(void)
{
    srand(time(NULL));
    int random_v = rand() % 2;

    bool newClosed = isClosed;
    if(random_v == 0){
        newClosed=!isCloseù;
    }

    if(newClosed != isClosed){
        isClosed = newClosed;
        // Notify all the observers
        coap_notify_observers(&motion_sensor);
    }

}

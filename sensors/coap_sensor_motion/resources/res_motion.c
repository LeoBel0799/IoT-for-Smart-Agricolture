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

// Modifica da 41 a 62
static bool closedgate = false;
static bool sysActive = false;
static int openingDegree = 180;

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
static void res_event_handler(void);


EVENT_RESOURCE(motion_sensor, //--> name
"title=\"Mechanical Grape Cover status: ?POST/PUT\";obs",   //---> descriptor (obs significa che è osservabile)
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

    if(sysActive==true && openingDegree<180){
        openingDegree=openingDegree+10;
    }else if(sysActive==false){
            openingDegree = 180;
    }
    if(closedgate==1){
        sysActive=true;
    }else if (closedgate==0){
        sysActive=false;
    }
    char active = sysActive == 1 ? 'T': 'N';
    char closed = closedgate == 1 ? 'T': 'N';
    strcpy(msg,"{\"Closed\":\"");
    strncat(msg,&closed,1);
    strcat(msg,"\", \"Active\":\"");
    strncat(msg,&active,1);
    strcat(msg,"\", \"Opening Degree\":\"");
    char degree[400];
    sprintf(degree, "%d°", openingDegree);
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

    bool newClosed = closedgate;
    if(random_v == 0){
        newClosed=!closedgate;
    }

    if(newClosed != closedgate){
        closedgate = newClosed;
        // Notify all the observers
        coap_notify_observers(&motion_sensor);
    }

}

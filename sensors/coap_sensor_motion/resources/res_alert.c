#include "contiki.h"
#include "coap-engine.h"
#include <string.h>
#include "time.h"
#include "os/dev/leds.h"
#include "sys/etimer.h"

//LOG
#include "sys/log.h"
#define LOG_MODULE "motion sensor"
#define LOG_LEVEL LOG_LEVEL_DBG

static bool isActive = false;
static int opening = 90;

static void get_opening_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
static void post_switch_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);


//Building up client response

RESOURCE(alert_actuator, //--> name
"title=\"alarm_actuator: ?POST\";obs;rt=\"alarm\"",
get_opening_handler,
post_switch_handler,
NULL,
NULL); //--> handler invoke auto  every time the state of resource change


static void get_opening_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset)
{
    // Create a JSON message with the detected presence value and led value
    int length;
    char msg[300];
    // T = true
    // N = negative
    char value2 = isActive == true ? 'T': 'N';
    strcpy(msg,"{\"active\":\"");
    strncat(msg,&value2,1);
    //strcat(msg,"\" \"");
    strcat(msg,"\", \"opening\":\"");
    char degree[400];
    sprintf(degree, "%d", opening);
    strcat(msg,degree);
    strcat(msg,"\"}");
    printf("Message: %s\n",msg);
    length = strlen(msg);
    memcpy(buffer, (uint8_t *)msg, length);

    coap_set_header_content_format(response, TEXT_PLAIN);
    coap_set_header_etag(response, (uint8_t *)&length, 1);
    coap_set_payload(response, (uint8_t *)buffer, length);


}


static void post_switch_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset)
{
    printf("entered in POST function!\n");
    if(request != NULL) {
        LOG_DBG("POST/PUT Request Sent\n");
    }

    printf("Post handler called\n");
    size_t len = 0;
    const char *state = NULL;
    int check = 1;
    if((len = coap_get_post_variable(request, "state", &state))) {
        if (atoi(state) == 1){
            if(isActive == true && opening < 90){
                opening = opening + 10;
            }
            leds_set(LEDS_NUM_TO_MASK(LEDS_GREEN));
            isActive = true;
        }
        else if(atoi(state) == 0){
            leds_set(LEDS_NUM_TO_MASK(LEDS_RED));
            isActive = false;
            opening = 0;
        }
        else{
            check = 0;
        }
    }
    else{
        check = 0;
    }

    if (check){
        coap_set_status_code(response, CHANGED_2_04);
    }
    else{
        coap_set_status_code(response, BAD_REQUEST_4_00);
    }
}




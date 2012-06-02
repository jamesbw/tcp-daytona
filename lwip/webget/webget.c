#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "lwipopts.h"
#include "lwip/tcpip.h"
//#include "lwip/sockets.h"
#include "lwip/sys.h"
#include "lwip/opt.h"
#include "lwip/tcp.h"
#include "lwip/inet.h"

#include "netif/tapif.h"
#include "netif/tunif.h"


#define HTTP_GET "GET "
#define HTTP_VER " HTTP/1.1"

static ip_addr_t ipaddr, netmask, gw;
static sys_sem_t init_sem;
static sys_sem_t exit_sem;

int
usage(char* prog)
{
    printf("Usage: %s <ipaddr> <path>\n", prog);
    return 1;
}

struct netif netif;

static void
init_netifs(void)
{
#if PPP_SUPPORT
  pppInit();
#if PPP_PTY_TEST
  ppp_sio = sio_open(2);
#else
  ppp_sio = sio_open(0);
#endif
  if(!ppp_sio)
  {
      perror("Error opening device: ");
      exit(1);
  }

#ifdef LWIP_PPP_CHAP_TEST
  pppSetAuth(PPPAUTHTYPE_CHAP, "lwip", "mysecret");
#endif

  pppOpen(ppp_sio, pppLinkStatusCallback, NULL);
#endif /* PPP_SUPPORT */
  
#if LWIP_DHCP
  {
    IP4_ADDR(&gw, 0,0,0,0);
    IP4_ADDR(&ipaddr, 0,0,0,0);
    IP4_ADDR(&netmask, 0,0,0,0);

    netif_add(&netif, &ipaddr, &netmask, &gw, NULL, tapif_init,
              tcpip_input);
    netif_set_default(&netif);
    dhcp_start(&netif);
  }
#else
  
  netif_set_default(netif_add(&netif,&ipaddr, &netmask, &gw, NULL, tapif_init,
                  tcpip_input));
  netif_set_up(&netif);

#endif

#if 0
  /* Only used for testing purposes: */
  netif_add(&ipaddr, &netmask, &gw, NULL, pcapif_init, tcpip_input);
#endif
  
#if 0 // LWIP_TCP  
  tcpecho_init();
  shell_init();
  httpd_init();
#endif
#if 0 //LWIP_UDP  
  udpecho_init();
#endif  
  /*  sys_timeout(5000, tcp_debug_timeout, NULL);*/
}

static void
tcpip_init_done(void *arg)
{
  init_netifs();

  sys_sem_signal(&init_sem);
}

err_t
send_request(struct tcp_pcb *tpcb)
{

    printf("Connected\n");

    sys_sem_signal(&exit_sem);

    return ERR_OK;
}

err_t 
connected(void *arg, struct tcp_pcb *tpcb, err_t err)
{
    if (err != ERR_OK) {
        tcp_abort(tpcb);
        return ERR_ABRT;
    }

    return send_request(tpcb);
}


int
connection_init(ip_addr_t * ipaddr, short port) {
    struct tcp_pcb *pcb;
    err_t err;

    printf("Connecting...\n");

    pcb = tcp_new();
    LWIP_ASSERT("tcp: tcp_new failed", pcb != NULL);

    /* set SOF_REUSEADDR here to explicitly bind httpd to multiple interfaces */
    err = tcp_connect(pcb, ipaddr, port, connected);
    if (err != ERR_OK) {
        printf("tcp: tcp_connect failed, err == %i\n", err);
        exit(1);
    }

    return ERR_OK;
}

int
main (int argc, char** argv)
{
    // Local addresses.
    IP4_ADDR(&gw, 192,168,0,1);
    IP4_ADDR(&netmask, 255,255,255,0);
    IP4_ADDR(&ipaddr, 192,168,0,200);

    if (argc < 3) {
        return usage(argv[0]);
    }

    char* host_s = argv[1];
    short port = atoi(argv[2]);
    char* path_s = argv[3];

    ip_addr_t addr;

    if (ipaddr_aton(host_s, &addr) == 0) {
        printf("Could not parse address.");
        return usage(argv[0]);
    }

    /*
    struct in_addr addr_in;

    addr_in.s_addr = inet_addr(host_s);

    if (inet_aton(host_s, &addr_in) == 0) {
        printf("Could not parse address.");
        return usage(argv[0]);
    }

    char * ip = inet_ntoa(addr_in);

    printf("Connecting to '%s'...\n", ip);

    struct sockaddr_in addr;
    // set up address to connect to
    //
    memset(&addr, 0, sizeof(addr));
    addr.sin_len = sizeof(addr);
    addr.sin_family = AF_INET;
    addr.sin_port = PP_HTONS(3000);
    addr.sin_addr = addr_in;
    */
    if(sys_sem_new(&init_sem, 0) != ERR_OK && sys_sem_new(&init_sem, 0) != ERR_OK) {
        LWIP_ASSERT("Failed to create semaphore", 0);
    }

    struct netif netif;

    netif_init();

    tcpip_init(tcpip_init_done, &init_sem);
    sys_sem_wait(&init_sem);
    printf("TCP/IP initialized.\n");

    sleep(10);

    connection_init(&addr, port);

    sys_sem_wait(&exit_sem);

    return 0;
}

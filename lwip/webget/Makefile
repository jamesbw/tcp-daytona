LWIP_DIR=lwip/src
CONTRIB_DIR=contrib
LIB_DIR=$(CONTRIB_DIR)/ports/unix/proj/lib

CFLAGS=-I $(LWIP_DIR)/include/ -I . -I $(CONTRIB_DIR)/ports/unix/include/ -I $(LWIP_DIR)/include/ipv4/ -Wall

all: webget

webget: webget.c liblwip.so
	 gcc $(CFLAGS) -o webget webget.c -L $(LIB_DIR) -llwip -pthread

liblwip.so:
	make -C $(LIB_DIR) all

clean:
	rm -f *.o webget
	make -C $(LIB_DIR) clean

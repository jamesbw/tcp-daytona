tcp-daytona
===========


Replicating TCP Daytona
-----------------------

Instructions:
- launch a c1.xlarge Ubuntu 12.04 server instance on EC2
- ssh in with X forwarding: ssh -X ubuntu@xxxxx.amazonaws.com
- install git : sudo apt-get install git
- clone github repo: git clone https://github.com/jamesbw/tcp-daytona.git
- cd tcp-daytona
- ./setup
- ./run
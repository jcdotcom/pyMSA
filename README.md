pymail is a simple MSA server made in Python!

run from command line with "py pyMSA.py"

the server runs indefinitely awaiting connection requests from MUA clients on localhost
once a connection to an MUA has been established, it handles the incoming data from a
new thread, enabling the handling of multiple connections simultaneously.

currently it is limited to localhost, for testing purposes I have been using thunderbird
configured to use loopback as the address for the server and watching tcp port 9000
in wireshark.

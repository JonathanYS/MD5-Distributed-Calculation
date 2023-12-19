# MD5-Distributed-Calculation
This is a distributed calculation to find the original MD5 message (before applying the algorithm to the value). It can also be called Distributed BruteForce, because of the way it works.

This project is for the purposes of learning, it is a simple project.
Connectivity checks are not enabled, so if you try to execute first the client and the server isn't up, it won't work. You need to first execute the server and then the clients.
The random value that is being created for the MD5 algorithm is between 10000-99999 (integers). I have picked a specific number of Max Clients that will be connected to the server (3).

This program works in the way of brute forcing the original value before the MD5 algorithm has been applied to it. It creates processes according to the number of cores in each client's computer, and in each process, 2 threads are brute-forcing their way to get the original value. If a client's computer has more cores than others, it will "calculate" (try) more ranges of values than other clients' computers.

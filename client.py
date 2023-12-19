""" This program was created by Yonatan Deri. """
import socket
import threading
import os
import multiprocessing
import math
import hashlib

ip = "127.0.0.1"
port = 5000
cores = os.cpu_count()
processes_list = []
is_found = False


class Thread(threading.Thread):
    """ This class is responsible for the threading activity of the client (2 threads per process). """
    def __init__(self, t_range, md5, t_client_socket):
        """ This function is an object build function which is responsible for building an object of this class.
        It gets the range that this thread needs to calculate, the md5 target message and the client socket
        (so it will be able to communicate with the server when it finds the correct decoded message). """
        threading.Thread.__init__(self)
        self.range = t_range
        self.md5_target = md5
        self.client_socket = t_client_socket

    def run(self):
        """ This function runs when the class's object gets started (the thread gets started),
         using the start() function. """
        global is_found
        for _ in range(self.range[0], self.range[1] + 1):
            if not is_found:
                hashed_value = hashlib.md5(str(_).encode()).hexdigest()
                if hashed_value == self.md5_target:
                    self.client_socket.send(str(_).encode())
                    is_found = True
                    print("+++++++found+++++++: ", str(_))
                    break


class Calculate(multiprocessing.Process):
    """ This class is responsible for the creation of multiple processes as well as
    creating objects of the Thread class so it will assign 2 threads per process. """
    def __init__(self, p_client_socket, t1_ranges, t2_ranges, md5):
        """ This function is an object build function which is responsible for building an object of this class.
         It gets the client socket, the ranges that the 2 soon to be crated threads need to calculate and the
          md5 target message. """
        multiprocessing.Process.__init__(self)
        self.t1_ranges = t1_ranges
        self.t2_ranges = t2_ranges
        self.md5_target = md5
        self.client_socket = p_client_socket

    def run(self):
        """ This function runs when the class's object gets started (the process gets started),
         using the start() function. """
        threads_list = [Thread(self.t1_ranges, self.md5_target, self.client_socket),
                        Thread(self.t2_ranges, self.md5_target, self.client_socket)]
        for thread in threads_list:
            thread.start()
        for thread in threads_list:
            thread.join()


class Client:
    """ This class is responsible for all of the client functionality. """
    def __init__(self):
        """ This function is an object build function which is responsible for building an object of this class.
         It assigns the class's variable my_socket a socket and starts the connection process to the server. """
        self.my_socket = socket.socket()
        self.my_socket.connect((ip, port))

    def send_cores(self):
        """ This function is responsible for sending the cores number
         the client's device have and sends it to the server. """
        global cores
        print(cores)
        self.my_socket.send((str(cores)).encode())

    def get_ranges(self):
        """ This function is responsible for getting the ranges (the server has sent) that this client
         needs to calculate. It's also calculating the ranges that each thread will need to calculate.  """
        global processes_list, cores
        threads_calculating_ranges = []
        self.my_socket.settimeout(None)
        md5_target = self.my_socket.recv(1024).decode()
        # print("==============md5_target==============: ", md5_target)
        ranges = self.my_socket.recv(1024).decode()
        # print("==============ranges==============: ", ranges)
        ranges = tuple(map(int, ranges.split(', ')))
        numbers_to_iterate = ranges[1] - ranges[0] + 1
        sum_threads = cores * 2  # 2 threads per process (core).
        ranges_per_each_thread = math.ceil(numbers_to_iterate / sum_threads)
        start = ranges[0]
        end = start + ranges_per_each_thread
        for _ in range(sum_threads):
            threads_calculating_ranges.append((start, end))
            start = end + 1
            end = end + ranges_per_each_thread
        i = 0
        for _ in range(cores):
            processes_list.append(Calculate(self.my_socket, threads_calculating_ranges[i],
                                            threads_calculating_ranges[i + 1], md5_target))
            i += 2
        # print("====================threads_calculating_ranges====================: ", threads_calculating_ranges)
        # print("====================threads_calculating_ranges====================: ", processes_list)

    def listen_to_found_message(self):
        """ This function is responsible for listening to the server for a "found" message.
         This message will stop the activity of the client (all the threads and processes). """
        global is_found
        while not is_found:
            flag = self.my_socket.recv(5).decode()
            print(flag)
            if flag == "found":
                is_found = True


if __name__ == '__main__':
    """ This function is responsible for creating the client object from the "Client" class,
     calling the client object's functions and starting all the processes (process per core). """
    client_obj = Client()
    client_obj.send_cores()

    client_obj.get_ranges()

    for process in processes_list:
        process.start()

    client_obj.listen_to_found_message()

""" This program was created by Yonatan Deri. """
import socket
import threading
import hashlib
import random
import math

md5_target = 0
MAX_POSSIBILITIES = 9 * (math.pow(10, 4))  # 9 possibilities for the first digit (1 - 9. Without the 0) times 10 to
# the power of 4, because we have 10 possibilities (0-9) for each of the next 4 digits.
# That gives us 90000 possibilities.
client_dict = dict()  # the keys are the client_socket objects and the values are
# the amount of cores of each connected client's machine.
client_calc_ranges = dict()
MAX_CLIENT = 3
ip = '127.0.0.1'
port = 5000
threads_list = []
ranges_dict = dict()
is_found = False
message = None


class GetCoresThread(threading.Thread):
    """ This class is responsible for getting the amount of cores each client's machine has in a threaded way. """
    def __init__(self, client_sock, client_address):
        """ This function is an object build function which is responsible for building an object of this class.
         It gets the client socket (for communication with the client) and the client address (just for standard). """
        threading.Thread.__init__(self)
        self.client_sock = client_sock
        self.client_address = client_address

    def run(self):
        """ This function runs when the class's object gets started (the thread gets started),
         using the start() function. """
        global client_dict
        while True:
            cores = self.client_sock.recv(3).decode()
            client_dict[self.client_sock] = cores
            break


class GetCalculations(threading.Thread):
    """ This class is responsible for sending the required variables for the clients for them to start the calculations.
     As well as listening to the clients if one of them has found the md5 digest original message."""
    def __init__(self, client_sock, calc_range):
        """ This function is an object build function which is responsible for building an object of this class.
        It gets the client socket (for communication with the client) and the calculation ranges to send to the client,
        so it will know what ranges it needs to calculate while other clients calculate other ranges
        (this is what makes this program to work in a distributed way of calculating). """
        threading.Thread.__init__(self)
        self.client_socket = client_sock
        self.range = str(calc_range).replace('(', "").replace(')', "")
        # print("++++++++++range++++++++++: ", self.range)

    def run(self):
        """ This function runs when the class's object gets started (the thread gets started),
         using the start() function. """
        global is_found, message, md5_target
        self.client_socket.send(str(md5_target).encode())
        self.client_socket.send(self.range.encode())
        message = self.client_socket.recv(1024).decode()
        # print("++++++++++message++++++++++: ", message)
        is_found = True


class Server:
    """ This class is responsible for all of the server functionality. """
    def __init__(self):
        """ This function is an object build function which is responsible for building an object of this class.
         It assigns a socket to a variable called "server_socket", bind this socket
         using the ip and port declared earlier, and starts the listening process to all of the 3 clients. """
        self.server_socket = socket.socket()
        self.server_socket.bind((ip, port))
        self.server_socket.listen(MAX_CLIENT)

    def calculate_ranges(self):
        """ This function is responsible for calculating the ranges each client needs to calculate using it's machine,
         in respect to the amount of cores each client's machine has. """
        global client_dict, client_calc_ranges, ranges_dict
        sum_cores = 0
        for dict_key in client_dict:
            cores = client_dict[dict_key]
            print("cores", cores)
            sum_cores += int(cores)  # Let's say the machines by default don't have hyperthreading on them, so each
            # client would run 1 process per core (so for an 8 core machine, the machine would run 8 processes.
            # Given that it's entire purpose is brute forcing the MD5 decoded digest original message).
        print("sum_cores: ", sum_cores)
        for dict_key in client_dict:
            ranges_dict[dict_key] = math.ceil((int(client_dict[dict_key]) / sum_cores) * MAX_POSSIBILITIES)
        # print("================ranges_dict================: ", ranges_dict)
        previous_range = 10000
        start_range = 10000
        for ranges_dict_key in ranges_dict:
            current_range = int(ranges_dict[ranges_dict_key])
            current_range = current_range + previous_range
            ranges_dict[ranges_dict_key] = (start_range, current_range)
            previous_range = current_range
            start_range = previous_range + 1

    def get_clients(self):
        """ This function in responsible for getting the connection of 3 clients (the MAX value for this exercise)
         to the server. """
        count = 0  # Max = 3.
        global client_dict, threads_list

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(client_address)
            client_dict[client_socket] = 0
            threads_list.append(GetCoresThread(client_socket, client_address))
            count += 1
            if count == MAX_CLIENT:
                # print("====================client_dict====================: ", client_dict)
                break

    def send_found_message(self):
        """ This function is responsible for sending the "found" message to all of the clients,
         telling them that the search is over because the md5 digest original message has been found. """
        global is_found, client_dict
        while not is_found:
            pass
        for key_client in client_dict:
            key_client.send("found".encode())


def create_hash():
    """ This function is responsible for creating the md5 target message,
     using a random input value (to the md5 algorithm) in the range of 10000-99999. """
    global md5_target
    num = random.randint(10000, 99999)
    md5_target = hashlib.md5(str(num).encode()).hexdigest()


if __name__ == '__main__':
    """ This function is responsible for calling all of the other functions,
     creating the classes' objects and starting all of the threads. """
    create_hash()
    print(md5_target)
    server = Server()
    server.get_clients()

    for thread in threads_list:
        thread.start()
    for thread in threads_list:
        thread.join()
    # print("====================client_dict====================: ", client_dict)

    server.calculate_ranges()  # Waiting for all the clients to be connected first.
    # print("====================ranges_dict====================: ", ranges_dict)

    calculations_list = []
    for key in ranges_dict:
        calculations_list.append(GetCalculations(key, ranges_dict[key]))
    # print("====================calculations_list====================: ", calculations_list)

    for thread in calculations_list:
        thread.start()

    #  No need to wait for all threads to be finished because,
    #  when they get the "found" message, they will stop on their own.

    server.send_found_message()

    print("+++++++++++++message+++++++++++++: ", message)

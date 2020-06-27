import os
import subprocess


class BinCommandFailure(Exception):
    pass


class AddServerFailure(Exception):
    pass


class DisableServerFailure(Exception):
    pass


class EnableServerFailure(Exception):
    pass


class PanicServerFailure(Exception):
    pass


class RemoveServerFailure(Exception):
    pass


class SetLoadMultiplierServerFailure(Exception):
    pass


class Scalelite(object):

    def __init__(self, bin_path):
        run_scalelite_command_in_shell(bin_path)
        self.bin_path = bin_path

    def status(self):
        """
        rake status
        List all BigBlueButton servers and all meetings currently running
        :return: servers: List of servers dict
        """
        scalelite_command = f"{self.bin_path} status"
        response = run_scalelite_command_in_shell(scalelite_command)
        servers = []

        response_list = response.split("\n")
        for row in response_list:
            if "HOSTNAME" not in row:
                list_chunk = row.split()
                if len(list_chunk) == 6:
                    list_chunk.insert(0, "")
                server = {
                    'hostname': list_chunk[0],
                    'state': list_chunk[1],
                    'status': list_chunk[2],
                    'meetings': int(list_chunk[3]),
                    'users': int(list_chunk[4]),
                    'largest_meetings': int(list_chunk[5]),
                    'videos': int(list_chunk[6])
                }
                servers.append(server)
        return servers

    def list_servers(self):
        """
        rake servers
        List configured BigBlueButton servers
        :return: servers: List of servers dict
        """
        scalelite_command = f"{self.bin_path} servers"
        response = run_scalelite_command_in_shell(scalelite_command)
        servers = []

        if response != "No servers are configured":
            response_list = response.split("\n")
            list_chunks = [response_list[i:i + 7] for i in range(0, len(response_list), 7)]
            for list_chunk in list_chunks:
                server = {
                    'id': list_chunk[0].replace("id: ", ""),
                    'url': list_chunk[1].replace("url: ", "").replace("\t", ""),
                    'secret': list_chunk[2].replace("secret: ", "").replace("\t", ""),
                    'state': list_chunk[3].replace("\t", ""),
                    'load': list_chunk[4].replace("load: ", "").replace("\t", ""),
                    'load_multiplier': list_chunk[5].replace("load_multiplier: ", "").replace("\t", ""),
                    'status': list_chunk[6].replace("\t", "")
                }
                servers.append(server)
        return servers

    def add_server(self, url, secret, load_multiplier=None):
        """
        rake servers:add[url,secret,load_multiplier]
        Add a new BigBlueButton server (it will be added disabled)
        :param url: Complete URL to the BigBlueButton API endpoint of the server.
        :param secret: Security secret to access the BigBlueButton API endpoint of the server.
        :param load_multiplier: Used to give individual servers a higher or lower priority over other servers
        :return: server_id: ID value used when updating or removing the server
        """
        params_list = [url, secret]
        if load_multiplier:
            params_list.append(load_multiplier)
        params_string = ','.join(str(param) for param in params_list)

        scalelite_command = f"{self.bin_path} servers:add[{params_string}]"
        response = run_scalelite_command_in_shell(scalelite_command)
        response_list = response.split("\n")

        if response_list[0] != "OK":
            raise AddServerFailure(response)
        server_id = response_list[1].replace("id: ", "")
        return server_id

    def disable_server(self, server_id):
        """
        rake servers:disable[id]
        Mark a BigBlueButton server as unavailable to stop scheduling new meetings
        :param server_id: ID value used when updating or removing the server
        """
        scalelite_command = f"{self.bin_path} servers:disable[{server_id}]"
        response = run_scalelite_command_in_shell(scalelite_command)
        if response != "OK":
            raise DisableServerFailure(response)

    def enable_server(self, server_id):
        """
        rake servers:enable[id]
        Mark a BigBlueButton server as available for scheduling new meetings
        :param server_id: ID value used when updating or removing the server
        """
        scalelite_command = f"{self.bin_path} servers:enable[{server_id}]"
        response = run_scalelite_command_in_shell(scalelite_command)
        if response != "OK":
            raise EnableServerFailure(response)

    def set_load_multiplier_server(self, server_id, load_multiplier):
        """
        rake servers:loadMultiplier[id,loadMultiplier]
        Set the load-multiplier of a BigBlueButton server
        :param server_id: ID value used when updating or removing the server
        :param load_multiplier: Used to give individual servers a higher or lower priority over other servers.
        """
        params_list = [server_id, load_multiplier]
        params_string = ','.join(str(param) for param in params_list)

        scalelite_command = f"{self.bin_path} servers:loadMultiplier[{params_string}]"
        response = run_scalelite_command_in_shell(scalelite_command)
        if response != "OK":
            raise SetLoadMultiplierServerFailure(response)

    def panic_server(self, server_id):
        """
        rake servers:panic[id]
        Mark a BigBlueButton server as unavailable, and clear all meetings from it
        :param server_id: ID value used when updating or removing the server
        """
        scalelite_command = f"{self.bin_path} servers:panic[{server_id}]"
        response = run_scalelite_command_in_shell(scalelite_command)
        if response != "OK":
            raise PanicServerFailure(response)

    def remove_server(self, server_id):
        """
        rake servers:remove[id]
        Remove a BigBlueButton server
        :param server_id: ID value used when updating or removing the server
        """
        scalelite_command = f"{self.bin_path} servers:remove[{server_id}]"
        response = run_scalelite_command_in_shell(scalelite_command)
        if response != "OK":
            raise RemoveServerFailure(response)


def run_scalelite_command_in_shell(scalelite_command):
    process = subprocess.run(scalelite_command,
                             shell=True,
                             check=False,
                             capture_output=True,
                             env=os.environ)
    try:
        process.check_returncode()
        return process.stdout.decode("UTF-8").strip()

    except subprocess.CalledProcessError:
        error_msg = process.stderr.decode("UTF-8").strip()
        raise BinCommandFailure(f"{scalelite_command}: {error_msg}")

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

    def about(self):
        """
        rake about
        List versions of all Rails frameworks and the environment
        :return:
        """
        scalelite_command = f"{self.bin_path} about"
        return run_scalelite_command_in_shell(scalelite_command)

    def status(self):
        """
        rake status
        List all BigBlueButton servers and all meetings currently running
        :return:
        """
        scalelite_command = f"{self.bin_path} status"
        return run_scalelite_command_in_shell(scalelite_command)

    def list_servers(self):
        """
        rake servers
        List configured BigBlueButton servers
        :return:
        """
        scalelite_command = f"{self.bin_path} servers"
        return run_scalelite_command_in_shell(scalelite_command)

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

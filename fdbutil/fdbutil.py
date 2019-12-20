""" Contains class and code for getting data from and controlling foundationdb """
import json
import os
import socket
import subprocess
from fdbutil.exceptions import FdbUtilException


import configparser


# Shamelessly lifted from:
# https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
def get_ip_address():
    """ Using the opening of a socket to determine my local ip. """

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
    except socket.error as exc:
        raise FdbUtilException("Unable to determine local ip address")

    return sock.getsockname()[0]


class FdbUtil(object):
    """ Class for performing some routine tasks with fdbutil """

    def __init__(self, args):
        """ Initialize some defaults to define the config file if we need it """

        self.suffix = args.suffix
        self.confdir = args.confdir

        # create path for the foundationdb.conf file defining all the fdbserver processes
        # typically this ends up being /etc/foundationdb/foundationdb.conf
        self.conf = os.path.join(self.confdir, "foundationdb.conf")

        try:
            os.stat(self.conf)
        except OSError as exc:
            FdbUtilException("%s is missing" % self.conf)

    def _get_cluster_file(self, tier="ssd"):

        # The ssd tier cluster file is typically labeled "fdb.cluster" so we'll
        # allow the user to specify either "fdb" or "ssd".
        if tier == "ssd":
            tier = "fdb"

        return os.path.join(self.confdir, tier + self.suffix)

    def _get_status(self, cluster_file):
        """
        Grab the fdb status. We try to use the fdb python api but
        will fallback to using a subprocess to call fdbcli

        :param str cluster_file: full path to the cluster file with the coordinator list
        :return: dict from json decoded status
        :rtype: dict
        """

        results = subprocess.Popen(
            ["fdbcli", "-C", cluster_file, "--exec", "status json"],
            stdout=subprocess.PIPE,
        )

        # TODO: probably should add some logic to test that important known keys exist
        try:
            fdb_status = json.loads(results.stdout.read())
        except (ValueError, json.JSONDecodeError) as exc:
            raise FdbUtilException("Unable to parse json status payload: %s" % (exc))

        return fdb_status

    def missing(self, args):
        """
        Determines missing processes for specified tier (defaults to ssd tier)

        :param argparse.Namespace args: parsed args
        """

        my_ip = get_ip_address()

        all_tiers = (
            [args.tier]
            if args.tier != "all"
            else ["ssd", "memory", "memory1", "memory2", "memory3"]
        )

        metric_output = []
        stdout_output = []
        for tier in all_tiers:
            cluster_file = self._get_cluster_file(tier)

            try:
                os.stat(cluster_file)
            except OSError:
                continue

            (missing, expected) = self._get_procs(cluster_file, my_ip)

            output = {proc: 1 if proc in missing else 0 for proc in expected}
            output.update({"tier": tier})
            metric_output.append(output)

            missing_list = "None" if len(missing) == 0 else ", ".join(missing)
            stdout_output.append(
                "missing processes for %s tier: %s" % (tier, missing_list)
            )

        if args.metrics:
            print(json.dumps(metric_output))
        else:
            for line in stdout_output:
                print(line)

    def _get_procs(self, cluster_file, my_ip):
        """
        Get both the expected and running processes and then generate a set of missing procs.

        :param str cluster_file: full path to a cluster file listing the cluster coordinators
        :param str my_ip: my local ip when determing which running processes belong to the local ip
        :return: missing processes and expected processes
        :rtype: tuple
        """

        # Grab the status in json format
        status = self._get_status(cluster_file)

        # from the json status, get all the existing running processes
        running_procs = self._get_running_processes(status)

        # now parse the fdb config file(*not* the cluster file with the coordinators) to determine which
        # processes are expected to run on this host. We'll only get the processes associated with the
        # cluster_file
        expected = self._get_expected_processes(cluster_file)

        # Now loop through discovered processes and create a python set with all discovered processes for this host
        disc_procs = set()
        for proc in running_procs:
            (ip_addr, port) = proc[0].split(":")
            if ip_addr == my_ip:
                disc_procs.add(port)

        missing_procs = sorted(expected.difference(disc_procs))

        return missing_procs, sorted(expected)

    def _get_running_processes(self, status):
        """
        Parse the decoded json and return the known running processes
        :param dict status: the decoded json of the status
        :return: list of tuples with running processes
        :rtype: list
        """

        # This loops all processes and returns a list of tuples that describe each known process.
        # The two elements are
        # 1. address in format of <IP>:<PORT>
        # 2. the type of process. This will be used in a later iteration of the code.
        # Note: could use list comprehension but for readability, skipping this
        proc_details = status["cluster"]["processes"]
        all_procs = []
        for proc in proc_details:
            try:
                all_procs.append(
                    (proc_details[proc]["address"], proc_details[proc]["class_type"])
                )
            except KeyError as exc:
                raise FdbUtilException("Unable to parse json status")
        return all_procs

    def _get_expected_processes(self, cluster_file):
        """
        Parses the foundationdb configuraton file which is typically /etc/foundationdb/foundationdb.conf and returns
        a set of expected processes for the tier specified in self.tier

        :return: set of processes
        """

        # foundationdb is in configparser format. yay!
        config = configparser.ConfigParser()
        config.read(self.conf)

        expected_processes = set()
        for section in config.sections():
            # We use section header names to determine the processes.
            if "fdbserver.4" in section:
                port = section.split(".")[1]

                # Cluster files are specified in the section or default to "fdb.cluster"
                try:
                    cluster = os.path.basename(config[section]["cluster_file"])
                except KeyError:
                    # Default value if cluster_file is not defined
                    cluster = "fdb.cluster"

                if cluster == os.path.basename(cluster_file):
                    expected_processes.add(port)

        return expected_processes

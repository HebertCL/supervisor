import os
import sys
import time
import shlex
import argparse
import subprocess
import logging

import psutil

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

logger.addHandler(handler)

def is_process_alive(pid):
    """
    Checks if a process is running given its pid.
    Returns false if process is not found.

    param pid: int The pid number
    """
    return psutil.pid_exists(int(pid))


def is_supervised_process(pid, name):
    """
    Given a PID and name, checks if the curren running process
    matches the expected process name to supervise. Returns true
    if process command matches with the supervised process name,
    otherwise returns false.

    param pid: int The pid number
    param name: str The process name
    """
    proc = psutil.Process(pid)
    cmdline = proc.cmdline()
    command = " ".join(cmdline)

    if command == name:
        return True

    return False


def start_process(name, healthcheck, attempts, backoff):
    """
    Run a given process and retries a number of times if process exit code
    is not successful. Returns an error when number of attempts is reached.

    param name: str The command to be executed
    param attempts: int The number of attempts to run the command
    param backoff: int Time in seconds to wait between every attempt
    """ 
    tries = 0
    
    logger.info(
        f"Running process {name}"
    )
    while tries <= attempts:
        with subprocess.Popen(command) as proc:
            exit_status = proc.wait(healthcheck)
            if exit_status == None:
                logger.info(
                    f"Process {name} running with PID {proc.pid}"
                )
                continue
            elif exit_status == 0:
                logger.info(
                    f"Process {name} with PID {proc.pid} finished successfully"
                )
                return proc.returncode


def args_parser(args):
    """ 
    Argument parser function

    param: args arguments
    """
    parser = argparse.ArgumentParser(
        description="Supervise a running process with a given set of arguments"
    )

    parser.add_argument(
        "--pid",
        help="PID number of the process to supervise",
        type=int,
        required=True,
    )
    parser.add_argument(
        "--name",
        help="The process expected to be running under a given PID",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--check",
        help="Number in seconds to wait between cheking for the process",
        type=int,
        required=True,
    )
    parser.add_argument(
        "--retries",
        help="Number of attempts to start a process before giving up",
        type=int,
        default=0,
        required=False,
    )
    parser.add_argument(
        "--backoff",
        help="Number in seconds to wait before re-attempting to start a process",
        type=int,
        default=0,
        required=False,
    )

    return parser.parse_args(args)

def main(pid, proc_name, healthcheck, retries, backoff):
    """ 
    Main function
    """
    logger.info(
        f"Validating PID {pid} is up and running"
    )
    if is_process_alive(pid) and is_supervised_process(pid, proc_name):
        logger.info(
            f"Process {proc_name} running with PID {pid}. Checking back in the next {healthcheck} seconds"
        )
    else:
        logger.info(
            f"Process or command does not match. Exiting"
        )
        


if __name__ == "__main__":
    # print(sys.argv[1:])
    args = args_parser(sys.argv[1:])
    main(args.pid, args.name.strip(), args.check, args.retries, args.backoff)

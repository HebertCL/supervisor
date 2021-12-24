"""
Script that looks for a process using its pid and command
and starts the command if not running, with the ability to attempt
to run the command several times if exit statusis other than 0
"""
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


def run(cmd):
    """
    Run a given process.
    Returns the PID and returned code from execution.

    param cmd: str The command to be executed
    """
    logger.info("Running process %s", cmd)

    command = shlex.split(cmd)
    proc = subprocess.Popen(command)
    proc.wait()

    return proc.pid, proc.returncode


def supervise_process(pid, cmd):
    """
    Checks for PID and cmdline to match with provided input.
    Returns false if either of the conditions is not met.

    param pid: int The pid number
    param name: str The command to validate against cmdline method
    """
    if is_process_alive(pid) and is_supervised_process(pid, cmd):
        return True

    return False


def run_process(cmd, retry, backoff):
    """
    Attemtps to start a process and retries in case it fails.
    Returns exit code.

    param cmd: str The command to execute
    param retry: int The number of times to attempt to run the command before giving up
    param backoff: int Time in seconds between every attempt
    """
    attempt = 1

    while attempt < retry:
        _, status_code = run(cmd)
        if status_code == 0:
            return status_code
        else:
            logger.info(
                "Command %s failed with status code %s. Attempt %s/%s",
                cmd,
                status_code,
                attempt,
                retry,
            )
            time.sleep(backoff)
            attempt +=1

    _, status_code = run(cmd)
    if status_code != 0:
        logger.info(
            "Command %s execution failed with status %s. Exiting", cmd, status_code
        )
        return status_code

    return status_code


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


def main(pid, cmd, healthcheck, retry, backoff):
    """
    Main function
    """
    logger.info("Validating PID %s is up and running", pid)
    while supervise_process(pid, cmd):
        logger.info(
            "Process %s running with PID %s. Checking back in the next %s seconds",
            cmd,
            pid,
            healthcheck,
        )
        time.sleep(healthcheck)

    logger.info("Process not found. Starting process...")
    status = run_process(cmd, retry, backoff)
    if status == 0:
        logger.info("Process %s with PID %s finished with status %s", cmd, pid, status)
        sys.exit(0)

    logger.error("Process execution failed. Exiting")
    sys.exit(1)


if __name__ == "__main__":
    # print(sys.argv[1:])
    args = args_parser(sys.argv[1:])
    main(args.pid, args.name.strip(), args.check, args.retries, args.backoff)

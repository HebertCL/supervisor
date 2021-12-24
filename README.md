# Supervisor

A small program that tracks other processes and starts them if not running

## Get started

To get supervisor up and running it is recommended to use Python's virtual environments.
To do so, simply run the following commands (from root project):

```sh
pip install virtualenv
virtualenv -p $(whereis python | awk '{print $2}') venv
source venv/bin/activate
pip install -r requirements.txt
```

## Supervisor logic flow

Current version of supervisor assumes there's an already running process and expects a PID from which it will be monitoring such process. If not found, attempts to execute the given command with a given number of retries and waits for its completion. It will retry the command until command execution exits with return code 0, otherwise, fails.

![supervisor](./supervisor.png "Supervisor logic")
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
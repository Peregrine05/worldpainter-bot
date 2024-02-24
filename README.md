# README

This Discord bot was created for use in the 
[WorldPainter Discord server](https://discord.gg/NrGWtXnra8). Instances of 
the bot are intended to be used in at most one server.

## Setup

This project has been tested with Python 3.10 and 3.11. Python 3.12 does not 
work.

Download the code with `git clone` or the green `Code` button. Optionally, 
create a virtual environment. Populate the fields of the `example_env` file 
with the appropriate values, and then rename the `example_env` file to 
`.env`.

To run the bot, use the commands:

```commandline
pip install -r requirements.txt
python main.py
```

If storage space is limited, use the command:

```commandline
pip install --no-cache-dir -r requirements.txt && python main.py
```

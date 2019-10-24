# HG180U Parental Control Helper Script
A python script to manage the Parental Control system of a HG180u PLDT Home DSL router.

I use the Parental Controls feature of my PLDT Home DSL router to control the times that devices are allowed to connect to the internet. It's mostly used for making sure that kids do not go past their bedtime surfing the net. Accessing and using the router's dashboard is slow and inneficient so I decided to make a script to do it automatically.

This is an improvement of [my old script](https://github.com/accidentalrebel/PLDT-Router-Parental-Control) that works on an older router.

## How it works
This script sends an ssh request to 192.168.1.1 containing the user specified commands as parameters. 

To get these commands I studied the scripts from inside the router that is related to handling the parental control entries. 

## Usage
```
usage: net_parental_control.py [-h] [-e ENABLE] [-l] [-v] [-d DEVICES] [-a ADD]
                               [-r REMOVE]
                               user password

positional arguments:
  user                  The username to sign in using SSH.
  password              The password to sign in using SSH.

optional arguments:
  -h, --help            show this help message and exit
  -e ENABLE, --enable ENABLE
                        Enable the parental control. Only accepts "0" or "1"
  -l, --list            Lists the entries.
  -v, --verbose         Logs verbosely.
  -d DEVICES, --devices DEVICES
                        Specify path of the devices.json file to use
  -a ADD, --add ADD     Add an entry. The format should be: username
                        Mon,Tue,Wed,Thu,Fri,Sat 08:00-19:00. This option should be
                        passed along with "-d".
  -r REMOVE, --remove REMOVE
                        Remove an entry by specifying the entry number.
```

## Devices File
The devices.json file should look like the one below:
```
{
    "device1": "88:88:88:88:88:88",
    "device2": "88:88:88:88:88:88",
    "device3": "88:88:88:88:88:88"
}
```

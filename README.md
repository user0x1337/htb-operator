# HTB-Operator - A CLI for accessing Hackthebox 
<img src="https://github.com/user-attachments/assets/7ea918e1-f9d3-4de5-bca7-5bf396bb4f6e" alt="Bild" width="300"/>

![GitHub release](https://img.shields.io/github/v/release/user0x1337/htb-operator)
![GitHub Repo stars](https://img.shields.io/github/stars/user0x1337/htb-operator)

<div>
  <img alt="current version" src="https://img.shields.io/badge/Linux-supported-success">
  <img alt="current version" src="https://img.shields.io/badge/Windows-unsupported-blue">
  <img alt="current version" src="https://img.shields.io/badge/MacOS-supported_|_untested-yellow">
  <br>
  <img alt="amd64" src="https://img.shields.io/badge/amd64%20(x86__64)-supported-success">
  <img alt="arm64" src="https://img.shields.io/badge/arm64%20(aarch64)-supported-success">
  <br>
  <img alt="current version" src="https://img.shields.io/badge/Python_>=3.12-supported-success">
  <br>
  <img alt="current version" src="https://img.shields.io/badge/HTB--API_v4-supported-success">
  <br><br>
</div>

HTB-Operator is a project developed and maintained by [user0x1337](https://github.com/user0x1337). It interacts with the API of HackTheBox, a popular cybersecurity training platform. The main objective is to save time while interacting with the platform of HTB. 

<img alt="current version" src="https://img.shields.io/badge/Status-Under_Development-red">

# Installation
HTB-Operator is written in Python. In general, it can be executed on every OS if python is installed on this OS. But it was only tested on Linux (Kali, Ubuntu) and has some limitations on Windows (I was not in the mood for migrating some features for Windows...maybe later).

It is strongly recommended to create a venv:
```bash
1. python3 -m venv .venv
2. source .venv/bin/activate 
``` 

You can install htb-operator using pip:
```bash
pip3 install git+https://github.com/user0x1337/htb-operator
```

# Configuration
You need an API-token from HTB. For that:
1. Visit the URL: [https://app.hackthebox.com/profile/settings](https://app.hackthebox.com/profile/settings)
2. Click on "Create App Token"
3. Store the token
4. Call `htb-operator init -api YOUR_API_TOKEN`

# Commands
The tool is command based. You can call `-h` or `--help` for displaying the help information in each stage. The "top level" commands are displayed if you call the programm without any arguments:


```bash 
htb-operator
```
![image](https://github.com/user-attachments/assets/4dd6800d-53c1-464e-acb3-db61ca261082)


## init
TBD
## Info 
The `info` command retireves the information for a user. If no user is indicated, it will display the information for the authenticated user, i.e. for your user. 
```bash
htb-operator info
```

### `-s` / `--username`
Using `-s USERNAME` or `--username USERNAME` you can search for the user with the username `USERNAME` and display its profile. E.g.
```bash
htb-operator info -s HTBBot
```
![image](https://github.com/user-attachments/assets/8a613234-4dce-4f41-8927-cf004c857cdb)


### `-a` / `--activity`
Usually, the activity is limited to the recent 20 entries. Using `-a` or `--activity` shows the entire activity history without any limits.
```bash
htb-operator info -a
```
 
 `-s` / `--username` works with this flag, too.
```bash
htb-operator info -a -s HTBBot
```
![image](https://github.com/user-attachments/assets/addda738-5435-4e66-9058-2efe81ca4a65)


## certificate
You can list or download obtained certification of completion. 

### `-l` / `--list`
List all obtained certification of completion.
```bash
htb-operator certificate --list
```
![image](https://github.com/user-attachments/assets/0783bd15-590f-43a9-a4b0-eefa08e6409e)


### download
Using the `download` subcommand, you are able to download the certificate. With `--id` you have to indicate the certification id (e.g. obtained by listing all certificates) and with `-f` or `--filename`, you can set the target directory and the target filename.

![image](https://github.com/user-attachments/assets/8725d37a-32ea-4d2c-bc23-d90c184cec62)

# challenge
The challenge command provides commands for listing all available challenges, displaying info about a specific challenge, downloading files and writeups, starting challenge instances or submitting flags. For example, if you want to download the file, unzip it and start the instance in HTB, you need only one command:
```bash
htb-operator challenge download --name "Hunting License" --unzip -s
```

## search
Using search, you are able to search for challenge which contain the name of the searching word. The argument `--name` is required.
```bash
htb-operator challenge search --name Spook
```
![image](https://github.com/user-attachments/assets/420f4564-b3d9-40ba-8ff6-f72ec7c54fe2)

### `--unsolved`
Displays only challenges which are not solved. If both `--solved` and `--unsolved` are speicifed, just unsolved challenges will be returned.

### `--solved`
Displays only challenges which are already solved. If both `--solved` and `--unsolved` are speicifed, just unsolved challenges will be returned.

### `--todo`
Displays only challenges whose `TODO`-Flag has been set.

###  `--category` 
Displays only challenges which are part of the specified category. You can specify more than one category, but they must be seperated by commas [,]. For example:
```bash
htb-operator challenge search --name Spook --category Web,Crypto,Pwn
```
![image](https://github.com/user-attachments/assets/1475a94a-7017-4101-b742-de0838c77eab)

### `--difficulty`
Displays only challenges which matches the specified difficulty.




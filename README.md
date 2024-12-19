# HTB-Operator - A CLI for accessing Hackthebox 
<img src="https://github.com/user-attachments/assets/7ea918e1-f9d3-4de5-bca7-5bf396bb4f6e" alt="Bild" width="300"/>

![GitHub Tags](https://img.shields.io/github/v/tag/user0x1337/htb-operator)
![GitHub Releases](https://img.shields.io/github/v/release/user0x1337/htb-operator)
![GitHub Repo stars](https://img.shields.io/github/stars/user0x1337/htb-operator)

<div>
  <b>OS</b><br>
  <img alt="current version" src="https://img.shields.io/badge/Linux-supported-success"><br>
  <img alt="current version" src="https://img.shields.io/badge/Windows-supported_|_but_not_all_features-lightgreen"><br>
  <img alt="current version" src="https://img.shields.io/badge/MacOS-supported_|_untested-yellow">
  <br><br>
  <b>Architecture</b><br>
  <img alt="amd64" src="https://img.shields.io/badge/amd64%20(x86__64)-supported-success"><br>
  <img alt="arm64" src="https://img.shields.io/badge/arm64%20(aarch64)-supported-success">
  <br><br>
<b>Misc</b><br>
  <img alt="current version" src="https://img.shields.io/badge/Python_>=3.12-supported-success">
  <br> 
  <img alt="current version" src="https://img.shields.io/badge/HTB--API_v4-supported-success">
  <br><br>
</div>

HTB-Operator is a project developed and maintained by [user0x1337](https://github.com/user0x1337). It interacts with the API of [HackTheBox](https://www.hackthebox.com/), a popular cybersecurity training platform. The main objective is to save time while interacting with the platform of HTB. 

<img alt="current version" src="https://img.shields.io/badge/Status-Under_Development-red">

# Restrictions on Windows
Windows imposes certain restrictions or obstacles, which result in not supporting all features. Features/commands which will not work:
* VPN: Starting and stopping

# Installation
HTB-Operator is written in Python. In general, it can be executed on every OS if python is installed on this OS. But it was only tested on Linux (Kali, Ubuntu) and has some limitations on Windows (I was not in the mood for migrating some features for Windows...maybe later).

It is strongly recommended to create a venv. Use [pipx](https://pipx.pypa.io/latest/) (which will automatically create a virtual python environment) to install `htb-operator`:
```bash
pipx install htb-operator
```

# Configuration
You need an API-token from HTB. For that:
1. Visit the URL: [https://app.hackthebox.com/profile/settings](https://app.hackthebox.com/profile/settings)

2. Click on "Create App Token"
   
![image](https://github.com/user-attachments/assets/48024f28-df90-4f39-b285-5a09a2ac8bb5)

3. Create a token
   
![image](https://github.com/user-attachments/assets/045e6828-fa0b-4cc7-b644-33384fc1e901)

4. Store the token
   
![image](https://github.com/user-attachments/assets/5eb05a1f-4716-4d23-869f-29255fb7404f)

5. Call `htb-operator init -api YOUR_API_TOKEN`

# Commands
The tool is command based. You can call `-h` or `--help` for displaying the help information in each stage. The "top level" commands are displayed if you call the programm without any arguments:


```bash 
htb-operator
```
![image](https://github.com/user-attachments/assets/fbb1a80a-8005-40bd-86c6-ac3ff32dabf0)




# init
The init command should be the first command you use. As already mentioned above, you need to register your generated API-Key using the init command:
```bash
htb-operator init -api YOUR_API_TOKEN
```
![image](https://github.com/user-attachments/assets/e5f3792b-46a8-4211-82dd-5aea5f516044)

The init command also supports to indicate an alternative URL for accessing HTB API. This should only be used with caution and in an unlikely case when HTB itself changes the API-URL.

# Info 
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


# certificate
You can list or download obtained certification of completion. 

### `-l` / `--list`
List all obtained certification of completion.
```bash
htb-operator certificate --list
```
![image](https://github.com/user-attachments/assets/d9fabf5d-cb2a-4663-812a-55cd030ff275)


### download
Using the `download` subcommand, you are able to download the certificate. With `--id` you have to indicate the certification id (e.g. obtained by listing all certificates) and with `-f` or `--filename`, you can set the target directory and the target filename.

![image](https://github.com/user-attachments/assets/8725d37a-32ea-4d2c-bc23-d90c184cec62)

# machine
The machine command provides commands for listing all available machines, displaying info about a specific machine, stop, reset and start a machine, and so on. 

## list
Lists all active and retired machines. Furthermore, you can add some filter flags for optimizing your view. Check out the provided flags with `htb-operator machine list -h`. 
```bash
htb-operator machine list
```
![image](https://github.com/user-attachments/assets/d4ab1f19-d695-448c-816c-62268dc806eb)

Active machines which will be retired soon, are flagged as `✘/✔`.

### `--limit` 
As default only the 20 recent machines are displayed. If you want to increase or decrease the number of displyed machine, just use the `--limit <NUMBER>` flag. For example:
```bash
htb-operator machine list --limit 10
```
![image](https://github.com/user-attachments/assets/a2ad559b-944a-470e-932a-429d8d93e6b3)

### `--retired`
If the `--retired` flag is set, only retired machines are displayed. 
```bash
htb-operator machine list --retired
```
![image](https://github.com/user-attachments/assets/da96ca5a-ff12-4bff-9edc-57319304f2ed)


### `--active`
If the `--active` flag is set, only active machines are displayed. 
```bash
htb-operator machine list --active
```

### `--group-by-os` 
You can change grouping of the result set. Instead of grouping the result by `Retired` and `Active`, you can group the result by OS.
```bash
htb-operator machine list --group-by-os
```
![image](https://github.com/user-attachments/assets/1dcfbcde-c640-4281-849c-8e98bc48aa52)

## start
Start the instance of a given machine. If another machine already runs, you will asked for terminating the running machine before starting the new one. You must indicate the ID of the machine using `--id` flag or the name using `--name` 
```bash
htb-operator machine start --id 620
```
![image](https://github.com/user-attachments/assets/6e13bdb3-e755-4a6a-9cee-b08b6884c56a)


### `--start-vpn` 
If you use this flag, a VPN connection will automatically be established based on the configured VPN-Server. This operation needs **root/sudo/admin** permission. In Linux, you will be asked for entering your sudo password. 
```bash
htb-operator machine start --id 620 --start-vpn
```
![image](https://github.com/user-attachments/assets/2820fa16-0aa7-49fa-940e-09c0d9a67b38)


### `--update-hosts-file`
If you use this flag, the hosts file in `/etc/hosts` (Linux) or `/drivers/etc/hosts` (Windows, not tested) will be updated. The hostname of the machine plus the suffix `htb` (i.e. `HOSTNAME.htb`) and the assigned IP address will be inserted. This operation needs **root/sudo/admin** permission. In Linux, you will be asked for entering your sudo password.  

```bash
htb-operator machine start --id 620 --update-hosts-file
```
![image](https://github.com/user-attachments/assets/5399d44a-aaa5-4383-97fa-f4e90e00422b)


### `--wait-for-release`
Only works for scheduled machine. Starting the machine is paused until the release date/time will be reached and will be available for the entire community. It can be useful if you want to get a first blood. 
```bash
htb-operator machine start --id 620 --wait-for-release
```

### `--script <SCRIPT_FILE>`
Executes a custom bash script when all previous steps are done (i.e. an IP was assigned, possible VPN-Connection has been established, and so on). htb-operator will set the following environment variables:
* $HTB_MACHINE_IP -> Assigned IP
* $HTB_MACHINE_NAME -> Machine name (e.g. "Sea") 
* $HTB_MACHINE_OS -> Machine OS ("Linux", "Windows", "FreeBSD", ...)
* $HTB_MACHINE_DIFFICULTY -> Machine's difficulty (e.g. "Easy")
* $HTB_MACHINE_INFO -> Info provided by HTB
* $HTB_MACHINE_HOSTNAME -> Hostname (e.g. "sea.htb") 

#### Example
I would like to run following script:
```bash
#!/usr/bin/bash

echo "Starting script, assigned IP $HTB_MACHINE_IP and Hostname $HTB_MACHINE_HOSTNAME"
nmap "$HTB_MACHINE_HOSTNAME" -p 80 --open
```
My call looks like (as you can see, I can combine the flags for automation):
```bash
htb-operator machine start --id 620 --script /tmp/example.sh --start-vpn --update-hosts-file
```

![image](https://github.com/user-attachments/assets/de741502-87af-407d-aa33-a3e856e1d3bd)

In my case, I got a warning because I already had a running VPN conneciton. In general, this warning is for your information and you can ignore it.

## stop
This command stops an active running machine. This operation needs **root/sudo/admin** permission. In Linux, you will be asked for entering your sudo password.   
```bash
htb-operator machine stop
```
![image](https://github.com/user-attachments/assets/29a0a12b-3247-4594-ade6-7f8a4aff9067)

### `--stop-vpn` 
Kills all running HTB-VPN-connection after stopping the machine.
```bash
htb-operator machine stop --stop-vpn
```

### `--clean-hosts-file`
Removes the hostname which matches the machine name from your hosts file. This operation needs **root/sudo/admin** permission. In Linux, you will be asked for entering your sudo password.  
```bash
htb-operator machine stop --clean-hosts-file
```

### Example
You can combine the "stop" flags mentioned above:
```bash
htb-operator machine stop --stop-vpn --clean-hosts-file
```
![image](https://github.com/user-attachments/assets/57216405-e246-4c9c-8552-0bf8b289330e)

## reset
Just reset the active running machine.
```bash
htb-operator machine reset
```
### `--update-hosts-file`
Updates the hosts file, functioning exactly the same way as in `machine start`.
```bash
htb-operator machine reset --update-hosts-file
```

## extend
Extends the expiry time of the machine.
```bash
htb-operator machine extend
```

## status
Returns information about the active running machine.

![image](https://github.com/user-attachments/assets/242ad7e9-95e9-42f1-a0f4-dea5afa8b085)

## info
Displays detailed information about a machine given by the flag `--id` or `--name`.
```bash
htb-operator machine info --id 620
```
![image](https://github.com/user-attachments/assets/d426e72d-b26a-46f8-b30e-2dd9a3d6dbd9)

## submit
Sumbit the flag for the active machine. Use the flag `--user-flag` for submitting the user flag, `--root-flag` for the root flag. You also need to use the flag `-d` for specifying the difficulty rating (from 1="Piece of Cake" to 10="Brainfuck"). 
```bash
htb-operator machine submit --user-flag <FLAG> -d <DIFFICULTY_RATING>
```

## ssh-grab
A ssh connection will be established to the victim host. After that, it tries to grab the flag from `/home/USERNAME/user.txt` (for non-root) or `/root/root.txt` (for root user) and submit it to HTB for the active running machine. You also need to use the flag `-d` for specifying the difficulty rating (from 1="Piece of Cake" to 10="Brainfuck").
```bash
htb-operator machine ssh-grab -u <SSH-USERNAME> -p <SSH-PASSWORD> -i <TARGET_HOST> -d <DIFFICULT_RATING>
```

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


# Prolabs
The prolabs command provides commands for listing all ProLabs as well as getting detailed information about a specific ProLab. 

## list
List all prolabs.
```bash
htb-operator prolabs list
```
![image](https://github.com/user-attachments/assets/9f5a1514-5260-4845-bcc7-5eada511a8b1)

## info 
Get more detailed information about a ProLab which is definied by the `--id` or `--name` flag.
```bash
htb-operator prolabs info --name APTLabs
```
![image](https://github.com/user-attachments/assets/6b751c2e-6572-4020-aaf6-4ca64943462b)

# VPN
**Does not work on Windows**.

You can start and stop a HTB-VPN connection. You can also view the status of the HTB-VPN connection. Furthermore, you can download OpenVPN files or execute a benchmark against all or a subset of VPN-Servers.

## list
List all VPN-Servers. You can filter e.g. for locations or for special VPN servers (e.g. labs, prolabs, and so on). You can combine the flags. Use the help command for more information.
```bash
htb-operator vpn list --location US
```
![image](https://github.com/user-attachments/assets/6344f4cb-c1d1-446d-990f-62979e8cf49d)

## download
You can download a OpenVPN file for the given VPN-Server ID. You can obtain the VPN-Server ID with the `list` subcommand mentioned above. Use the help command for more information.
```bash
htb-operator vpn download --id <ID> --path /tmp/test.ovpn
```
## start
Start a VPN connection with the given VPN server. If the area or "VPN Access" (as per HTB) is not assigned, htb-operator will attempt to switch to the appropriate "VPN Access" after requesting the user's permission. This action needs root/admin permissions.
```bash
htb-operator vpn start --id 35
```
![image](https://github.com/user-attachments/assets/a27beae8-e75a-4fb4-8361-1373cae2ebe2)

## stop
Stops all running HTB-VPN connections. This action needs root/admin permissions.
```bash
htb-operator vpn stop
```
![image](https://github.com/user-attachments/assets/5be9242e-eab3-46b1-8f0e-80f0c73c5583)

## switch
Switch the accessible VPN-Server(s). The target VPN-Server has to be specified using the `--id` flag . 
```bash
htb-operator vpn switch --id 28
```
![image](https://github.com/user-attachments/assets/d34fbafd-9624-48f1-9ac2-df7353275146)

## benchmark
Run a benchmark against all VPN-Servers or a subset of the VPN-Servers. Use the help command for more information to refine your test set. This can take a lot time (depending on your internet connection and the size of your test set).
```bash
htb-operator vpn benchmark --only-accessible
```
![image](https://github.com/user-attachments/assets/70f6fb70-24c7-40fc-a0a4-20d9073fddec)


# Seasons
You can display the results of the current or past seasons using the subcommand `list`. For more details, you can use the subcommand `info`.
```bash
htb-operator seasons list
```
![image](https://github.com/user-attachments/assets/4e1914de-edb6-4566-996e-0e2ec32a7b0f)

## info
The `info` subcommand provides a flag to display only a subset of the seasons using the flag `--ids`. Additionally, it allows viewing results from another user using the flag `--username`. You can combine the flags `--ids` and `--username`.
```bash
htb-operator seasons info --username HTBBot
```
![image](https://github.com/user-attachments/assets/462f93de-122a-450d-85a0-e8d7d16d7aba)


# badge
You can display all badges in HTB using the command `badge` with the subcommand `list`. 
```bash
htb-operator badge list
```
![image](https://github.com/user-attachments/assets/8394d6f5-9613-4c2f-8395-8f1d23052cc0)

You can also filter for "open" badges (i.e. which have not been earned yet) using the flag `--open`. You can also use the flag `--category` for filtering for specific categories. Additionally, you can specify another user if you want to display his earning status using the flag `--username`. You can combine the flags.
```bash
htb-operator badge list --username HTBBot --category Rank,Challenge
```
![image](https://github.com/user-attachments/assets/bd69b590-d161-49a0-8e12-40f445a66a77)


# Pwnbox
If you have a running pwnbox instance, you can get the status of the running pwnbox, establish a ssh connection without knowing the credentials, open the pwnbox desktop in your default browser or terminates a running pwnbox instance. Due to implementation restrictions in HTB, it is not possible to start a new pwnbox instance using htb-operator. 

## status
Read the status of the running pwnbox instance.
```bash
htb-operator pwnbox status
```
![image](https://github.com/user-attachments/assets/d4bceea5-ae14-4083-b5a1-c6bfe76ee2ac)

## ssh
**Does not work on Windows**.

Establishs a SSH connection with the running pwnbox instance. sshpass must be installed on you system.
```bash
htb-operator pwnbox ssh
```
![image](https://github.com/user-attachments/assets/fc197020-c117-4d48-bf7d-4e502c5630a4)

## open
This command opens the Pwnbox Desktop in your default browser.
```bash
htb-operator pwnbox open
```

## terminate
It terminates a running Pwnbox instance.
```bash
htb-operator pwnbox terminate
```
![image](https://github.com/user-attachments/assets/53f6f518-7152-409e-9ae1-096dc2494104)





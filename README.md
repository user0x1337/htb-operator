# HTB-Operator - A CLI for Hack The Box
<img src="https://github.com/user-attachments/assets/7ea918e1-f9d3-4de5-bca7-5bf396bb4f6e" alt="Bild" width="300"/>

![GitHub Tags](https://img.shields.io/github/v/tag/user0x1337/htb-operator)
![GitHub Releases](https://img.shields.io/github/v/release/user0x1337/htb-operator)
![GitHub Repo stars](https://img.shields.io/github/stars/user0x1337/htb-operator)

<div>
  <b>Tests</b><br>
    <img src="https://camo.githubusercontent.com/17b7e1414777604dd31e53667892a72dc70a8671d4a97ed302fe277efee9c8e9/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f74657374732d3130322532307061737365642d73756363657373">
  <br><br>
  <b>OS</b><br>
  <img alt="current version" src="https://img.shields.io/badge/Linux-supported-success"><br>
  <img alt="current version" src="https://img.shields.io/badge/Windows-supported_|_but_not_all_features-lightgreen"><br>
  <img alt="current version" src="https://img.shields.io/badge/MacOS-supported-success">
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

HTB-Operator is developed and maintained by [user0x1337](https://github.com/user0x1337). It interacts with the [Hack The Box](https://www.hackthebox.com/) API, a popular cybersecurity training platform. Its primary goal is to save time when working with HTB.

<img alt="current version" src="https://img.shields.io/badge/Status-Under_Development-red">

# Restrictions on Windows
Windows has platform-specific limitations, so not all features are supported.
Unsupported features/commands:

- VPN start and stop

# Installation
HTB-Operator is written in Python. In general, it can run on any OS with Python installed. It has mainly been tested on Linux (Kali, Ubuntu) and currently has some limitations on Windows.

It is strongly recommended to use a virtual environment. Use [pipx](https://pipx.pypa.io/latest/) (which automatically creates an isolated Python environment) to install `htb-operator`:

```bash
pipx install htb-operator
```

# Configuration
You need an HTB API token:

1. Visit: [https://app.hackthebox.com/account-settings](https://app.hackthebox.com/account-settings)

2. Click **Create App Token**.
<img width="1465" height="181" alt="image" src="https://github.com/user-attachments/assets/99e85feb-020c-4ffb-9f37-54f437d42a78" />

3. Create a token.
<img width="567" height="409" alt="image" src="https://github.com/user-attachments/assets/69d3edbc-b66b-454c-a33f-7ec339177696" />

4. Store the token.
<img width="562" height="389" alt="image" src="https://github.com/user-attachments/assets/78631296-fc5c-4de8-9f7a-df47a20b5482" />

5. Run:

```bash
htb-operator init -api YOUR_API_TOKEN
```

The API token (and other settings) is stored locally at:

- Linux: `$HOME/.config/htb-operator/config.ini`
- Windows: `%APPDATA%\htb-operator\config.ini`

# Commands
The tool is command-based. You can use `-h` or `--help` at any level to display help information. The top-level commands are shown when you run the program without arguments:

```bash
htb-operator
```

![image](https://github.com/user-attachments/assets/fbb1a80a-8005-40bd-86c6-ac3ff32dabf0)

# init
`init` should be the first command you run. As mentioned above, use it to register your API token:

```bash
htb-operator init -api YOUR_API_TOKEN
```

![image](https://github.com/user-attachments/assets/e5f3792b-46a8-4211-82dd-5aea5f516044)

`init` also supports an alternative HTB API URL. Use this only with caution and only if HTB changes the API URL.

# Info
The `info` command retrieves information for a user. If no user is specified, it shows information for the authenticated user.

```bash
htb-operator info
```

### `-s` / `--username`
Using `-s USERNAME` or `--username USERNAME`, you can display the profile of `USERNAME`. Example:

```bash
htb-operator info -s HTBBot
```

![image](https://github.com/user-attachments/assets/8a613234-4dce-4f41-8927-cf004c857cdb)

### `-a` / `--activity`
By default, activity is limited to the most recent 20 entries. Use `-a` or `--activity` to show the full activity history.

```bash
htb-operator info -a
```

`-s` / `--username` also works with this flag:

```bash
htb-operator info -a -s HTBBot
```

![image](https://github.com/user-attachments/assets/addda738-5435-4e66-9058-2efe81ca4a65)

# certificate
You can list or download earned certificates of completion.

### `-l` / `--list`
List all earned certificates of completion:

```bash
htb-operator certificate --list
```

![image](https://github.com/user-attachments/assets/d9fabf5d-cb2a-4663-812a-55cd030ff275)

### download
Using the `download` subcommand, you can download a certificate. With `--id`, specify the certificate ID (for example, from `--list`), and with `-f` / `--filename`, set the target path and filename.

![image](https://github.com/user-attachments/assets/8725d37a-32ea-4d2c-bc23-d90c184cec62)

# machine
The `machine` command provides subcommands to list machines, display details, and start, stop, or reset machines.

## list
Lists active and retired machines. You can add filter flags to optimize the output. See available flags with `htb-operator machine list -h`.

```bash
htb-operator machine list
```

![image](https://github.com/user-attachments/assets/d4ab1f19-d695-448c-816c-62268dc806eb)

Active machines that will be retired soon are marked as `✘/✔`.

### `--limit`
By default, the 20 most recent machines are shown. Use `--limit <NUMBER>` to change that value. Example:

```bash
htb-operator machine list --limit 10
```

![image](https://github.com/user-attachments/assets/a2ad559b-944a-470e-932a-429d8d93e6b3)

### `--retired`
If `--retired` is set, only retired machines are shown.

```bash
htb-operator machine list --retired
```

![image](https://github.com/user-attachments/assets/da96ca5a-ff12-4bff-9edc-57319304f2ed)

### `--active`
If `--active` is set, only active machines are shown.

```bash
htb-operator machine list --active
```

### `--group-by-os`
Changes grouping of the result set. Instead of grouping by `Retired` and `Active`, output is grouped by OS.

```bash
htb-operator machine list --group-by-os
```

![image](https://github.com/user-attachments/assets/1dcfbcde-c640-4281-849c-8e98bc48aa52)

## start
Starts an instance of a machine. If another machine is already running, you will be asked whether to stop it before starting the new one. Specify either `--id` or `--name`.

```bash
htb-operator machine start --id 620
```

![image](https://github.com/user-attachments/assets/6e13bdb3-e755-4a6a-9cee-b08b6884c56a)

### `--start-vpn`
If set, a VPN connection is established automatically based on the configured VPN server. This action requires **root/sudo/admin** permissions. On Linux, you will be prompted for your sudo password.

```bash
htb-operator machine start --id 620 --start-vpn
```

![image](https://github.com/user-attachments/assets/2820fa16-0aa7-49fa-940e-09c0d9a67b38)

### `--update-hosts-file`
If set, the hosts file in `/etc/hosts` (Linux) or `/drivers/etc/hosts` (Windows, not tested) is updated. The machine hostname plus suffix `htb` (for example `HOSTNAME.htb`) and the assigned IP address are added. This action requires **root/sudo/admin** permissions. On Linux, you will be prompted for your sudo password.

```bash
htb-operator machine start --id 620 --update-hosts-file
```

![image](https://github.com/user-attachments/assets/5399d44a-aaa5-4383-97fa-f4e90e00422b)

### `--wait-for-release`
Works only for scheduled machines. Starting is paused until the machine reaches its release date/time and is available to the full community. This is useful if you want to aim for first blood.

```bash
htb-operator machine start --id 620 --wait-for-release
```

### `--script <SCRIPT_FILE>`
Executes a custom Bash script after all prior steps are complete (for example, IP assignment and optional VPN setup). `htb-operator` sets these environment variables:

- `$HTB_MACHINE_IP` -> assigned IP
- `$HTB_MACHINE_NAME` -> machine name (for example `Sea`)
- `$HTB_MACHINE_OS` -> machine OS (`Linux`, `Windows`, `FreeBSD`, ...)
- `$HTB_MACHINE_DIFFICULTY` -> machine difficulty (for example `Easy`)
- `$HTB_MACHINE_INFO` -> information provided by HTB
- `$HTB_MACHINE_HOSTNAME` -> hostname (for example `sea.htb`)

#### Example
Example script:

```bash
#!/usr/bin/bash

echo "Starting script, assigned IP $HTB_MACHINE_IP and hostname $HTB_MACHINE_HOSTNAME"
nmap "$HTB_MACHINE_HOSTNAME" -p 80 --open
```

Command (flags can be combined for automation):

```bash
htb-operator machine start --id 620 --script /tmp/example.sh --start-vpn --update-hosts-file
```

![image](https://github.com/user-attachments/assets/de741502-87af-407d-aa33-a3e856e1d3bd)

In this example, a warning appeared because a VPN connection was already running. This is informational and can usually be ignored.

## stop
Stops the currently active machine. This action requires **root/sudo/admin** permissions. On Linux, you will be prompted for your sudo password.

```bash
htb-operator machine stop
```

![image](https://github.com/user-attachments/assets/29a0a12b-3247-4594-ade6-7f8a4aff9067)

### `--stop-vpn`
Stops all running HTB VPN connections after stopping the machine.

```bash
htb-operator machine stop --stop-vpn
```

### `--clean-hosts-file`
Removes the hostname that matches the machine name from your hosts file. This action requires **root/sudo/admin** permissions. On Linux, you will be prompted for your sudo password.

```bash
htb-operator machine stop --clean-hosts-file
```

### Example
You can combine the `stop` flags shown above:

```bash
htb-operator machine stop --stop-vpn --clean-hosts-file
```

![image](https://github.com/user-attachments/assets/57216405-e246-4c9c-8552-0bf8b289330e)

## reset
Resets the currently active machine.

```bash
htb-operator machine reset
```

### `--update-hosts-file`
Updates the hosts file, working exactly like `machine start --update-hosts-file`.

```bash
htb-operator machine reset --update-hosts-file
```

## extend
Extends the machine expiry time.

```bash
htb-operator machine extend
```

## status
Returns information about the currently active machine.

![image](https://github.com/user-attachments/assets/242ad7e9-95e9-42f1-a0f4-dea5afa8b085)

## info
Displays detailed information about a machine specified via `--id` or `--name`.

```bash
htb-operator machine info --id 620
```

![image](https://github.com/user-attachments/assets/d426e72d-b26a-46f8-b30e-2dd9a3d6dbd9)

## submit
Submits a flag for the active machine. Use `--user-flag` for the user flag and `--root-flag` for the root flag. You also need `-d` to rate difficulty (from `1` = `Piece of Cake` to `10` = `Brainfuck`).

```bash
htb-operator machine submit --user-flag <FLAG> -d <DIFFICULTY_RATING>
```

## ssh-grab
Establishes an SSH connection to the target host. It then attempts to read the flag from `/home/USERNAME/user.txt` (non-root) or `/root/root.txt` (root), and submits it to HTB for the currently active machine. You also need `-d` to provide a difficulty rating (from `1` = `Piece of Cake` to `10` = `Brainfuck`).

```bash
htb-operator machine ssh-grab -u <SSH-USERNAME> -p <SSH-PASSWORD> -i <TARGET_HOST> -d <DIFFICULT_RATING>
```

# challenge
The `challenge` command provides subcommands to list challenges, display details, download files/writeups, start challenge instances, and submit flags. Example: download files, unzip them, and start the instance with one command:

```bash
htb-operator challenge download --name "Hunting License" --unzip -s
```

## search
Use `search` to find challenges that contain the search term. `--name` is required.

```bash
htb-operator challenge search --name Spook
```

![image](https://github.com/user-attachments/assets/420f4564-b3d9-40ba-8ff6-f72ec7c54fe2)

### `--unsolved`
Shows only unsolved challenges. If both `--solved` and `--unsolved` are provided, unsolved challenges are returned.

### `--solved`
Shows only solved challenges. If both `--solved` and `--unsolved` are provided, unsolved challenges are returned.

### `--todo`
Shows only challenges with the `TODO` flag set.

### `--category`
Shows only challenges in the specified category. You can provide multiple categories separated by commas. Example:

```bash
htb-operator challenge search --name Spook --category Web,Crypto,Pwn
```

![image](https://github.com/user-attachments/assets/1475a94a-7017-4101-b742-de0838c77eab)

### `--difficulty`
Shows only challenges that match the specified difficulty.

# Prolabs
The `prolabs` command provides subcommands to list all ProLabs and retrieve details for a specific ProLab.

## list
Lists all ProLabs.

```bash
htb-operator prolabs list
```

![image](https://github.com/user-attachments/assets/9f5a1514-5260-4845-bcc7-5eada511a8b1)

## info
Gets detailed information about a ProLab specified via `--id` or `--name`.

```bash
htb-operator prolabs info --name APTLabs
```

![image](https://github.com/user-attachments/assets/6b751c2e-6572-4020-aaf6-4ca64943462b)

`info` already includes ProLab flags and machines. For focused views, use these dedicated subcommands:

## flags
List only ProLab flags.

```bash
htb-operator prolabs flags --name APTLabs
```

## machines
List only ProLab machines.

```bash
htb-operator prolabs machines --name APTLabs
```

## progress
Show ownership/certificate progress and milestone status.

```bash
htb-operator prolabs progress --name APTLabs
```

## changelog
Show ProLab changelog entries. By default, the latest 20 entries are displayed.

```bash
htb-operator prolabs changelog --name APTLabs --limit 20
```

## reset-status
Show reset status and the timestamp of the last reset (if available).

```bash
htb-operator prolabs reset-status --name APTLabs
```

## submit
Use `submit` to submit ProLab flags. Example:

```bash
htb-operator prolabs submit --name "PROLAB" --flag 'HTB{FAKE_FLAG}'
```

# VPN
**Does not work on Windows.**

You can start and stop HTB VPN connections, view VPN status, download OpenVPN files, and run benchmarks against all or selected VPN servers.

## list
Lists VPN servers. You can filter, for example, by location or server type (labs, prolabs, etc.). Flags can be combined. Use the help command for details.

```bash
htb-operator vpn list --location US
```

![image](https://github.com/user-attachments/assets/6344f4cb-c1d1-446d-990f-62979e8cf49d)

## download
Downloads an OpenVPN file for a given VPN server ID. You can get the ID from the `list` subcommand. Use the help command for details.

```bash
htb-operator vpn download --id <ID> --path /tmp/test.ovpn
```

## start
Starts a VPN connection for the given server. If the area or "VPN Access" (as defined by HTB) is not assigned, `htb-operator` will try to switch to the appropriate "VPN Access" after asking for confirmation. This action requires root/admin permissions.

```bash
htb-operator vpn start --id 35
```

![image](https://github.com/user-attachments/assets/a27beae8-e75a-4fb4-8361-1373cae2ebe2)

## stop
Stops all running HTB VPN connections. This action requires root/admin permissions.

```bash
htb-operator vpn stop
```

![image](https://github.com/user-attachments/assets/5be9242e-eab3-46b1-8f0e-80f0c73c5583)

## switch
Switches accessible VPN server(s). Specify the target server using `--id`.

```bash
htb-operator vpn switch --id 28
```

![image](https://github.com/user-attachments/assets/d34fbafd-9624-48f1-9ac2-df7353275146)

## benchmark
Runs a benchmark against all VPN servers or a selected subset. Use the help command to refine the test set. This may take significant time, depending on your internet connection and the test size.

```bash
htb-operator vpn benchmark --only-accessible
```

![image](https://github.com/user-attachments/assets/70f6fb70-24c7-40fc-a0a4-20d9073fddec)

# Seasons
You can display results for current or past seasons with the `list` subcommand. For more details, use `info`.

```bash
htb-operator seasons list
```

![image](https://github.com/user-attachments/assets/4e1914de-edb6-4566-996e-0e2ec32a7b0f)

## info
The `info` subcommand provides `--ids` to show only selected seasons. It also supports `--username` to view another user's results. You can combine `--ids` and `--username`.

```bash
htb-operator seasons info --username HTBBot
```

![image](https://github.com/user-attachments/assets/462f93de-122a-450d-85a0-e8d7d16d7aba)

# badge
You can display all HTB badges using `badge list`.

```bash
htb-operator badge list
```

![image](https://github.com/user-attachments/assets/8394d6f5-9613-4c2f-8395-8f1d23052cc0)

You can also filter for open badges (not yet earned) with `--open`. Use `--category` to filter by category. You can additionally use `--username` to display another user's badge status. Flags can be combined.

```bash
htb-operator badge list --username HTBBot --category Rank,Challenge
```

![image](https://github.com/user-attachments/assets/bd69b590-d161-49a0-8e12-40f445a66a77)

# Pwnbox
If you have a running Pwnbox instance, you can check status, establish an SSH connection without manually handling credentials, open the Pwnbox desktop in your default browser, or terminate the running instance. Due to HTB implementation restrictions, starting a new Pwnbox instance via `htb-operator` is currently not possible.

## status
Reads the status of the running Pwnbox instance.

```bash
htb-operator pwnbox status
```

![image](https://github.com/user-attachments/assets/d4bceea5-ae14-4083-b5a1-c6bfe76ee2ac)

## ssh
**Does not work on Windows.**

Establishes an SSH connection to the running Pwnbox instance. `sshpass` must be installed on your system.

```bash
htb-operator pwnbox ssh
```

![image](https://github.com/user-attachments/assets/fc197020-c117-4d48-bf7d-4e502c5630a4)

## open
Opens the Pwnbox desktop in your default browser.

```bash
htb-operator pwnbox open
```

## terminate
Terminates the running Pwnbox instance.

```bash
htb-operator pwnbox terminate
```

![image](https://github.com/user-attachments/assets/53f6f518-7152-409e-9ae1-096dc2494104)

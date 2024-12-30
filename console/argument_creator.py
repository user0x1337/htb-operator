import argparse
from argparse import ArgumentParser

from colorama import Fore, Style


# noinspection PyUnresolvedReferences
def create_arg_parser(htb_cli: "HtbCLI") -> ArgumentParser:
    parser: ArgumentParser = argparse.ArgumentParser(prog=f"{htb_cli.package_name}", description=f"{Fore.MAGENTA}CLI tool for HTB operations.{Style.RESET_ALL}")
    subparsers = parser.add_subparsers(title="commands", description="Available commands", dest="command")

    # info command
    _create_info_command_parser(subparsers=subparsers)

    # Certificates command
    _create_certificate_command_parser(subparsers=subparsers)

    # Challenge command
    _create_challenge_command_parser(subparsers=subparsers)

    # machine command
    _create_machine_command_parser(subparsers=subparsers)

    # prolabs command
    _create_prolabs_command_parser(subparsers=subparsers)

    # vhosts command
    _create_vhosts_command_parser(subparsers=subparsers)

    # init command
    _create_init_command_parser(subparsers=subparsers)

    # proxy command
    _create_proxy_command_parser(subparsers=subparsers)

    # version command
    _create_version_command_parser(subparsers=subparsers)

    # check_api_key command
    _create_api_key_command_parser(subparsers=subparsers)

    # Season command
    _create_season_command_parser(subparsers=subparsers)

    # pwnbox command
    _create_pwnbox_command_parser(subparsers=subparsers)

    # VPN command
    _create_vpn_command_parser(subparsers=subparsers)

    # Sherlock command
    _create_sherlock_command_parser(subparsers=subparsers)

    # Badges command
    _create_badge_command_parser(subparsers=subparsers)

    # help command
    subparsers.add_parser("help", help="show this help message and exit")

    return parser

def _create_vhosts_command_parser(subparsers):
    from command import VhostCommand

    vhost_parser: ArgumentParser = subparsers.add_parser("vhost", help="Commands for Vhost")
    vhost_parser.set_defaults(func=VhostCommand)
    vhost_sub_parser = vhost_parser.add_subparsers(title="commands", description="Available commands", dest="vhost")
    vhost_add_sub_parser = vhost_sub_parser.add_parser(name="add", help="Add vhost in hosts file for the active running machine.")
    vhost_add_sub_parser.add_argument("--subdomain", type=str, metavar="<HOSTNAME>", required=True, help="Add <HOSTNAME> to the hosts file. Adding more than one host must be seperated by commas [,]")
    vhost_add_sub_parser.add_argument("--no-machine-hostname", action="store_true" ,help="If indicated, the machine hostname will not be added automatically to the vhost.")
    vhost_sub_parser.add_parser(name="add-hostname", help='Add the hostname of the active running machine (e.g. for the machine "Alert" the hostname "alert.htb" will be added)')


def _create_badge_command_parser(subparsers):
    from command import BadgeCommand

    badge_parser: ArgumentParser = subparsers.add_parser("badge", help="Commands for Badges")
    badge_parser.set_defaults(func=BadgeCommand)
    badge_sub_parser = badge_parser.add_subparsers(title="commands", description="Available commands", dest="badge")
    badge_list_parser = badge_sub_parser.add_parser(name="list", help="List all badges")
    badge_list_parser.add_argument("-s", "--username", type=str, default=None,help="Specify an username. Default is the own user")
    badge_list_parser.add_argument("--open", action="store_true",help="Filter badges which the user has not obtained, yet.")
    badge_list_parser.add_argument("--category", type=str, default=None,help="Filter badges by category. Indicating more than one category must be seperated by commas [,]")


def _create_sherlock_command_parser(subparsers):
    from command import SherlockCommand

    sherlock_parser: ArgumentParser = subparsers.add_parser("sherlock", help="Commands for Sherlock")
    sherlock_parser.set_defaults(func=SherlockCommand)
    sherlock_sub_parser = sherlock_parser.add_subparsers(title="commands", description="Available commands", dest="sherlock")
    sherlock_list_parser = sherlock_sub_parser.add_parser(name="list", help="List all sherlock")
    sherlock_list_parser.add_argument("--active", action="store_true",help="Only active shelocks are displayed")
    sherlock_list_parser.add_argument("--retired", action="store_true", help='Only retired shelocks are displayed. If "--active" is also indicated, "--retired" is ignored')
    sherlock_list_parser.add_argument("--filter-category", type=str, default=None, metavar="<CATEGORY-NAME>", help='Displays only the sherlocks which belongs to the given category. Adding more than one category must be seperated by commas [,]')



def _create_pwnbox_command_parser(subparsers):
    from command import PwnBoxCommand

    pwnbox_parser: ArgumentParser = subparsers.add_parser("pwnbox", help="Commands for Pwnbox")
    pwnbox_parser.set_defaults(func=PwnBoxCommand)
    pwnbox_sub_parser = pwnbox_parser.add_subparsers(title="commands", description="Available commands", dest="pwnbox")
    pwnbox_sub_parser.add_parser(name="status", help="Status of an active running Pwnbox")
    pwnbox_sub_parser.add_parser(name="ssh", help="Connect to pwnbox via SSH")
    pwnbox_sub_parser.add_parser(name="open", help="Open Pwnbox Desktop in your default browser")
    pwnbox_sub_parser.add_parser(name="terminate", help="Terminates the Pwnbox")


def _create_season_command_parser(subparsers):
    from command import SeasonCommand

    seasons_parser: ArgumentParser = subparsers.add_parser("seasons", help="Commands for Seasons")
    seasons_parser.set_defaults(func=SeasonCommand)
    seasons_sub_parser = seasons_parser.add_subparsers(title="commands", description="Available commands", dest="seasons")
    seasons_sub_parser.add_parser(name="list", help="List all Seasons")
    seasons_info_parser = seasons_sub_parser.add_parser(name="info", help="Get detailed information about the seasons for a specific user")
    seasons_info_parser.add_argument("-s", "--username",  metavar="USERNAME", type=str, default=None, help="Specify an username to retrieve their information. Default is the own user")
    seasons_info_parser.add_argument("--ids", type=str, metavar="<ID1,ID2,ID3,...>", default=None,  help='Get the information for the given season id. More IDs must be separated by commas[,]. Default: all seasons')

def _create_prolabs_command_parser(subparsers):
    """Prolabs command"""
    from command import ProlabsCommand

    prolabs_parser: ArgumentParser = subparsers.add_parser("prolabs", help="Commands for Prolabs")
    prolabs_parser.set_defaults(func=ProlabsCommand)
    prolabs_sub_parser = prolabs_parser.add_subparsers(title="commands", description="Available commands", dest="prolabs")
    prolabs_sub_parser.add_parser(name="list", help="List all Prolabs")

    prolab_info_parser = prolabs_sub_parser.add_parser(name="info", help="Get the info for the corresponding Prolab")
    prolab_info_parser.add_argument("--id", type=int, metavar="Prolab ID", help="ID of the Prolab. Either --id or --name must be specified")
    prolab_info_parser.add_argument("--name", type=str, metavar="Prolab Name", help="Name of the Prolab. Either --id or --name must be specified")

    prolabs_submit_flag: ArgumentParser = prolabs_sub_parser.add_parser(name="submit", help="Submit the flag")
    prolabs_submit_flag.add_argument("--id", type=int, metavar="Prolab ID",
                                     help="ID of the Prolab. Either --id or --name must be specified")
    prolabs_submit_flag.add_argument("--name", type=str, metavar="Prolab Name",
                                     help="Name of the Prolab. Either --id or --name must be specified")
    prolabs_submit_flag.add_argument("-fl", "--flag", type=str, metavar="Flag", help="The flag")

def _create_api_key_command_parser(subparsers):
    from command import ApiKey

    api_key_parser: ArgumentParser = subparsers.add_parser("api_key", help="Some api-key configurations")
    api_key_parser.add_argument("--check", action="store_true", help="Check the validity of the stored API-Key.")
    api_key_parser.add_argument("--renew", type=str,
                                help="Stored a new API key. Alter configurations inside the config file are preserved.")
    api_key_parser.set_defaults(func=ApiKey)

def _create_vpn_command_parser(subparsers):
    from command import VpnCommand

    vpn_parser: ArgumentParser = subparsers.add_parser("vpn", help="Commands for OpenVPN in HTB")
    vpn_parser.set_defaults(func=VpnCommand)
    vpn_sub_parser = vpn_parser.add_subparsers(title="commands", description="Available commands", dest="vpn")

    vpn_list_parser = vpn_sub_parser.add_parser(name="list", help="List all VPN Servers")
    vpn_list_parser.add_argument("--labs", action="store_true", help="Lists all labs VPN configurations")
    vpn_list_parser.add_argument("--endgames", action="store_true", help="Lists all endgames VPN configurations")
    vpn_list_parser.add_argument("--fortresses", action="store_true", help="Lists all fortresses VPN configurations")
    vpn_list_parser.add_argument("--release-arena", action="store_true", help="Lists all release-arena VPN configurations")
    vpn_list_parser.add_argument("--starting-point", action="store_true",help="Lists all starting-point VPN configurations")
    vpn_list_parser.add_argument("--prolabs", action="store_true",help="Lists all prolabs VPN configurations")
    vpn_list_parser.add_argument("--only-accessible", action="store_true", help="Lists all current accessible VPN configurations")
    vpn_list_parser.add_argument("--location", type=str, metavar="<Location>", default=None, help="Lists VPN configurations which resides in the given location")
    vpn_list_parser.add_argument("--total-clients", action="store_true", help="Sum ups the total number of clients for the listed VPN servers.")

    vpn_download_parser = vpn_sub_parser.add_parser(name="download", help="Download the OpenVPN-file related to the VPN Server")
    vpn_download_parser.add_argument("--id", type=int, metavar="<ID of VPN Server>", required=True, help="ID of the VPN Server")
    vpn_download_parser.add_argument("--tcp", action="store_true", help="Uses a TCP-connection instead of an UDP-connection for establishing a VPN connection")
    vpn_download_parser.add_argument("--path", type=str, required=True, metavar="PATH", help="Path of file to download including filename")

    vpn_start_parser = vpn_sub_parser.add_parser(name="start", help="Starts a OpenVPN connection for a given VPN-Server. SUDO/Root permissions are required.")
    vpn_start_parser.add_argument("--id", type=int, metavar="<ID of VPN Server>", required=False, help="ID of the VPN Server. If no IP is stated, it will run the VPN specified by the active running machine. If there is no running machine, the command will fail.")
    vpn_start_parser.add_argument("--tcp", action="store_true", help="Uses a TCP-connection instead of an UDP-connection for establishing a VPN connection")
    vpn_start_parser.add_argument("--interface", type=str, default="tun_htb", metavar="<Interface Name>", help='Custom name of the local network interface for the vpn connection. Default: "tun_htb"')

    vpn_sub_parser.add_parser(name="status", help="List all active VPN connections")
    vpn_sub_parser.add_parser(name="stop", help="Stops all active HTB-OpenVPN connection. SUDO/Root permissions are required.")

    vpn_benchmark_parser = vpn_sub_parser.add_parser(name="benchmark", help="Benchmark VPN Servers")
    vpn_benchmark_parser.add_argument("--labs", action="store_true", help="Benchmark all labs VPN servers")
    vpn_benchmark_parser.add_argument("--endgames", action="store_true", help="Benchmark all endgames VPN servers")
    vpn_benchmark_parser.add_argument("--fortresses", action="store_true", help="Benchmark all fortresses VPN servers")
    vpn_benchmark_parser.add_argument("--release-arena", action="store_true", help="Benchmark all release-arena VPN servers")
    vpn_benchmark_parser.add_argument("--starting-point", action="store_true",help="Benchmark all starting-point VPN servers")
    vpn_benchmark_parser.add_argument("--prolabs", action="store_true",help="Benchmark all prolabs VPN servers")
    vpn_benchmark_parser.add_argument("--only-accessible", action="store_true", help="Benchmark all current accessible VPN servers")
    vpn_benchmark_parser.add_argument("--location", type=str, metavar="<Location>", default=None, help="Benchmark VPN servers which resides in the given location")

    vpn_switch_parser = vpn_sub_parser.add_parser(name="switch", help="Switch the VPN Server")
    vpn_switch_parser.add_argument("--id", type=int, metavar="<ID of VPN Server>", required=True, help="ID of the VPN Server")

def _create_version_command_parser(subparsers):
    from command import VersionCommand
    version_parser: ArgumentParser = subparsers.add_parser("version", help="Displays the current version and can check for a new version.")
    version_parser.set_defaults(func=VersionCommand)
    version_parser.add_argument("--check", action="store_true", help="Checks for a new version")


def _create_proxy_command_parser(subparsers):
    from command import ProxyCommand

    proxy_parser: ArgumentParser = subparsers.add_parser("proxy", help="Proxy configuration")
    proxy_parser.add_argument("--http", metavar="HTTP_PROXIES", type=str,
                              help='Specify the http(s) proxy in the form "<http_proxy>,<https_proxy>" seperated by ","')
    proxy_parser.add_argument("--clear", action="store_true", help="Clear the proxies")
    proxy_parser.set_defaults(func=ProxyCommand)


def _create_init_command_parser(subparsers):
    from command import InitCommand

    init_parser: ArgumentParser = subparsers.add_parser("init", help="Initialize the htb-operator")
    init_parser.add_argument("-api", "--apikey", type=str, required=True, help="Specify the API-key.")
    init_parser.add_argument("--apiurl", type=str, default=None, help="(Optional) URL for accessing the HTB API")
    init_parser.set_defaults(func=InitCommand)


def _create_machine_command_parser(subparsers):
    from command import MachineCommand

    def add_id_name_arguments(parser: ArgumentParser):
        parser.add_argument("--name", type=str, metavar="Machine Name", help="Name of the Machine. Either --id or --name must be specified")
        parser.add_argument("--id", type=int, metavar="Machine ID", help="ID of the Machine. Either --id or --name must be specified")

    machine_parser: ArgumentParser = subparsers.add_parser(name="machine", help="Commands for HTB-Machines")
    machine_parser.set_defaults(func=MachineCommand)
    machine_sub_parser = machine_parser.add_subparsers(title="commands", description="Available commands", dest="machine")

    machine_start = machine_sub_parser.add_parser(name="start", help="Start a machine")
    add_id_name_arguments(machine_start)
    machine_start.add_argument("--update-hosts-file", action="store_true", help='The machine\'s hosts will be added to or be updated the hosts file after an IP is assigned. The machine name plus ".htb" is used as hostname. SUDO/Root privileges are required!')
    machine_start.add_argument("--start-vpn", action="store_true", help='Starts a VPN connection that matches the machine being started.')
    machine_start.add_argument("--script", type=str, metavar="<Path to Bash-Script>", default=None, help='Path to the script which will be executed after the starting stage is finished. Keywords will be replaced.')
    machine_start.add_argument("--wait-for-release", action="store_true", help="For scheduled machine: Wait for release date/time and spawn automatically. It's a blocking call")
    machine_start.add_argument("--vhost-hostname", type=str, metavar="<HOSTNAME>", required=False, help="Add <HOSTNAME> to the hosts file. Adding more than one host must be seperated by commas [,]")
    machine_start.add_argument("--vhost-no-machine-hostname", action="store_true", help="If indicated, the machine hostname will not be added automatically to the vhost.")

    maschine_stop_parser = machine_sub_parser.add_parser(name="stop", help="Stop the active machine. If no machine is active, this command will have no effect.")
    maschine_stop_parser.add_argument("--clean-hosts-file", action="store_true", help='The machine\'s hosts will be removed from the hosts file. SUDO/Root privileges are required!')
    maschine_stop_parser.add_argument("--stop-vpn", action="store_true", help='Stops all HTB VPN connection.')
    maschine_reset_parser = machine_sub_parser.add_parser(name="reset", help="Reset the active machine. If no machine is active, this command will have no effect.")
    maschine_reset_parser.add_argument("--update-hosts-file", action="store_true", help='The machine\'s hosts will be added to or be updated the hosts file after an IP is assigned. The machine name plus ".htb" is used as hostname. SUDO/Root privileges are required!')

    machine_sub_parser.add_parser(name="status", help="Displays the active machine(s)")
    machine_sub_parser.add_parser(name="extend",help="Extends the uptime of the active machine")

    machine_info_parser = machine_sub_parser.add_parser(name="info", help="Displays detailed information for a machine")
    add_id_name_arguments(machine_info_parser)

    maschine_list_parser = machine_sub_parser.add_parser(name="list", help="Lists all machines")
    maschine_list_parser.add_argument("--retired", action="store_true", help="Lists only retired machines")
    maschine_list_parser.add_argument("--active", action="store_true", help="Lists only active machines")
    maschine_list_parser.add_argument("--limit", type=int, metavar="<LIMIT>", default=20, help="Lists the recent <LIMIT> machines of each type, separately (active vs. retired). Default: 20")
    maschine_list_parser.add_argument("--search", type=str, metavar="<Keyword>", required=False, default=None, help="Search for machines which contains <KEYWORD> in their names.")
    maschine_list_parser.add_argument("--filter-win", action="store_true", help="Filter machines with Windows OS")
    maschine_list_parser.add_argument("--filter-linux", action="store_true", help="Filter machines with Linux OS")
    maschine_list_parser.add_argument("--filter-freebsd", action="store_true", help="Filter machines with FreeBSD OS")
    maschine_list_parser.add_argument("--filter-openbsd", action="store_true", help="Filter machines with OpenBSD OS")
    maschine_list_parser.add_argument("--filter-other-os", action="store_true", help="Filter machines with other OS")
    maschine_list_parser.add_argument("--group-by-os", action="store_true", help="Groups the results by OS")

    machine_submit_flag: ArgumentParser = machine_sub_parser.add_parser(name="submit", help="Submit the flag to the active machine")
    machine_submit_flag.add_argument("-ufl", "--user-flag", type=str, metavar="Flag", help="The user flag")
    machine_submit_flag.add_argument("-rfl", "--root-flag", type=str, metavar="Flag", help="The root flag")
    machine_submit_flag.add_argument("-d", "--difficulty", type=int, metavar="<Difficulty Rating>",
                                       help='Specify the difficulty rating of obtaining the specific flag (between 1 = "Piece of Cake" and 10 = "Brainfuck")')

    machine_ssh_grab_flag: ArgumentParser = machine_sub_parser.add_parser(name="ssh-grab",help="Grab the flag from the active machine via SSH")
    machine_ssh_grab_flag.add_argument("-u", "--username", type=str, metavar="USERNAME", help="username")
    machine_ssh_grab_flag.add_argument("-p", "--password", type=str, metavar="Password",help="password")
    machine_ssh_grab_flag.add_argument("-i", "--host", type=str, metavar="Host", help="Hostname or IP address")
    machine_ssh_grab_flag.add_argument("-d", "--difficulty", type=int, metavar="<Difficulty Rating>",
                                       help='Specify the difficulty rating of obtaining the specific flag (between 1 = "Piece of Cake" and 10 = "Brainfuck")')


def _create_challenge_command_parser(subparsers):
    from command import ChallengeCommand

    def add_id_name_arguments(parser: ArgumentParser):
        parser.add_argument("--name", type=str, metavar="Challenge Name",help="Name of the challenge. Either --id or --name must be specified")
        parser.add_argument("--id", type=int, metavar="Challenge ID", help="ID of the challenge. Either --id or --name must be specified")

    challenge_parser: ArgumentParser = subparsers.add_parser(name="challenge", help="Commands for HTB-Challenges")
    challenge_parser.set_defaults(func=ChallengeCommand)
    challenge_sub_parser = challenge_parser.add_subparsers(title="commands", description="Available commands",
                                                           dest="challenge")
    challenge_list_parser: ArgumentParser = challenge_sub_parser.add_parser(name="list",
                                                                            help="List all available challenges")
    challenge_list_parser.add_argument("--retired", action="store_true", default=False,
                                       help="only retired challenges are listed")
    challenge_list_parser.add_argument("--unsolved", action="store_true", help="only unsolved challenges are listed")
    challenge_list_parser.add_argument("--solved", action="store_true",
                                       help="only solved challenges are listed. If both --solved and --unsolved are specified, just unsolved will be returned")
    challenge_list_parser.add_argument("--todo", action="store_true", help='only challenges which are marked as "TODO"')
    challenge_list_parser.add_argument("--category", metavar="CATEGORY", type=str, default=None,
                                       help="Filter challenges by category")
    challenge_list_parser.add_argument("--difficulty", metavar="Difficulty", type=str, default=None,
                                       help="Filter challenges by difficulty")

    challenge_info: ArgumentParser = challenge_sub_parser.add_parser(name="info", help="Displays info about a challenge")
    add_id_name_arguments(challenge_info)

    challenge_search: ArgumentParser = challenge_sub_parser.add_parser(name="search", help="Search for challenges")
    challenge_search.add_argument("--name", type=str, metavar="WORD", required=True, help="Search for challenge whose name begins with this word")
    challenge_search.add_argument("--unsolved", action="store_true", help="only unsolved challenges are listed")
    challenge_search.add_argument("--solved", action="store_true",
                                       help="only solved challenges are listed. If both --solved and --unsolved are specified, just unsolved will be returned")
    challenge_search.add_argument("--todo", action="store_true", help='only challenges which are marked as "TODO"')
    challenge_search.add_argument("--category", metavar="CATEGORY", type=str, default=None,
                                       help="Filter challenges by category")
    challenge_search.add_argument("--difficulty", metavar="Difficulty", type=str, default=None,
                                       help="Filter challenges by difficulty")

    challenge_submit_flag: ArgumentParser = challenge_sub_parser.add_parser(name="submit", help="Submit the flag")
    add_id_name_arguments(challenge_submit_flag)
    challenge_submit_flag.add_argument("-d", "--difficulty", type=int, metavar="<Difficulty Rating>",
                                       help='Specify the difficulty rating of the challenge (between 1 = "Piece of Cake" and 10 = "Brainfuck")')
    challenge_submit_flag.add_argument("-fl", "--flag", type=str, metavar="Flag", help="The flag")

    challenge_download: ArgumentParser = challenge_sub_parser.add_parser(name="download", help="Download files from challenge if provided")
    add_id_name_arguments(challenge_download)
    challenge_download.add_argument("-d", "--path", type=str, default=None, metavar="Directory",
                                    help="Directory where the challenge will be downloaded. If no directory is provided, the current working directory will be used."
                                         "If the directory doest not exist, it will be created.")
    challenge_download.add_argument("--unzip", action="store_true",
                                    help="Unzip the downloaded file after downloading in the target directory.")
    challenge_download.add_argument("-s", "--start_instance", action="store_true",
                                    help="Try to start the instance when the download was successful.")
    challenge_instance: ArgumentParser = challenge_sub_parser.add_parser(name="instance",
                                                                         help="Start/Stop instance if provided")
    challenge_instance_sub = challenge_instance.add_subparsers(title="commands", description="Available commands", dest="instance")

    challenge_instance_start = challenge_instance_sub.add_parser(name="start", help="Start an instance")
    add_id_name_arguments(challenge_instance_start)

    challenge_instance_stop = challenge_instance_sub.add_parser(name="stop", help="Stop an instance")
    add_id_name_arguments(challenge_instance_stop)

    challenge_instance_show = challenge_instance_sub.add_parser(name="status", help="Show the instance status")
    add_id_name_arguments(challenge_instance_show)


    challenge_download_writeup: ArgumentParser = challenge_sub_parser.add_parser(name="download_writeup", help="Download writeup from challenge if provided")
    add_id_name_arguments(challenge_download_writeup)
    challenge_download_writeup.add_argument("-d", "--path", type=str, default=None, metavar="Directory",
                                            help="Directory where the writeup will be downloaded. If no directory is provided, the current working directory will be used."
                                                 "If the directory doest not exist, it will be created.")


def _create_certificate_command_parser(subparsers):
    from command import CertificateCommand

    certificate_parser: ArgumentParser = subparsers.add_parser("certificate",
                                                               help="Retrieve obtained certificates of completion")
    certificate_parser.add_argument("-l", "--list", action="store_true", help="List all obtained certificates")
    certificate_parser.set_defaults(func=CertificateCommand)
    certificate_download_parser = (
        certificate_parser.add_subparsers(title="commands", description="Available commands", dest="certificate")
        .add_parser(name="download", help="Download certificate of completion"))
    certificate_download_parser.add_argument("--id", required=True, metavar="Certificate ID", type=int, default=None,
                                             help="Download certificate with the given ID")
    certificate_download_parser.add_argument("-f", "--filename", metavar="FILENAME", default=None, type=str,
                                             help="Filename (without extension) with or without a path specification. Default: Current working directory and certification ID as filename")


def _create_info_command_parser(subparsers):
    from command import InfoCommand

    info_parser: ArgumentParser = subparsers.add_parser("info",
                                                        help="Retrieve information from the active machine or a user.")
    info_parser.add_argument("-s", "--username", type=str, default=None,
                             help="Specify an username to retrieve their information. Default is the own user")
    info_parser.add_argument("-a", "--activity", action="store_true",
                             help="Show only the activity of the user if possible. All entries will be displayed!")
    info_parser.set_defaults(func=InfoCommand)
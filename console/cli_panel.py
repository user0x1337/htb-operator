from datetime import datetime, timedelta, timezone
from typing import List, Optional, Set

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from htbapi import Activity


def format_bool(value, color_true:Optional[str]=None, color_false:Optional[str]=None) -> str:
    """Format boolean value."""
    if type(value) != bool:
        return value

    if value:
        return f"[{color_true}]✔[/{color_true}]" if color_true is not None else "✔"
    else:
        return f"[{color_false}]✘[/{color_false}]" if color_false is not None else "✘"


def create_pwnbox_panel(pwnbox: dict):
    assert pwnbox is not None

    dummy_date = datetime(1, 1, 1) + timedelta(minutes=pwnbox["life_remaining"])
    pwnbox_status = {
        "ID": pwnbox["id"],
        "Hostname": f'{pwnbox["hostname"]}',
        "Username": f'{pwnbox["username"]}',
        "VNC Password": f'{pwnbox["vnc_password"]}',
        "VNC View Only Password": f'{pwnbox["vnc_view_only_password"]}',
        "Spectator URL": f'{pwnbox["spectate_url"]}',
        "Status": f'{pwnbox["status"]}',
        "Ready?": f'{format_bool(pwnbox["is_ready"])}',
        "Location": f'{pwnbox["location"]}',
        "Proxy URL": f'{pwnbox["proxy_url"]}',
        "Instance Lifetime": f'{dummy_date.strftime(f"%H:%M")} [Hours:Minutes]',
        "Expires at": 'Never' if pwnbox["expires_at"] == pwnbox["updated_at"] else f'{pwnbox["expires_at"].isoformat().replace("T", " ").replace("+00:00", "")} UTC',
        "Created at": f'{pwnbox["created_at"].isoformat().replace("T", " ").replace("+00:00", "")} UTC',
        "Updated at": f'{pwnbox["updated_at"].isoformat().replace("T", " ").replace("+00:00", "")} UTC'
    }

    max_key_length = max(len(key) for key in pwnbox_status.keys())
    status_text = "\n".join([f"[bold yellow]{k.ljust(max_key_length)}[/bold yellow] : [bold white]{v}[/bold white]" for k, v in pwnbox_status.items()])


    return Panel(renderable=Text.from_markup(text=status_text, justify="left"),
                 title=f"[bold yellow]Pwnbox Status[/bold yellow]",
                 expand=True,
                 border_style="yellow",
                 title_align="left")

def _create_machine_list_table_header() -> Table:
    table = Table(expand=True, show_lines=False, box=None)

    table.add_column("#", width=1)
    table.add_column("ID", width=1)
    table.add_column("Name", width=10)
    table.add_column("OS", width=6)
    table.add_column("Difficulty", width=4)
    table.add_column("\U00002605 Stars", justify="center", width=3)
    table.add_column("Own User?", justify="center", width=3)
    table.add_column("Own Root?", justify="center", width=3)
    table.add_column("Retired?", justify="center", width=3)
    table.add_column("Release date", max_width=10)

    return table


def _create_machine_list_table_rows(machine_info: List[dict], table: Table, filter_type) -> bool:
    found = False
    for i, m in enumerate([m for m in machine_info if filter_type(m)]):
        found = True

        if "Easy" == m["difficultyText"]:
            color = "bright_green"
        elif "Medium" == m["difficultyText"]:
            color = "bright_yellow"
        elif "Hard" == m["difficultyText"]:
            color = "bright_red"
        elif "Insane" == m["difficultyText"]:
            color = "bright_magenta"
        else:
            color = "bright_white"

        if m["os"].lower() == "windows":
            unicode_logo = "\U0001F5D4  "
        elif m["os"].lower() in ["linux", "freebsd", "openbsd"]:
            unicode_logo = "\U0001F427 "
        elif m["os"].lower() == "android":
            unicode_logo = "\U0001F4F1 "
        else:
            unicode_logo = ""

        retiring: bool = False
        if "retiring" in m and m["retiring"]:
            retiring = True
            retiring_font_begin = "[bold cyan]"
            retiring_font_end = "[/bold cyan]"
        else:
            retiring_font_begin = ""
            retiring_font_end = ""

        table.add_row(f'{retiring_font_begin}{i + 1}{retiring_font_end}',
                      f'{retiring_font_begin}{m["id"]}{retiring_font_end}',
                      f'{retiring_font_begin}[bold {color}]{m["name"]}[/bold {color}]{retiring_font_end}',
                      f'{retiring_font_begin}{unicode_logo}{m["os"]}{retiring_font_end}',
                      f'{retiring_font_begin}[bold {color}]{m["difficultyText"]}[/bold {color}]{retiring_font_end}',
                      f'{retiring_font_begin}{m["stars"]}{retiring_font_end}',
                      f'{retiring_font_begin}{"[bold green]" if m["authUserInUserOwns"] else ""}{format_bool(m["authUserInUserOwns"])}{"[/bold green]" if m["authUserInUserOwns"] else ""}{retiring_font_end}',
                      f'{retiring_font_begin}{"[bold green]" if m["authUserInUserOwns"] else ""}{format_bool(m["authUserInRootOwns"])}{"[/bold green]" if m["authUserInRootOwns"] else ""}{retiring_font_end}',
                      f'{retiring_font_begin}{format_bool(m["retired"])}{f'/{format_bool(True)}' if retiring else ""}{retiring_font_end}',
                      f'{retiring_font_begin}{m["release_date"].strftime("%Y-%m-%d") if m["release_date"] <= datetime.now(tz=timezone.utc) else m["release_date"].strftime("%Y-%m-%d %H:%M:%S UTC")}{retiring_font_end}'
                      )
    return found


def create_machine_list_group_by_os_panel(machine_info: List[dict]) -> Panel | Group | Table:
    """Create the panel for machine list group by OS."""
    assert machine_info is not None

    os_set: Set[str] = set([x["os"] for x in machine_info])

    panels = []
    for os in os_set:
        table = _create_machine_list_table_header()
        filter_type = lambda x: x["os"] == os
        if _create_machine_list_table_rows(table=table, machine_info=machine_info, filter_type=filter_type):
            panels.append(Panel(table,
                                title=f"[bold yellow]{os}[/bold yellow]",
                                border_style="yellow",
                                title_align="left",
                                expand=True))

    return Group(*panels)


def create_sherlock_list_group_by_retired_panel(sherlock_info: List[dict]) -> Panel | Group | Table:
    """Create the panel for sherlock list group by retired/active."""
    assert sherlock_info is not None

    panels = []
    for state_type in ["active", "retired"]:
        table = Table(expand=True, show_lines=False, box=None)

        table.add_column("#", width=1)
        table.add_column("ID", width=1)
        table.add_column("Name", width=10)
        table.add_column("Category", width=6)
        table.add_column("Difficulty", width=4)
        table.add_column("\U00002605 Rating", justify="center", width=3)
        table.add_column("Solved?", justify="center", width=3)
        table.add_column("Progress", justify="center", width=3)
        table.add_column("Release date")

        counter = 0
        for sherlock in sherlock_info:
            if sherlock["state"] != state_type:
                continue
            counter += 1

            if "Easy" == sherlock["difficulty"]:
                color = "bright_green"
            elif "Medium" == sherlock["difficulty"]:
                color = "bright_yellow"
            elif "Hard" == sherlock["difficulty"]:
                color = "bright_red"
            elif "Insane" == sherlock["difficulty"]:
                color = "bright_magenta"
            else:
                color = "bright_white"

            table.add_row(f'{counter}',
                          f'{sherlock["id"]}',
                          f'[bold {color}]{sherlock["name"]}[/bold {color}]',
                          f'{sherlock["category_name"]}',
                          f'[bold {color}]{sherlock["difficulty"]}[/bold {color}]',
                          f'{round(sherlock["rating"], 2)}',
                          f'{format_bool(sherlock["is_owned"], color_true="bold green", color_false="bold red")}',
                          f'{sherlock["progress"]}%',
                          f'{sherlock["release_date"].strftime("%Y-%m-%d")}')

        if counter > 0:
            panels.append(Panel(table,
                                title=f"[bold yellow]{"Retired" if state_type == "retired" else "Active"}[/bold yellow]",
                                border_style="yellow",
                                title_align="left",
                                expand=True))

    return Group(*panels)


def create_machine_list_group_by_retired_panel(machine_info: List[dict]) -> Panel | Group | Table:
    """Create the panel for machine list group by retired/active."""
    assert machine_info is not None

    panels = []
    for machine_type in ["active", "retired", "unreleased"]:
        table = _create_machine_list_table_header()
        filter_type = lambda x: x["retired"] == (machine_type == "retired") and x["release_date"] <= datetime.now(tz=timezone.utc) if machine_type in ["active", "retired"] else x["release_date"] > datetime.now(tz=timezone.utc)
        if _create_machine_list_table_rows(table=table, machine_info=machine_info, filter_type=filter_type):
            panels.append(Panel(table,
                                title=f"[bold yellow]{"Retired" if machine_type == "retired" else "Active" if machine_type == "active" else "Scheduled"}[/bold yellow]",
                                border_style="yellow",
                                title_align="left",
                                expand=True))

    return Group(*panels)


def create_prolab_detail_info_panel(prolab_dict: dict) -> Panel | Group | Table:
    assert prolab_dict is not None

    # Basic info
    basic_info = {
        "Name": prolab_dict["name"],
        "ID": prolab_dict["id"],
        "Version": prolab_dict["version"],
        "Release Date": prolab_dict["release_date"].strftime("%Y-%m-%d"),
        "Payment status": prolab_dict["state"],
        "Mini?": format_bool(prolab_dict["mini"]),
        "Identifier": prolab_dict["identifier"],
        "# Machines": prolab_dict["machines_count"],
        "# Flags": prolab_dict["flags_count"],
        "Entry Point(s)": ",".join(prolab_dict["entry_points"]),
        "Active Users": prolab_dict["active_users"],
        "Lab masters": ",".join([x["name"] for x in prolab_dict["lab_masters"]]),
        "Writeup Available": format_bool(prolab_dict["writeup_filename"] is not None),
        "Difficulty": prolab_dict["skill_level"].capitalize(),
        "Category Level": f'{prolab_dict["designated_category"]}',
        "Level": f'{prolab_dict["level"]}',
        "Team (Red/Blue/Purple)": prolab_dict["team"].capitalize(),
        "Ownership": f'{prolab_dict["ownership"]} %',
        "Eligible for Certificate": format_bool(prolab_dict["user_eligible_for_certificate"]),
    }

    # Flags
    flags_table = Table(expand=True, show_lines=False, box=None)
    flags_table.add_column("Name", max_width=10)
    flags_table.add_column("Points", width=1)
    flags_table.add_column("Owned?", width=1)
    for flag in prolab_dict["flags"]:
        color_first = "[bold green]" if flag["owned"] else ""
        color_last = "[/bold green]" if flag["owned"] else ""
        flags_table.add_row(flag["title"], f'{flag["points"]}', f'{color_first}{format_bool(flag["owned"])}{color_last}')

    # Machines
    machines_table = Table(expand=True, show_lines=False, box=None)
    machines_table.add_column("ID", max_width=0)
    machines_table.add_column("Name", max_width=8)
    machines_table.add_column("OS", max_width=10)
    for machine in prolab_dict["machines"]:
        if machine["os"].lower() == "windows":
            unicode_logo = "\U0001F5D4  "
        elif machine["os"].lower() in ["linux", "freebsd", "openbsd"]:
            unicode_logo = "\U0001F427 "
        elif machine["os"].lower() == "android":
            unicode_logo = "\U0001F4F1 "
        else:
            unicode_logo = ""

        machines_table.add_row(f'{machine["id"]}', machine["name"], f'{unicode_logo} {machine["os"]}')

    # Adjust table
    max_rows = max(len(prolab_dict["flags"]), len(basic_info.keys()), len(prolab_dict["machines"]))
    for i in range(len(prolab_dict["flags"]), max_rows):
        flags_table.add_row()

    for i in range(len(prolab_dict["machines"]), max_rows):
        machines_table.add_row()

    p_basic = _create_custom_panel(custom_dict=basic_info, panel_title="Basic info", target_height=max_rows + 1)
    p_flags = Panel(flags_table,
                    title=f"[bold yellow]Flags[/bold yellow]",
                    border_style="yellow",
                    title_align="left",
                    expand=True,
                    width=100)
    p_machines = Panel(machines_table,
                       title=f"[bold yellow]Machines[/bold yellow]",
                       border_style="yellow",
                       title_align="left",
                       expand=True,
                       width=60)

    table = Table.grid(expand=True)
    table.add_column()
    table.add_column()
    table.add_row(p_basic, p_flags, p_machines)

    return table

def _create_custom_panel(custom_dict: dict, panel_title: str, value_color_format: str | None = "bold cyan", target_height: int = -1) -> Panel:
    """Internal function for creating a panel"""
    assert custom_dict is not None
    assert len(custom_dict.keys()) > 0

    if value_color_format is None:
        begin_value_format = ""
        end_value_format = ""
    else:
        begin_value_format = f"[{value_color_format}]"
        end_value_format = f"[/{value_color_format}]"

    max_key_length = max(len(key) for key in custom_dict.keys())
    profile_text = "\n".join([f"[bold white]{key.ljust(max_key_length)}[/bold white] : {begin_value_format}{format_bool(value)}{end_value_format}"
                              for key, value in custom_dict.items()])

    # Normalize height if requested
    if target_height > 0:
        lines = profile_text.split("\n")
        padding_lines = target_height - len(lines)
        if padding_lines > 0:
            lines.extend([""] * padding_lines)
        profile_text = "\n".join(lines)

    return Panel(renderable=Text.from_markup(text=profile_text, justify="left"),
                 title=f"[bold yellow]{panel_title}[/bold yellow]",
                 expand=True,
                 border_style="yellow",
                 title_align="left")

def create_prolab_info_panel_text(prolab: dict) -> str:
    """Create the text for a panel"""
    panel_dict = {
        "Name": prolab["name"],
        "ID": prolab["id"],
        "Version": prolab["version"],
      #  "Description": BeautifulSoup(prolab["description"], "html.parser").get_text(),
        "Entry Points": ", ".join(prolab["entry_points"]),
        "Released at": prolab["release_date"].strftime("%Y-%m-%d"),
        "# Machines": prolab["machines_count"],
        "# Active users": prolab["active_users"],
        "# Flags": prolab["flags_count"],
        "Level": prolab["level"],
        "Skill Level": prolab["skill_level"].capitalize(),
        "Mini?": format_bool(prolab["mini"]),
        "Eligible for Certificate": format_bool(prolab["user_eligible_for_certificate"]),
        "New?": format_bool(prolab["new"]),
        "Category": prolab["designated_category"],
        "Completed [%]": prolab["ownership"],
        "State": prolab["state"].capitalize(),
        "Discord": prolab["discord_url"],
        "Lab masters": ",".join([x["name"] for x in prolab["lab_masters"]]),
    }

    max_key_length = max(len(key) for key in panel_dict.keys())
    text = "\n".join([f"[bold yellow]{k.ljust(max_key_length)}[/bold yellow] : [bold white]{v}[/bold white]"
                      for k,v in panel_dict.items()])

    return text


def create_challenge_info_panel(channel_info: dict) -> Table:
    basic = {
        "ID": channel_info["id"],
        "Name": channel_info["name"],
        "Retired": format_bool(channel_info["retired"]),
        "Difficulty": channel_info["difficulty"],
        "Category": channel_info["category_name"],
        "Points": f"{channel_info["points"]}",
        "Solves": f"{channel_info["solves"]}",
        "Likes": f"{channel_info["likes"]}",
        "Dislikes": f"{channel_info["dislikes"]}",
        "Release Date": channel_info["release_date"].strftime("%Y-%m-%d"),
        "Solved": format_bool(channel_info["solved"]),
        "Solved after": "-" if channel_info["authUserSolveTime"] is None else channel_info["authUserSolveTime"],
        "TODO": format_bool(channel_info["isTodo"]),
        "Recommended": format_bool(channel_info["recommended"] == 1)
    }

    max_key_length = max(len(key) for key in basic.keys())
    text_basic = "\n".join([
        f"[bold yellow]{k.ljust(max_key_length)}[/bold yellow] : [bold bright_green]{v}[/bold bright_green]" if k == "Difficulty" and "Easy" in v
        else f"[bold yellow]{k.ljust(max_key_length)}[/bold yellow] : [bold bright_yellow]{v}[/bold bright_yellow]" if k == "Difficulty" and "Medium" in v
        else f"[bold yellow]{k.ljust(max_key_length)}[/bold yellow] : [bold bright_red]{v}[/bold bright_red]" if k == "Difficulty" and "Hard" in v
        else f"[bold yellow]{k.ljust(max_key_length)}[/bold yellow] : [bold bright_magenta]{v}[/bold bright_magenta]" if k == "Difficulty" and "Insane" in v
        else f"[bold yellow]{k.ljust(max_key_length)}[/bold yellow] : [bold white]{v}[/bold white]"
        for k,v in basic.items()])

    basic_2 = {
        "Description": channel_info["description"],
        "First Blood User": "-" if channel_info["first_blood_user"] is None else f"{channel_info["first_blood_user"]} (ID: {channel_info["first_blood_user_id"]})",
        "First Blood Time": "-" if channel_info["first_blood_time"] is None else channel_info["first_blood_time"],
        "Author(s)": f"{channel_info["creator_name"]} (ID: {channel_info["creator_id"]})" + ("" if channel_info["creator2_name"] is None else f"{channel_info["creator2_name"]} (ID: {channel_info["creator2_id"]})"),
        "Downloadable": format_bool(channel_info["download"]),
        "Download Hash": "-" if not channel_info["download"] else channel_info["download_sha256"],
        "Has Instance": format_bool(channel_info["docker"]),
        "Instance IP": "-" if channel_info["docker_ip"] is None else channel_info["docker_ip"],
        "Instance Ports": "-" if channel_info["docker_ports"] is None or len(channel_info["docker_ports"]) == 0
                              else ",".join(str(x) for x in channel_info["docker_ports"]),
        "Released": format_bool(channel_info["released"] == 1),
        "Already Reviewed": format_bool(channel_info["hasReviewed"]),
        "Can review?": format_bool(channel_info["canReview"]),
        "Writeup provided?": format_bool(channel_info["writeup_provided"])

    }

    max_key_length = max(len(key) for key in basic_2.keys())
    text = "\n".join([f"[bold yellow]{k.ljust(max_key_length)}[/bold yellow] : [bold white]{v}[/bold white]"
                      for k,v in basic_2.items()])

    p_basic = Panel(renderable=Text.from_markup(text=text_basic, justify="left"),
                    title=f"[bold yellow]Basic Information[/bold yellow]",
                    expand=True,
                    border_style="yellow",
                    title_align="left")

    p = Panel(renderable=Text.from_markup(text=text, justify="left"),
              title=f"[bold yellow]Detail Information[/bold yellow]",
              expand=True,
              border_style="yellow",
              title_align="left")


    table = Table.grid(expand=True)
    table.add_column()
    table.add_column()
    table.add_row(p_basic, p)

    return table


def create_season_panel(season_dict: dict):
    assert season_dict is not None

    custom_dict = {
        "ID": season_dict["season_id"],
        "Name": season_dict["name"],
        "Start date": season_dict["start_date"],
        "Ende date": season_dict["end_date"],
        "Rank Tier": season_dict["tier"],
        "Username": season_dict["user_name"],
        "Rank": season_dict["current_rank"],
        "Total Players": season_dict["total_ranks"],
        "User Flags": season_dict["user_flags_pawned"],
        "User Bloods": season_dict["user_bloods_pawned"],
        "Root Flags": season_dict["root_flags_pawned"],
        "Root Bloods": season_dict["root_bloods_pawned"],
        "Total machines": season_dict["total_machines"]
    }

    return _create_custom_panel(custom_dict=custom_dict, panel_title=season_dict["name"])



def create_profile_panel(user_dict: dict) -> Panel:
    """Create a panel with profil information"""
    assert user_dict is not None
    assert len(user_dict.keys()) > 0

    profile_dict = {k: v["Name"] if k in ["Team", "University"] else v for k, v in user_dict.items()}
    return _create_custom_panel(custom_dict=profile_dict, panel_title="Profile")


def create_ranking_panel(ranking_dict: dict) -> Panel:
    """Create a panel with ranking information"""
    assert ranking_dict is not None
    assert len(ranking_dict.keys()) > 0

    if ranking_dict["Rank Requirement"] is None:
        ranking_dict["Rank Requirement"] = "-"
    else:
        ranking_dict["Rank Requirement"] = f"{ranking_dict["Rank Requirement"]}%"

    # Ranking brackets are optional
    if ranking_dict["Ranking_Bracket"] is not None:
        ranking_dict["Points"] = f'{ranking_dict["Points"]} ({ranking_dict["Ranking_Bracket"]["Points_Next_Bracket"]} pts needed for {ranking_dict["Ranking_Bracket"]["Next_Bracket"]})'

    ranking_dict = {
        "Rank": ranking_dict["Rank"],
        "Ranking": ranking_dict["Ranking"],
        "Points": ranking_dict["Points"],
        "Team": ranking_dict["Team"]["Rank"],
        "University": ranking_dict["University"]["Rank"],
        "Ownership": f'{ranking_dict["Ownership"]}% / {ranking_dict["Rank Requirement"]}',
    }

    return _create_custom_panel(custom_dict=ranking_dict, panel_title="Ranking Information")


def create_misc_panel(misc_dict: dict) -> Panel:
    """Create a panel with misc information"""
    assert misc_dict is not None
    assert len(misc_dict.keys()) > 0

    return _create_custom_panel(custom_dict=misc_dict, panel_title="Misc")


def create_advanced_labs_panel(advanced_list: List, title: str, target_height: int = -1) -> Panel:
    assert advanced_list is not None
    assert len(advanced_list) > 0

    profile_advanced_lab = {}
    for lab in advanced_list:
        value_format = "bold bright_yellow" if lab.total_flags > lab.owned_flags > 0 else "bold bright_red" if lab.owned_flags == 0 else "bold bright_green"

        profile_advanced_lab[lab.name] = f"[{value_format}]{lab.owned_flags} / {lab.total_flags}\t({lab.completion_percentage}%)[/{value_format}]"

    return _create_custom_panel(custom_dict=profile_advanced_lab,
                                panel_title=title,
                                value_color_format=None,
                                target_height=target_height)


def create_activity_panel(activity_list: List[Activity], limit_activity_entries: Optional[int]=20) -> Panel:
    """Create a panel with activity information"""
    assert activity_list is not None
    assert len(activity_list) > 0

    # sort list of dicts
    activity_list = sorted(activity_list, key=lambda activity: activity.date, reverse=True)


    # Only the recent 20 entries
    if limit_activity_entries is not None and len(activity_list) > limit_activity_entries:
        activity_list = activity_list[:limit_activity_entries]

    max_date_diff_length = max(len(activity.date_diff) for activity in activity_list)
    max_type_length = max(len(f"{activity.flag_title + " " if activity.object_type == "endgame" 
                                else activity.challenge_category + " " if activity.object_type == "challenge" 
                                else activity.object_type + " " if activity.object_type == "machine"
                                else ""}"
                              f"{activity.type}") for activity in activity_list)
    max_name_length = max(len(activity.name) for activity in activity_list)

    text = "\n".join([f"[bold yellow]{activity.date_diff.ljust(max_date_diff_length)} | "
                      f"Owned {(activity.flag_title + " " + activity.type).ljust(max_type_length) if activity.object_type == "endgame" 
                      else (activity.challenge_category + " " + activity.type).ljust(max_type_length) if activity.object_type == "challenge" 
                      else (activity.object_type + " " + activity.type).ljust(max_type_length) if activity.object_type == "machine" 
                      else activity.type.ljust(max_type_length)} [/bold yellow] - {activity.name.ljust(max_name_length)} | "
                      f"[bold white] +[{activity.points} pts] [/bold white]" for activity in activity_list])
    p = Panel(renderable=Text.from_markup(text=text, justify="left"),
              title=f"[bold yellow]Activity[/bold yellow]",
              expand=True,
              border_style="yellow",
              title_align="left")

    return p


def create_panel_active_machine_status(active_machine: dict) -> Table | Panel:
    """Create active machine status panel"""

    if active_machine["os"].lower() == "windows":
        unicode_logo = "\U0001F5D4  "
    elif active_machine["os"].lower() in ["linux", "freebsd", "openbsd"]:
        unicode_logo = "\U0001F427 "
    elif active_machine["os"].lower() == "android":
        unicode_logo = "\U0001F4F1 "
    else:
        unicode_logo = ""
    if "Easy" == active_machine["difficulty"]:
        color = "bright_green"
    elif "Medium" == active_machine["difficulty"]:
        color = "bright_yellow"
    elif "Hard" == active_machine["difficulty"]:
        color = "bright_red"
    elif "Insane" == active_machine["difficulty"]:
        color = "bright_magenta"
    else:
        color = "bright_white"

    expires_at: datetime = active_machine["expires_at"].replace(tzinfo=timezone.utc)
    time_left: datetime = datetime(1, 1, 1, tzinfo=timezone.utc) + (expires_at - datetime.now(tz=timezone.utc))
    panel_dict_text = {
        "Machine ID": f'{active_machine["id"]}',
        "Name": f'{active_machine["name"]}',
        "IP": f'{active_machine["ip"]}',
        "Expires at": f'{expires_at.strftime("%Y-%m-%d %H:%M:%S")} UTC ({time_left.strftime(f"%H:%M:%S")} left)',
        "Retired?": f'{format_bool(active_machine["retired"])}',
        "OS": f'{unicode_logo}{active_machine["os"]}',
        "Info": f'{'-' if active_machine["info_status"] is None else active_machine["info_status"]}',
        "Points": f'{active_machine["points"]}',
        "User owned?": f'{format_bool(active_machine["user_owned"], color_true="green", color_false="red")}',
        "Root owned?": f'{format_bool(active_machine["root_owned"], color_true="green", color_false="red")}',
        "Difficulty": f'[{color}]{active_machine["difficulty"]}[/{color}]',
        "VPN-Server": f'{format_bool(active_machine["vpn_server"])} (ID: {active_machine["vpn_server_id"]})',
        "# Players": f'{format_bool(active_machine["num_players"])}',
        "# Solved": f'{active_machine["num_solved"]}',
        "Entries in hosts-file": f'{", ".join(active_machine["hosts_file_name"].split("\n"))}'
    }

    return _create_custom_panel(custom_dict=panel_dict_text, panel_title="Active Machine", value_color_format="white")


import os
import time
from typing import Optional, List, cast, Tuple

from .exception.errors import RequestException, NoPwnBoxActiveException

# noinspection PyUnresolvedReferences
_vpn_server_cache = dict()
# noinspection PyUnresolvedReferences
_user_cache: dict[int, "User"] = dict()

class HTBClient:
    # noinspection PyUnresolvedReferences
    htb_http_request: "BaseHtbHttpRequest"

    # noinspection PyUnresolvedReferences
    def __init__(self,htb_http_request: "BaseHtbHttpRequest") -> None:
        assert htb_http_request is not None
        self.htb_http_request = htb_http_request

    # noinspection PyUnresolvedReferences
    def get_user(self, username: Optional[str]=None, user_id: Optional[int]=None) -> "User":
        from .user import User
        global _user_cache

        if user_id in _user_cache.keys():
            return _user_cache[user_id]

        if user_id is None:
            if username is None:
                data:dict = self.htb_http_request.get_request(endpoint="user/info")["info"]
                user_id: int = int(data["id"])

            else:
                data = self.htb_http_request.get_request(endpoint=f'search/fetch?query="{username}"')
                if len(data) == 0 or "users" not in data.keys():
                    return None
                user_id = data["users"][0]["id"]

        data = self.htb_http_request.get_request(endpoint=f"user/profile/basic/{user_id}")["profile"]

        # Ranking brackets are only provided for own (authenticated) user. If username is None, we will definitely retrieve
        # the information for the own user.
        ranking_bracket = self.get_user_ranking() if username is None else None

        user: User = User(_client=self, data=data, ranking_bracket=ranking_bracket)
        _user_cache[user_id] = user
        return user

    # noinspection PyUnresolvedReferences
    def search_challenges(self, name: str,
                          unsolved: Optional[bool] = None,
                          filter_todo: Optional[bool] = False,
                          filter_category_list: Optional[List[int]] = None,
                          filter_difficulty: Optional[str] = None) -> List["ChallengeList"]:
        """Search for challenges for a given name."""
        from .challenge import ChallengeList

        data: List = self.htb_http_request.get_request(endpoint=f'challenges?keyword={name}&sort_type=asc')["data"]
        if len(data) == 0:
            return []

        return [ChallengeList(_client=self, data={"id": d["id"],
                                                  "name": d["name"],
                                                  "retired": d["state"] == "retired",
                                                  "difficulty": d["difficulty"],
                                                  "solves": d["solves"],
                                                  "release_date": d["release_date"],
                                                  "challenge_category_id": d["category_id"],
                                                  "rating": d["rating"],
                                                  "avg_difficulty": d["user_difficulty"],
                                                  "authUserSolve": d["is_owned"]
                                                  }) for d in data
                if unsolved is None and d["is_owned"] == d["is_owned"] or d["is_owned"] != unsolved
                if filter_todo is None or not filter_todo or (d["isTodo"] == filter_todo)
                if filter_category_list is None or len(filter_category_list) == 0 or (
                            d["category_id"] in filter_category_list)
                if filter_difficulty is None or (d["difficulty"].lower() == filter_difficulty.lower())
                ]


    # noinspection PyUnresolvedReferences
    def get_user_ranking(self) -> "UserRankingHoF":
        """Get the ranking of the own (authenticated) user."""
        from .user import UserRankingHoF

        data = self.htb_http_request.get_request(endpoint=f"rankings/user/ranking_bracket")["data"]
        return UserRankingHoF(data=data, _client=self)


    # noinspection PyUnresolvedReferences
    def get_prolab_certificate_list(self) -> List["Certificate"]:
        from .certificate import Certificate

        data: dict = self.htb_http_request.get_request(endpoint=f"user/profile/certificates")
        if data is None or len(data.keys()) == 0 or "ownedProLab" not in data.keys():
            return []

        return [Certificate(_client=self, data=d) for d in data["ownedProLab"]]

    def download_prolab_certificate(self, certificate_id: int, path: str|None = None) -> str:
        """Download prolab certification and returns the file path"""
        assert certificate_id is not None and certificate_id > 0

        try:
            data = self.htb_http_request.get_request(endpoint=f"certificate/{certificate_id}/download", download=True)
        except RequestException as e:

            if not e.args or len(e.args) == 0 or "message" not in e.args[0].keys():
                raise RequestException(f"Could not download prolab certificate {certificate_id}")
            msg = e.args[0]["message"]
            if "unauthorized" in msg:
                raise RequestException(f"Could not download prolab certificate {certificate_id}: You are not authorized.")
            elif "Not Found" in msg:
                raise RequestException(f"Could not download prolab certificate {certificate_id}: Certificate not found.")
            else:
                raise e

        if path is None:
            path = os.path.join(os.getcwd(), f"{certificate_id}.pdf")
        elif not path.endswith(".pdf"):
            path += ".pdf"

        data = cast(bytes, data)
        with open(path, "wb") as f:
            f.write(data)

        return path

    # noinspection PyUnresolvedReferences
    def get_pwnbox_usage(self) -> "PwnboxUsage":
        """Get the usage of the Pwnbox instance for the auth user"""
        from .pwnbox import PwnboxUsage

        data:dict = self.htb_http_request.get_request(endpoint=f"pwnbox/usage")["data"]
        return PwnboxUsage(_client=self, data=data)

    # noinspection PyUnresolvedReferences
    def get_pwnbox_status(self) -> "PwnboxStatus":
        """Get the current pwnbox status."""
        from .pwnbox import PwnboxStatus

        data: dict = self.htb_http_request.get_request(endpoint=f"pwnbox/status")
        if data is not None and "message" in data.keys():
            raise NoPwnBoxActiveException(data["message"])

        if data is None:
            return None

        return PwnboxStatus(_client=self, data=data["data"])

    # noinspection PyUnresolvedReferences
    def get_season_details(self, user_id: int, season_id: int) -> Optional["SeasonUserDetails"]:
        """Get the season rank details for a given user."""
        from .season import SeasonUserDetails

        data = self.htb_http_request.get_request(endpoint=f"season/end/{season_id}/{user_id}")["data"]
        if data is None or len(data) == 0:
            return None

        data = cast(dict, data)
        return SeasonUserDetails(_client=self, data=data)

    def get_season_leaderboard_top_x(self, season_id: int, top_number:int) -> List["SeasonLeaderboardUserPosition"]:
        pass # top_number must be between 3 <= x <= 100
        # API: season/players/leaderboard/top/6?number=100

    # noinspection PyUnresolvedReferences
    def get_season_list(self) -> List["SeasonList"]:
        """Get the list of seasons"""
        from .season import SeasonList

        data: list = self.htb_http_request.get_request(endpoint=f"season/list")["data"]

        return [SeasonList(data=x, _client=self) for x in data]

    # noinspection PyUnresolvedReferences
    def get_challenge_list(self,
                           retired:bool = False,
                           unsolved: Optional[bool] = None,
                           filter_todo: Optional[bool] = False,
                           filter_category_list: Optional[List[int]] = None,
                           filter_difficulty: Optional[str] = None) -> List["ChallengeList"]:
        """Get a list of challenges

        :argument
            - retired: If true, return retired challenges
            - unsolved: If true, return unsolved challenges, if false, return solved challenges. If none, both are returned.
            - filter_todo: If true, return only challenges which are marked as "isTODO"
        :returns:
            List of challenges
        """
        from .challenge import ChallengeList

        if retired:
            data: list = self.htb_http_request.get_request(endpoint=f"challenge/list/retired")["challenges"]
        else:
            data: list = self.htb_http_request.get_request(endpoint=f"challenge/list")["challenges"]

        return [ChallengeList(_client=self, data=d) for d in data
                if unsolved is None and d["authUserSolve"] == d["authUserSolve"] or d["authUserSolve"] != unsolved
                if filter_todo is None or not filter_todo or (d["isTodo"] == filter_todo)
                if filter_category_list is None or len(filter_category_list) == 0 or (d["challenge_category_id"] in filter_category_list)
                if filter_difficulty is None or (d["difficulty"].lower() == filter_difficulty.lower())]

    # noinspection PyUnresolvedReferences
    def get_challenge_categories_list(self) -> List["Category"]:
        from .challenge import Category
        data: list = self.htb_http_request.get_request(endpoint=f"challenge/categories/list")["info"]

        return [Category(_client=self, data=x) for x in data]

    # noinspection PyUnresolvedReferences
    def get_prolab_progress_profile_summary(self, user_id: int) -> List["ProLabUserProfile"]:
        assert user_id is not None
        from .prolab import ProLabUserProfile

        data: dict = self.htb_http_request.get_request(endpoint=f"user/profile/progress/prolab/{user_id}")["profile"]
        return [ProLabUserProfile(_client=self, data=x) for x in data["prolabs"]]

    # noinspection PyUnresolvedReferences
    def get_endgame_progress_profile_summary(self, user_id: int) -> List["EndgameUserProfile"]:

        assert user_id is not None

        from .endgame import EndgameUserProfile

        data: dict = self.htb_http_request.get_request(endpoint=f"user/profile/progress/endgame/{user_id}")["profile"]
        return [EndgameUserProfile(_client=self, data=x) for x in data["endgames"]]

    # noinspection PyUnresolvedReferences
    def get_fortress_progress_profile_summary(self, user_id: int) -> List["FortressUserProfile"]:

        assert user_id is not None

        from .fortress import FortressUserProfile

        data: dict = self.htb_http_request.get_request(endpoint=f"user/profile/progress/fortress/{user_id}")["profile"]
        return [FortressUserProfile(_client=self, data=x) for x in data["fortresses"]]

    # noinspection PyUnresolvedReferences
    def get_sherlock_progress_profile_summary(self, user_id: int) -> List["SherlockUserProfile"]:
        assert user_id is not None
        from .sherlock import SherlockUserProfile

        data: dict = self.htb_http_request.get_request(endpoint=f"user/profile/progress/sherlocks/{user_id}")["profile"]
        return [SherlockUserProfile(_client=self, data=x) for x in data["challenge_categories"]]

    # noinspection PyUnresolvedReferences
    def get_sherlock_categories(self) -> List["SherlockCategory"]:
        """Get a list of sherlock categories"""
        from .sherlock import SherlockCategory
        data: list = self.htb_http_request.get_request(endpoint=f"sherlocks/categories/list")["info"]

        return [SherlockCategory(_client=self, data=x) for x in data]

    # noinspection PyUnresolvedReferences
    def get_sherlocks(self,
                      only_active: Optional[bool]=None,
                      only_retired: Optional[bool]=None,
                      filter_sherlock_category: Optional[List["SherlockCategory"]]=None) -> List["SherlockInfo"]:
        """Get a list of sherlock information"""
        from .sherlock import SherlockInfo

        if only_active:
            state = "&state=active"
        elif only_retired:
            state = "&state=retired"
        else:
            state = ""

        if filter_sherlock_category is not None and len(filter_sherlock_category) > 0:
            categories = f'&category[]={'&category[]='.join([str(x.id) for x in filter_sherlock_category])}'
        else:
            categories = ""

        page_no: int = 1
        sherlock_result: List["SherlockInfo"] = []
        while True:
            res: dict = self.htb_http_request.get_request(endpoint=f"sherlocks?page={page_no}{state}{categories}")

            if res is None or len(res.keys()) == 0:
                break
            if "data" not in res:
                break

            data:List[dict] = res["data"]
            if data is None or len(data) == 0:
                break

            sherlock_result += [SherlockInfo(_client=self, data=x) for x in data]

            last_page = res["meta"]["last_page"]
            if page_no >= last_page:
                break

            page_no += 1

        return sherlock_result

    # noinspection PyUnresolvedReferences
    def get_machine_progress_profile_summary(self, user_id: int) -> List["MachineOsUserProfile"]:
        assert user_id is not None
        from .machine import MachineOsUserProfile

        data: dict = self.htb_http_request.get_request(endpoint=f"user/profile/progress/machines/os/{user_id}")["profile"]
        return [MachineOsUserProfile(_client=self, data=x) for x in data["operating_systems"]]

    # noinspection PyUnresolvedReferences
    def get_challenge_progress_profile_summary(self, user_id: int) -> List["ChallengeUserProfile"]:
        assert user_id is not None
        from .challenge import ChallengeUserProfile

        data: dict = self.htb_http_request.get_request(endpoint=f"user/profile/progress/challenges/{user_id}")["profile"]
        return [ChallengeUserProfile(_client=self, data=x) for x in data["challenge_categories"]]

    # noinspection PyUnresolvedReferences
    def get_challenge(self, challenge_id_or_name: int | str) -> "ChallengeInfo":
        """Retrieve a challenge object for the given challenge ID."""
        from .challenge import ChallengeInfo

        if challenge_id_or_name is None:
            return None

        data = self.htb_http_request.get_request(endpoint=f'challenge/info/{challenge_id_or_name}')["challenge"]
        return ChallengeInfo(_client=self, data=data)


    # noinspection PyUnresolvedReferences
    def get_challenges(self, retired: bool = False) -> List["ChallengeList"]:
        """Requests a list of `Challenge` from the API"""
        from .challenge import ChallengeList

        if retired:
            data = self.htb_http_request.get_request(f"challenge/list/retired")
        else:
            data = self.htb_http_request.get_request(f"challenge/list")

        return [ChallengeList(data=x, _client=self) for x in data["challenges"]]

    # noinspection PyUnresolvedReferences
    def get_prolabs(self) -> List["ProLabInfo"]:
        """Requests a list of `ProLab` from the API"""
        from .prolab import ProLabInfo

        data: dict = self.htb_http_request.get_request(endpoint=f"prolabs")["data"]

        if data is None or len(data) == 0:
            return []

        return [ProLabInfo(data=x, _client=self) for x in data["labs"]]

    # noinspection PyUnresolvedReferences
    def get_prolab(self, prolab_id: Optional[int], prolab_name: Optional[str]) -> Optional["ProLabInfo"]:
        """Requests a `ProLab` from the API"""
        from .prolab import ProLabInfo

        data: dict = self.htb_http_request.get_request(endpoint=f"prolabs")["data"]

        if data is None or len(data) == 0:
            return None

        data_lab: Optional[dict]
        try:
            if prolab_id is not None:
                data_lab = next(x for x in data["labs"] if x["id"] == prolab_id)
            else:
                data_lab = next(x for x in data["labs"] if x["name"].lower().strip() == prolab_name.lower().strip())
        except StopIteration:
            return None

        if data_lab is None or len(data_lab) == 0:
            return None

        return ProLabInfo(data=data_lab, _client=self)



    # noinspection PyUnresolvedReferences
    def get_all_vpn_server(self,
                           products: List[str] = None,
                           vpn_location: Optional[str] = None) -> dict[int, "VpnServerInfo"]:
        """Get all VPN Server for the given product.
        :args: products. Valid values (as list): "labs", "starting_point", "fortresses", "release_arena", "endgames", "prolab"
               prolab_id: If product is equal to "prolab", I prolab_id must be indicated. Use "get_prolabs()" for
               retrieving the ID.
               prolab_name: Name of the prolab, if product = "prolab"
        """
        from .vpn import VpnServerInfo
        from .prolab import ProLabInfo
        import hashlib
        global _vpn_server_cache

        def parse_data(raw_data: dict, my_location: Optional[str]) -> dict:
            data_assigned: dict = raw_data.get("assigned", dict())
            data_location: dict = raw_data.get("options", dict())
            servers = dict()
            for location in [k for k in data_location.keys() if my_location is None or k == my_location]:
                for location_role in data_location[location].keys():
                    for server in data_location[location][location_role]["servers"].values():
                        server["product"] = f'{product} | {prolab_name}' if product == "prolab" else product
                        if data_assigned is not None and server["id"] == data_assigned.get("id", -1):
                            server["is_assigned"] = True
                            server["location_type_friendly"] = data_assigned.get("location_type_friendly", None)
                        servers[server["id"]] = VpnServerInfo(data=server, _client=self)
            return servers

        if products is None or len(products) == 0:
            products = ["starting_point", "fortresses", "release_arena", "labs", "endgames", "prolab"]


        vpn_servers: dict[int, VpnServerInfo] = dict()
        for product in [p for p in products if p != "prolab"]:
            # caching key
            caching_key = hashlib.md5(f'{product}'.encode()).hexdigest()

            # VPN Server are not altered very often. Use a cache for increasing performance. But we have to consider between
            # "release_arena" VPN-server and for "labs" VPN Server
            if (_vpn_server_cache is not None and
                    caching_key in _vpn_server_cache.keys() and
                    len(_vpn_server_cache[caching_key].keys()) > 0):
                print(f"Caching hit: {caching_key} | {product}")
                vpn_servers = vpn_servers | _vpn_server_cache.get(caching_key)
                continue

            if _vpn_server_cache is None:
                _vpn_server_cache = dict()

            data: dict = self.htb_http_request.get_request(endpoint=f"connections/servers?product={product}")["data"]
            servers = parse_data(data, my_location=vpn_location)
            _vpn_server_cache[caching_key] = servers
            if vpn_servers is not None and len(vpn_servers.keys()) > 0:
                for server in servers.values():
                    if server.id in vpn_servers.keys():
                        server.product = f'{product} | {vpn_servers[server.id].product}'

            vpn_servers = vpn_servers | servers

        if "prolab" in products:
            for prolab in self.get_prolabs():
                product = "prolab"
                prolab_name = prolab.name
                # caching key
                caching_key = hashlib.md5(f'{product}{prolab.id}'.encode()).hexdigest()

                # VPN Server are not altered very often. Use a cache for increasing performance. But we have to consider between
                # "release_arena" VPN-server and for "labs" VPN Server
                if (_vpn_server_cache is not None and
                        caching_key in _vpn_server_cache.keys() and
                        len(_vpn_server_cache[caching_key].keys()) > 0):
                    vpn_servers = vpn_servers | _vpn_server_cache.get(caching_key)
                    continue

                data: dict = self.htb_http_request.get_request(endpoint=f"connections/servers/prolab/{prolab.id}")["data"]
                servers = parse_data(data, my_location=vpn_location)
                _vpn_server_cache[caching_key] = servers
                vpn_servers = vpn_servers | servers

        return vpn_servers

    # noinspection PyUnresolvedReferences
    def get_accessible_vpn_server(self) -> dict[int, "AccessibleVpnServer"]:
        """Get all VPN Server which are directly accessible without switching the VPN-Server"""
        from .vpn import AccessibleVpnServer

        data: dict = self.htb_http_request.get_request(endpoint=f"connections")["data"]
        if data is None or len(data.keys()) == 0:
            return dict()

        prolabs: dict = {}
        for k, v in data.items():
            # prolabs are originally deeper in the tree structure. Flat the structure to access the prolabs easily, later.
            if k == "pro_labs":
                prolabs = {k:v for k,v in data[k].items() if type(v) == dict}
            else:
                data[k]["type"] = k  # key contains e.g. "lab", "endgames", ...

        data.pop("pro_labs", None)
        for k,v in prolabs.items():
            data[k] = v
            data[k]["type"] = "prolabs"

        del prolabs
        servers =  [AccessibleVpnServer(data=x, _client=self) for x in data.values()]

        return {k.id: k for k in servers if k.id is not None and k.id > 0}

    # noinspection PyUnresolvedReferences
    def get_active_connections(self) -> List["VpnConnection"]:
        from .vpn import VpnConnection

        data: List = self.htb_http_request.get_request(endpoint=f"connection/status")
        return [VpnConnection(data=x, _client=self) for x in data]


    # noinspection PyUnresolvedReferences
    def get_badges(self,
                   user_id: Optional[int]=None,
                   username: Optional[str]=None,
                   remove_obtained_badges: Optional[bool]=None) -> List["BadgeCategory"]:
        """Get all badges"""
        from .badge import BadgeCategory, Badge
        res = []

        if remove_obtained_badges is None:
            remove_obtained_badges = False

        user: User = self.get_user(user_id=user_id, username=username)
        if user is None:
            return res

        data: List[dict] = self.htb_http_request.get_request(endpoint=f"badges")["categories"]
        for x in data:
            badge_category = BadgeCategory(_client=self, data=x)
            if remove_obtained_badges:
                badge_category.badges = [x for x in badge_category.badges if x.id not in user.badges.keys()]
            else:
                for badge in badge_category.badges:
                    badge.set_badge_obtained(badge_obtained=badge.id in user.badges.keys(), when=user.badges.get(badge.id, None))

            res.append(badge_category)

        return res

    # noinspection PyUnresolvedReferences
    def get_machine_list(self,
                         retired: bool = False,
                         keyword: str = None,
                         limit: Optional[int] = None,
                         os_filter: Optional[List[str]] = None,
                         difficulty_filter: Optional[List[str]] = None,
                         sort_by: Optional[str] = "release-date",
                         sort_type: Optional[str] = "desc") -> List["MachineInfo"]:
        """Get a list of all machines for the given keyword (search word) and whether only retired or active machine should be
        considered."""
        from .machine import MachineInfo

        assert sort_type is None or sort_type in ["asc", "desc"]
        assert os_filter is None or len(os_filter) == len([x for x in os_filter if x in ["windows", "linux", "freebsd", "other", "openbsd"]])
        assert difficulty_filter is None or len(difficulty_filter) == len([x for x in difficulty_filter if x in ["easy", "medium", "hard", "insane"]])

        keyword_option = ""
        if keyword is not None:
            keyword_option = f'&keyword={keyword}'

        sort_option = ""
        if sort_by is not None:
            sort_option = f'&sort_type={sort_type}'

        os_filter_option = ""
        if os_filter is not None and len(os_filter) > 0:
            os_filter_option = "".join([f'&os[]={x}' for x in os_filter])

        os_difficulty_option = ""
        if difficulty_filter is not None and len(difficulty_filter) > 0:
            os_difficulty_option = "".join([f'&difficulty[]={x}' for x in difficulty_filter])

        result_list: List[MachineInfo] = []
        page_number = 1
        while True:
            if retired:
                res = self.htb_http_request.get_request(endpoint=f"machine/list/retired/paginated?per_page=100&page={page_number}{keyword_option}{sort_option}{os_filter_option}{os_difficulty_option}")
            else:
                res = self.htb_http_request.get_request(endpoint=f"machine/paginated?per_page=100&page={page_number}{keyword_option}{sort_option}{os_filter_option}{os_difficulty_option}")

            data: list = res["data"]
            if data is None or len(data) == 0:
                return result_list

            # Add retired flag because that data does not contain this information
            for x in data:
                if "retired" not in x:
                    x["retired"] = retired

            result_list = result_list + [MachineInfo(_client=self, data=x) for x in data]

            if limit is not None and len(data) >= limit:
                return result_list[:limit]

            meta: dict = res["meta"]
            last_page: int = meta["last_page"]
            if last_page <= page_number:
                break

            time.sleep(0.3)
            page_number += 1

        return result_list

    # noinspection PyUnresolvedReferences
    def get_unreleased_machines(self) -> List[Tuple["MachineInfo", Optional["MachineInfo"]]]:
        """Get a list of all unreleased machines and the corresponding scheduled retired machine (if available)"""
        from .machine import MachineInfo
        data: List[dict] = self.htb_http_request.get_request(endpoint=f"machine/unreleased")["data"]

        res = []
        for row in data:
            machine = self.get_machine(machine_id_or_name=row["id"])

            retiring_machine: Optional[MachineInfo] = None
            if "retiring" in row:
                retiring_machine = self.get_machine(machine_id_or_name=row["retiring"]["id"])

            res.append((machine, retiring_machine))
        return res


    # noinspection PyUnresolvedReferences
    def get_machine(self, machine_id_or_name: int | str) -> "MachineInfo":
        """Retrieve a machine object for the given machine ID or name."""
        from .machine import MachineInfo

        if machine_id_or_name is None:
            return None

        data = self.htb_http_request.get_request(endpoint=f'machine/profile/{machine_id_or_name}')["info"]
        return MachineInfo(_client=self, data=data)

    # noinspection PyUnresolvedReferences
    def get_active_machine(self) -> Optional["ActiveMachineInfo"]:
        """Retrieve the active machine info."""
        from .machine import ActiveMachineInfo

        data:dict = self.htb_http_request.get_request(endpoint=f'machine/active')["info"]
        if data is None or len(data.keys()) == 0:
            return None

        return ActiveMachineInfo(_client=self, data=data)
    

    # noinspection PyUnresolvedReferences
    def get_user_activity(self, user_id: int) -> List["Activity"]:
        """Retrieves a list of `Activity` from the API"""
        from .activity import Activity

        data:dict = self.htb_http_request.get_request(endpoint=f'user/profile/activity/{user_id}')["profile"]
        if len(data["activity"]) == 0:
            return []

        return [Activity(data=x, _client=self) for x in data["activity"]]

    # noinspection PyUnresolvedReferences
    def get_fortress_list(self) -> List["Fortress"]:
        """Retrieves a list of `Fortress` from the API"""
        from .fortress import Fortress

        data: dict = self.htb_http_request.get_request(endpoint=f'fortresses')["data"]
        return [Fortress(_client=self, data=self.htb_http_request.get_request(endpoint=f'fortress/{x["id"]}')["data"]) for x in data.values()]


    def __repr__(self):
        return f"<Client '{self._api_base}{self._api_version}'>"

class BaseHtbApiObject(object):
    _client: HTBClient
    id: int

    def __eq__(self, other):
        return self.id == other.id and type(self) == type(other)
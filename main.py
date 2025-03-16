from datetime import datetime
import json
import time
from colorama import Fore
import requests
import random


class zoopapp:
    BASE_URL = "https://tgapi.zoop.com/api/"
    HEADERS = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
        "connection": "keep-alive",
        "host": "tgapi.zoop.com",
        "content-type": "application/json",
        "origin": "https://tgapp.zoop.com",
        "referer": "https://tgapp.zoop.com/",
        "sec-ch-ua": '"Microsoft Edge";v="134", "Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge WebView2";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0",
    }

    def __init__(self):
        self.query_list = self.load_query("query.txt")
        self.token = None
        self.config = self.load_config()
        self.userId = None
        self.index_daily = 0

    def banner(self) -> None:
        """Displays the banner for the bot."""
        self.log("🎉 Zoop App Free Bot", Fore.CYAN)
        self.log("🚀 Created by LIVEXORDS", Fore.CYAN)
        self.log("📢 Channel: t.me/livexordsscript\n", Fore.CYAN)

    def log(self, message, color=Fore.RESET):
        safe_message = message.encode("utf-8", "backslashreplace").decode("utf-8")
        print(
            Fore.LIGHTBLACK_EX
            + datetime.now().strftime("[%Y:%m:%d ~ %H:%M:%S] |")
            + " "
            + color
            + safe_message
            + Fore.RESET
        )

    def load_config(self) -> dict:
        """
        Loads configuration from config.json.

        Returns:
            dict: Configuration data or an empty dictionary if an error occurs.
        """
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                self.log("✅ Configuration loaded successfully.", Fore.GREEN)
                return config
        except FileNotFoundError:
            self.log("❌ File not found: config.json", Fore.RED)
            return {}
        except json.JSONDecodeError:
            self.log(
                "❌ Failed to parse config.json. Please check the file format.",
                Fore.RED,
            )
            return {}

    def load_query(self, path_file: str = "query.txt") -> list:
        """
        Loads a list of queries from the specified file.

        Args:
            path_file (str): The path to the query file. Defaults to "query.txt".

        Returns:
            list: A list of queries or an empty list if an error occurs.
        """
        self.banner()

        try:
            with open(path_file, "r") as file:
                queries = [line.strip() for line in file if line.strip()]

            if not queries:
                self.log(f"⚠️ Warning: {path_file} is empty.", Fore.YELLOW)

            self.log(f"✅ Loaded {len(queries)} queries from {path_file}.", Fore.GREEN)
            return queries

        except FileNotFoundError:
            self.log(f"❌ File not found: {path_file}", Fore.RED)
            return []
        except Exception as e:
            self.log(f"❌ Unexpected error loading queries: {e}", Fore.RED)
            return []

    def login(self, index: int) -> None:
        self.log("🔐 Attempting to log in...", Fore.GREEN)

        if index >= len(self.query_list):
            self.log("❌ Invalid login index. Please check again.", Fore.RED)
            return

        token = self.query_list[index]
        self.log(
            f"📋 Using token: {token[:10]}... (truncated for security)",
            Fore.CYAN,
        )

        req_url = f"{self.BASE_URL}oauth/telegram"
        payload = {"initData": token}
        headers = self.HEADERS

        try:
            self.log("📡 Sending login request...", Fore.CYAN)
            response = requests.post(req_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            if "data" in data:
                data = data["data"]
                access_token = data.get("access_token")
                if not access_token:
                    self.log("❌ Access token not found in response.", Fore.RED)
                    return

                info = data.get("information", {})
                self.token = access_token  # Simpan access_token ke self.token
                self.userId = info.get("userId", "Unknow")
                self.index_daily = info.get("index", 0)

                username = info.get("username", "Unknown")
                year_join = info.get("yearJoin", "N/A")
                point = info.get("point", 0)
                spin = info.get("spin", 0)
                is_premium = info.get("isPremium", False)

                self.log("✅ Login successful!", Fore.GREEN)
                self.log(f"👤 Username: {username}", Fore.LIGHTGREEN_EX)
                self.log(f"🎂 Year Joined: {year_join}", Fore.CYAN)
                self.log(f"⭐ Premium: {is_premium}", Fore.CYAN)
                self.log(f"💎 Points: {point}", Fore.CYAN)
                self.log(f"🔄 Spins: {spin}", Fore.CYAN)
            else:
                self.log("⚠️ Unexpected response structure.", Fore.YELLOW)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to send login request: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"❌ Data error (possible JSON issue): {e}", Fore.RED)
        except KeyError as e:
            self.log(f"❌ Key error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", Fore.RED)

    def spin(self) -> None:
        self.log("🎰 Checking spin opportunity...", Fore.GREEN)

        # Siapkan headers dengan menambahkan authorization
        headers = {**self.HEADERS, "Authorization": f"Bearer {self.token}"}
        user_url = f"{self.BASE_URL}users/{self.userId}"

        # Ambil data user untuk mendapatkan jumlah spin yang tersedia
        try:
            response = requests.get(user_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if "data" in data:
                user_data = data["data"]
                current_spin = user_data.get("spin", 0)
                self.log(f"🎰 Current spin available: {current_spin}", Fore.CYAN)
                if current_spin <= 0:
                    self.log("ℹ️ No spin opportunity available.", Fore.YELLOW)
                    return
            else:
                self.log("⚠️ Unexpected response structure from user details.", Fore.YELLOW)
                return
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch user details: {e}", Fore.RED)
            return
        except ValueError as e:
            self.log(f"❌ Data error (possible JSON issue): {e}", Fore.RED)
            return
        except KeyError as e:
            self.log(f"❌ Key error: {e}", Fore.RED)
            return

        spin_url = f"{self.BASE_URL}users/spin"

        # Lakukan spin terus selama spin > 0
        import datetime
        while current_spin > 0:
            current_date = datetime.datetime.utcnow().isoformat() + "Z"  # Format ISO UTC dengan trailing 'Z'
            payload = {"userId": self.userId, "date": current_date}

            self.log(f"🎡 Attempting spin. Spins remaining: {current_spin}", Fore.CYAN)
            try:
                spin_response = requests.post(spin_url, headers=headers, json=payload)
                spin_response.raise_for_status()
                spin_data = spin_response.json()

                if "data" in spin_data:
                    spin_result = spin_data["data"]
                    circle = spin_result.get("circle", {})
                    reward = circle.get("name", "N/A")
                    self.log(f"✅ Spin successful! Reward: {reward}", Fore.GREEN)
                else:
                    self.log("⚠️ Unexpected spin response structure.", Fore.YELLOW)
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Failed to perform spin: {e}", Fore.RED)
                break
            except ValueError as e:
                self.log(f"❌ Data error during spin (possible JSON issue): {e}", Fore.RED)
                break
            except KeyError as e:
                self.log(f"❌ Key error during spin: {e}", Fore.RED)
                break

            # Perbarui jumlah spin yang tersisa dengan melakukan GET ulang
            try:
                response = requests.get(user_url, headers=headers)
                response.raise_for_status()
                data = response.json()
                if "data" in data:
                    user_data = data["data"]
                    current_spin = user_data.get("spin", 0)
                    self.log(f"🔄 Updated spin available: {current_spin}", Fore.CYAN)
                else:
                    self.log("⚠️ Unexpected response structure while updating spin count.", Fore.YELLOW)
                    break
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Failed to update spin count: {e}", Fore.RED)
                break
            except ValueError as e:
                self.log(f"❌ Data error while updating spin count (possible JSON issue): {e}", Fore.RED)
                break
            except KeyError as e:
                self.log(f"❌ Key error while updating spin count: {e}", Fore.RED)
                break

        # Lakukan final check untuk memastikan tidak ada lagi kesempatan spin
        try:
            response = requests.get(user_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if "data" in data:
                final_spin = data["data"].get("spin", 0)
                self.log(f"✅ Final spin count: {final_spin}", Fore.GREEN)
            else:
                self.log("⚠️ Unexpected final response structure.", Fore.YELLOW)
        except Exception as e:
            self.log(f"❌ Error during final spin count check: {e}", Fore.RED)
            
    def daily(self) -> None:
        self.log("testing bro")
        self.log("🌞 Collecting daily reward...", Fore.GREEN)
        headers = {**self.HEADERS, "Authorization": f"Bearer {self.token}"}
        daily_url = f"{self.BASE_URL}asks/rewardDaily/{self.userId}"
        payload = {"index": self.index_daily + 1}

        try:
            response = requests.post(daily_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            if "data" in data:
                daily_data = data["data"]
                # Perbarui index_daily jika ada field dailyIndex di response
                self.index_daily = daily_data.get("dailyIndex", self.index_daily)
                
                self.log("✅ Daily reward claimed successfully!", Fore.GREEN)
                self.log(f"📆 Day Claim: {daily_data.get('dayClaim')}", Fore.CYAN)
                self.log(f"🔁 Claimed: {daily_data.get('claimed')}", Fore.CYAN)
                self.log(f"🎡 Spined: {daily_data.get('spined')}", Fore.CYAN)
            else:
                self.log("⚠️ Unexpected response structure.", Fore.YELLOW)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to claim daily reward: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"❌ Data error (possible JSON issue): {e}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", Fore.RED)

    def task(self) -> None:
        self.log("🔍 Fetching tasks...", Fore.GREEN)
        headers = {**self.HEADERS, "Authorization": f"Bearer {self.token}"}
        social_url = f"{self.BASE_URL}social"

        try:
            response = requests.get(social_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            tasks = data.get("data", [])
            self.log(f"✅ Retrieved {len(tasks)} tasks.", Fore.GREEN)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch tasks: {e}", Fore.RED)
            return
        except ValueError as e:
            self.log(f"❌ Data error (possible JSON issue): {e}", Fore.RED)
            return

        # Proses setiap task
        for task in tasks:
            task_type = task.get("type", "")
            task_title = task.get("title", "Unknown Task")
            task_id = task.get("_id")
            
            # Jika task merupakan task yang sudah selesai (REGISTER_ZOOP_APP), lewati proses claim
            if task_type == "REGISTER_ZOOP_APP":
                self.log(f"ℹ️ Task '{task_title}' already completed. Skipping.", Fore.YELLOW)
                continue

            # Siapkan endpoint claim task dan payload sesuai misi task
            claim_url = f"{self.BASE_URL}tasks/verified/{task_id}"
            payload = {
                "point": task.get("point", 0),
                "spin": task.get("spin", 0),
                "type": task_type
            }

            self.log(f"🚀 Claiming task '{task_title}' with payload: {payload}", Fore.CYAN)
            try:
                claim_response = requests.post(claim_url, headers=headers, json=payload)
                claim_response.raise_for_status()
                claim_data = claim_response.json()
                self.log(f"✅ Successfully claimed task '{task_title}'", Fore.GREEN)
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Failed to claim task '{task_title}': {e}", Fore.RED)
            except ValueError as e:
                self.log(f"❌ Data error during claim for task '{task_title}': {e}", Fore.RED)
            except Exception as e:
                self.log(f"❌ Unexpected error during claim for task '{task_title}': {e}", Fore.RED)

    def load_proxies(self, filename="proxy.txt"):
        """
        Reads proxies from a file and returns them as a list.

        Args:
            filename (str): The path to the proxy file.

        Returns:
            list: A list of proxy addresses.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                proxies = [line.strip() for line in file if line.strip()]
            if not proxies:
                raise ValueError("Proxy file is empty.")
            return proxies
        except Exception as e:
            self.log(f"❌ Failed to load proxies: {e}", Fore.RED)
            return []

    def set_proxy_session(self, proxies: list) -> requests.Session:
        """
        Creates a requests session with a working proxy from the given list.

        If a chosen proxy fails the connectivity test, it will try another proxy
        until a working one is found. If no proxies work or the list is empty, it
        will return a session with a direct connection.

        Args:
            proxies (list): A list of proxy addresses (e.g., "http://proxy_address:port").

        Returns:
            requests.Session: A session object configured with a working proxy,
                            or a direct connection if none are available.
        """
        # If no proxies are provided, use a direct connection.
        if not proxies:
            self.log("⚠️ No proxies available. Using direct connection.", Fore.YELLOW)
            self.proxy_session = requests.Session()
            return self.proxy_session

        # Copy the list so that we can modify it without affecting the original.
        available_proxies = proxies.copy()

        while available_proxies:
            proxy_url = random.choice(available_proxies)
            self.proxy_session = requests.Session()
            self.proxy_session.proxies = {"http": proxy_url, "https": proxy_url}

            try:
                test_url = "https://httpbin.org/ip"
                response = self.proxy_session.get(test_url, timeout=5)
                response.raise_for_status()
                origin_ip = response.json().get("origin", "Unknown IP")
                self.log(
                    f"✅ Using Proxy: {proxy_url} | Your IP: {origin_ip}", Fore.GREEN
                )
                return self.proxy_session
            except requests.RequestException as e:
                self.log(f"❌ Proxy failed: {proxy_url} | Error: {e}", Fore.RED)
                # Remove the failed proxy and try again.
                available_proxies.remove(proxy_url)

        # If none of the proxies worked, use a direct connection.
        self.log("⚠️ All proxies failed. Using direct connection.", Fore.YELLOW)
        self.proxy_session = requests.Session()
        return self.proxy_session

    def override_requests(self):
        """Override requests functions globally when proxy is enabled."""
        if self.config.get("proxy", False):
            self.log("[CONFIG] 🛡️ Proxy: ✅ Enabled", Fore.YELLOW)
            proxies = self.load_proxies()
            self.set_proxy_session(proxies)

            # Override request methods
            requests.get = self.proxy_session.get
            requests.post = self.proxy_session.post
            requests.put = self.proxy_session.put
            requests.delete = self.proxy_session.delete
        else:
            self.log("[CONFIG] proxy: ❌ Disabled", Fore.RED)
            # Restore original functions if proxy is disabled
            requests.get = self._original_requests["get"]
            requests.post = self._original_requests["post"]
            requests.put = self._original_requests["put"]
            requests.delete = self._original_requests["delete"]


if __name__ == "__main__":
    zoop = zoopapp()
    index = 0
    max_index = len(zoop.query_list)
    config = zoop.load_config()
    if config.get("proxy", False):
        proxies = zoop.load_proxies()

    zoop.log(
        "🎉 [LIVEXORDS] === Welcome to Zoop App Automation === [LIVEXORDS]", Fore.YELLOW
    )
    zoop.log(f"📂 Loaded {max_index} accounts from query list.", Fore.YELLOW)

    while True:
        current_account = zoop.query_list[index]
        display_account = (
            current_account[:10] + "..."
            if len(current_account) > 10
            else current_account
        )

        zoop.log(
            f"👤 [ACCOUNT] Processing account {index + 1}/{max_index}: {display_account}",
            Fore.YELLOW,
        )

        if config.get("proxy", False):
            zoop.override_requests()
        else:
            zoop.log("[CONFIG] Proxy: ❌ Disabled", Fore.RED)

        zoop.login(index)

        zoop.log("🛠️ Starting task execution...")
        tasks = {
            "daily": "Automatically claim your daily reward! 🌞",
            "task": "Automatically complete your tasks! ✅",
            "spin": "Automatically spin the wheel! 🎰"
        }

        for task_key, task_name in tasks.items():
            task_status = config.get(task_key, False)
            zoop.log(
                f"[CONFIG] {task_name}: {'✅ Enabled' if task_status else '❌ Disabled'}",
                Fore.YELLOW if task_status else Fore.RED,
            )

            if task_status:
                zoop.log(f"🔄 Executing {task_name}...")
                getattr(zoop, task_key)()

        if index == max_index - 1:
            zoop.log("🔁 All accounts processed. Restarting loop.")
            zoop.log(
                f"⏳ Sleeping for {config.get('delay_loop', 30)} seconds before restarting."
            )
            time.sleep(config.get("delay_loop", 30))
            index = 0
        else:
            zoop.log(
                f"➡️ Switching to the next account in {config.get('delay_account_switch', 10)} seconds."
            )
            time.sleep(config.get("delay_account_switch", 10))
            index += 1

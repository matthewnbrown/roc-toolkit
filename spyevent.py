import time
import random
import os
import pickle
from os.path import exists
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from rocalert.captcha.captcha_logger import CaptchaLogger
from rocalert.cookiehelper import (
    load_cookies_from_browser,
    load_cookies_from_path,
    save_cookies_to_path,
)
from rocalert.events import SpyEvent
from rocalert.roc_settings import SettingsSetupHelper, UserSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.rocaccount import BattlefieldTarget
from rocalert.services import captchaservices
from rocalert.services.urlgenerator import ROCDecryptUrlGenerator
from rocalert.services.rocwebservices import BattlefieldPageService

lower_rank_cutoff = 0
upper_rank_cutoff = None

# Comma separated ids. Put your own ID in here
skip_ids = {7530}
skip_ranks = {112, 666}

reversed_order = True

captcha_method = "none" # ai or manual or none

# This will only spy on selected IDs. Other filters ignored
onlyspy_ids = {}

# Page range for battlefield scanning
lower_page_range = 1
upper_page_range = None  # If None, will automatically find the largest page

login_sessions = 10
bf_scan_workers = 10
bf_async_scan_pages = 5
spy_workers = 50
spy_async_spy_counts = 10

cookie_filename = "cookies" # this is old, dont use it to save the 10 cookies

captchasavepath = "captcha_img/"
captchaans_log = "logs/spyevent.log"

skip_idsstr = {str(id) for id in skip_ids}
onlyspy_idsstr = {str(id) for id in onlyspy_ids}


class SessionManager:
    """Manages multiple login sessions with cookie storage and retrieval"""
    
    def __init__(self, user_settings: UserSettings, num_sessions: int):
        self.user_settings = user_settings
        self.num_sessions = num_sessions
        self.sessions: List[RocWebHandler] = []
        self.session_lock = Lock()
        self.session_dir = "sessions"
        
        # Create sessions directory if it doesn't exist
        if not os.path.exists(self.session_dir):
            os.makedirs(self.session_dir)
    
    def create_sessions(self) -> bool:
        """Create and login the specified number of sessions"""
        print(f"Creating {self.num_sessions} login sessions...")
        
        success_count = 0
        for i in range(self.num_sessions):
            try:
                roc = RocWebHandler(ROCDecryptUrlGenerator())
                if self._login_session(roc, i):
                    self.sessions.append(roc)
                    success_count += 1
                    print(f"Session {i+1}/{self.num_sessions} created successfully")
                else:
                    print(f"Failed to create session {i+1}/{self.num_sessions}")
                
                # Small delay between logins
                # time.sleep(1)
                
            except Exception as e:
                print(f"Error creating session {i+1}: {e}")
        
        print(f"Successfully created {success_count}/{self.num_sessions} sessions")
        return success_count > 0
    
    def _login_session(self, roc: RocWebHandler, session_id: int) -> bool:
        """Login a single session and save cookies"""
        session_file = os.path.join(self.session_dir, f"session_{session_id}.cookies")
        
        # Try to load existing cookies first
        if self._load_session_cookies(roc, session_file) and roc.is_logged_in():
            return True
        
        # Try browser cookies
        if self._load_browser_cookies(roc) and roc.is_logged_in():
            self._save_session_cookies(roc, session_file)
            return True
        
        # Perform fresh login
        try:
            roc.login(
                self.user_settings.get_setting("email").value,
                self.user_settings.get_setting("password").value
            )
            # time.sleep(0.5)
            
            if roc.is_logged_in():
                self._save_session_cookies(roc, session_file)
                return True
        except Exception as e:
            print(f"Login error for session {session_id}: {e}")
        
        return False
    
    def _load_session_cookies(self, roc: RocWebHandler, session_file: str) -> bool:
        """Load cookies from session file"""
        if os.path.exists(session_file):
            try:
                with open(session_file, 'rb') as f:
                    cookies = pickle.load(f)
                    roc.add_cookies(cookies)
                    return True
            except Exception as e:
                print(f"Error loading session cookies: {e}")
        return False
    
    def _save_session_cookies(self, roc: RocWebHandler, session_file: str):
        """Save cookies to session file"""
        try:
            with open(session_file, 'wb') as f:
                pickle.dump(roc.get_cookies(), f)
        except Exception as e:
            print(f"Error saving session cookies: {e}")
    
    def _load_browser_cookies(self, roc: RocWebHandler) -> bool:
        """Load cookies from browser"""
        if self.user_settings.get_setting("load_cookies_from_browser").value:
            try:
                url_generator = ROCDecryptUrlGenerator()
                cookies = load_cookies_from_browser(
                    self.user_settings.get_setting("browser").value,
                    url_generator.get_home()
                )
                roc.add_cookies(cookies)
                return True
            except Exception as e:
                print(f"Error loading browser cookies: {e}")
        return False
    
    def get_random_session(self) -> Optional[RocWebHandler]:
        """Get a random available session"""
        with self.session_lock:
            if not self.sessions:
                return None
            return random.choice(self.sessions)


class BattlefieldScanningWorkers:
    """Manages battlefield page scanning with multiple workers"""
    
    def __init__(self, session_manager: SessionManager, num_workers: int, pages_per_batch: int):
        self.session_manager = session_manager
        self.num_workers = num_workers
        self.pages_per_batch = pages_per_batch
    
    def scan_battlefield_pages(self) -> List[BattlefieldTarget]:
        """Scan battlefield pages using multiple workers"""
        # Get total page range using first available session
        session = self.session_manager.get_random_session()
        if not session:
            print("No sessions available for battlefield scanning")
            return []
        
        try:
            # Use configured page range or get from battlefield
            if upper_page_range is None:
                # Get the maximum page from battlefield
                _, max_page = BattlefieldPageService.get_page_range(session)
                actual_lower = lower_page_range
                actual_upper = max_page
                print(f'Using configured lower page ({lower_page_range}) and auto-detected upper page ({max_page})')
            else:
                # Use configured page range
                actual_lower = lower_page_range
                actual_upper = upper_page_range
                print(f'Using configured page range: {actual_lower} to {actual_upper}')
            
            print(f'Battlefield scanning: Pages {actual_lower} to {actual_upper} with {self.num_workers} workers')
        except Exception as e:
            print(f"Error getting page range: {e}")
            return []
        
        all_users = []
        page_ranges = []
        
        # Create page ranges for workers
        for start in range(actual_lower, actual_upper + 1, self.pages_per_batch):
            end = min(start + self.pages_per_batch - 1, actual_upper)
            page_ranges.append((start, end))
        
        # Process page ranges with workers
        import time
        scan_start = time.time()
        completed_ranges = 0
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            future_to_range = {
                executor.submit(self._scan_page_range, start, end): (start, end)
                for start, end in page_ranges
            }
            
            for future in as_completed(future_to_range):
                start, end = future_to_range[future]
                try:
                    users = future.result()
                    all_users.extend(users)
                    completed_ranges += 1
                    elapsed = time.time() - scan_start
                    print(f'Scanned pages {start}-{end}: {len(users)} users ({completed_ranges}/{len(page_ranges)} ranges) - Elapsed: {elapsed:.1f}s')
                except Exception as e:
                    print(f'Error scanning pages {start}-{end}: {e}')
        
        total_scan_time = time.time() - scan_start
        print(f'Total users scanned: {len(all_users)} in {total_scan_time:.2f} seconds')
        return all_users
    
    def _scan_page_range(self, start_page: int, end_page: int) -> List[BattlefieldTarget]:
        """Scan a range of pages using a single worker"""
        session = self.session_manager.get_random_session()
        if not session:
            return []
        
        users = []
        for pagenum in range(start_page, end_page + 1):
            try:
                user_resp = BattlefieldPageService.run_service(session, pagenum)
                if user_resp['response'] == 'success':
                    users.extend(user_resp['result'])
                else:
                    print(f'Error loading page {pagenum}: {user_resp.get("error", "Unknown error")}')
                
                # Small delay between pages
                # time.sleep(0.1)
                
            except Exception as e:
                print(f'Exception loading page {pagenum}: {e}')
        
        return users


class SpyWorkers:
    """Manages spy operations with multiple workers"""
    
    def __init__(self, session_manager: SessionManager, num_workers: int, spy_attempts_per_batch: int):
        self.session_manager = session_manager
        self.num_workers = num_workers
        self.spy_attempts_per_batch = spy_attempts_per_batch
        self.url_generator = ROCDecryptUrlGenerator()
        self.completed_users = set()  # Track users who are completely spied on
    
    def spy_on_users(self, users: List[BattlefieldTarget], user_filter_func, captcha_method: str, solver=None) -> None:
        """Spy on users using multiple workers"""
        import time
        spy_operation_start = time.time()
        
        filtered_users = [user for user in users if user_filter_func(user) and user.id not in self.completed_users]
        if not filtered_users:
            print("No users to spy on after filtering (all users already completed)")
            return
        
        print(f'Starting spy operations on {len(filtered_users)} users with {self.num_workers} workers')
        print(f'Users already completed: {len(self.completed_users)}')
        
        # Distribute users among workers
        users_per_worker = max(1, len(filtered_users) // self.num_workers)
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            future_to_worker = {}
            
            for i in range(0, len(filtered_users), users_per_worker):
                worker_users = filtered_users[i:i + users_per_worker]
                if worker_users:
                    future = executor.submit(
                        self._spy_worker, 
                        worker_users, 
                        captcha_method, 
                        solver
                    )
                    future_to_worker[future] = f"Worker-{i//users_per_worker + 1}"
            
            # Wait for all workers to complete
            completed_workers = 0
            for future in as_completed(future_to_worker):
                worker_name = future_to_worker[future]
                try:
                    result = future.result()
                    completed_workers += 1
                    elapsed = time.time() - spy_operation_start
                    print(f'{worker_name} completed ({completed_workers}/{len(future_to_worker)}): {result} - Elapsed: {elapsed:.1f}s')
                except Exception as e:
                    print(f'{worker_name} failed: {e}')
        
        total_spy_time = time.time() - spy_operation_start
        print(f'Spy operations completed in {total_spy_time:.2f} seconds. Total users fully spied: {len(self.completed_users)}')
    
    def _spy_worker(self, users: List[BattlefieldTarget], captcha_method: str, solver=None) -> dict:
        """Single spy worker that processes a batch of users"""
        session = self.session_manager.get_random_session()
        if not session:
            return {"error": "No session available"}
        
        stats = {"users_processed": 0, "successful_spies": 0, "errors": 0, "completed_users": 0}
        
        for user in users:
            try:
                # Skip if user is already completed
                if user.id in self.completed_users:
                    continue
                
                #print(f'Worker spying on user #{user.rank}: {user.name}')
                
                # Perform spy attempts for this user
                spy_results = self._spy_user_multiple_attempts(
                    session, user, self.spy_attempts_per_batch, captcha_method, solver
                )
                
                stats["users_processed"] += 1
                stats["successful_spies"] += spy_results["successful"]
                stats["errors"] += spy_results["errors"]
                
                # Mark user as completed if they hit limit or reached max attempts
                if spy_results["completed"]:
                    self.completed_users.add(user.id)
                    stats["completed_users"] += 1
                    print(f'✅ User #{user.rank}: {user.name} - COMPLETED (fully spied)')
                
                # Small delay between users
                #time.sleep(0.5)
                
            except Exception as e:
                print(f'Error processing user {user.name}: {e}')
                stats["errors"] += 1
        
        return stats
    
    def _spy_user_multiple_attempts(self, session: RocWebHandler, user: BattlefieldTarget, 
                                  num_attempts: int, captcha_method: str, solver=None) -> dict:
        """Perform multiple spy attempts on a single user"""
        targeturl = self.url_generator.get_home() + f'/attack.php?id={user.id}&mission_type=recon'
        payload = {
            'defender_id': user.id,
            'mission_type': 'recon',
            'reconspies': 1,
            'submit': 'Recon'
        }
        
        results = {"successful": 0, "errors": 0, "completed": False}
        max_spies_per_user = 10  # Maximum spies allowed per user
        
        for attempt in range(num_attempts):
            try:
                # Stop if we've reached the maximum spies for this user
                if results["successful"] >= max_spies_per_user:
                    results["completed"] = True
                    print(f'Reached max spies ({max_spies_per_user}) for user {user.name}')
                    break
                
                # Handle captcha based on method
                captcha = None
                if captcha_method == "manual":
                    # For manual captcha, we'd need to get from a queue
                    # This is a simplified version
                    pass
                elif captcha_method == "ai" and solver:
                    # Get and solve captcha automatically
                    captcha = session.get_img_captcha('roc_armory')
                    if captcha:
                        solved_captcha = solver.solve_captcha(captcha)
                        captcha.ans = solved_captcha.ans
                
                # Submit spy request
                valid_captcha = session.submit_captcha_url(
                    captcha, targeturl, payload, session.Pages.SPY
                )
                
                if valid_captcha:
                    results["successful"] += 1
                    if 'You cannot recon this person' in session.r.text:
                        print(f'Reached spy limit for user {user.name}')
                        results["completed"] = True
                        break
                    elif 'Administrator account' in session.r.text:
                        print(f'Detected admin account {user.name}')
                        results["completed"] = True
                        break
                else:
                    results["errors"] += 1
                
                # Small delay between attempts
                #  time.sleep(0.2)
                
            except Exception as e:
                print(f'Spy attempt {attempt + 1} failed for {user.name}: {e}')
                results["errors"] += 1
        
        # Mark as completed if we've done the maximum attempts or hit limits
        if results["successful"] >= max_spies_per_user or results["completed"]:
            results["completed"] = True
        
        return results


def user_filter(user: BattlefieldTarget) -> bool:
    if onlyspy_idsstr and len(onlyspy_idsstr) > 0:
        return user in onlyspy_idsstr

    if (
        lower_rank_cutoff
        and user.rank < lower_rank_cutoff
        or upper_rank_cutoff
        and user.rank > upper_rank_cutoff
    ):
        return False

    return not (user.rank in skip_ranks or user.id in skip_idsstr)


def __load_browser_cookies(roc: RocWebHandler, us: UserSettings) -> bool:
    if us.get_setting("load_cookies_from_browser").value:
        url_generator = ROCDecryptUrlGenerator()
        cookies = load_cookies_from_browser(
            us.get_setting("browser").value, url_generator.get_home()
        )
        roc.add_cookies(cookies)
        # time.sleep(0.25)
        return True
    return False


def __load_cookies_file(roc: RocWebHandler, cookie_filename: str) -> bool:
    if exists(cookie_filename):
        print("Loading saved cookies")
        cookies = load_cookies_from_path(cookie_filename)
        if cookies is not None:
            roc.add_cookies(cookies)
        return True
    
    return False

def __log(s: str):
    print(s)


def login(roc: RocWebHandler, us: UserSettings):
    __log("Attempting to get login status")
    if __load_cookies_file(roc, cookie_filename) and roc.is_logged_in():
        __log("Successfully used cookie file")
        return True

    if __load_browser_cookies(roc, us) and roc.is_logged_in():
        __log(
            "Successfully pulled cookie from {}".format(us.get_setting("browser").value)
        )
        save_cookies_to_path(roc.get_cookies(), cookie_filename)
        return True

    __log("Logging in..")
    roc.login(us.get_setting("email").value, us.get_setting("password").value)
    time.sleep(0.25)
    if roc.is_logged_in():
        __log("Login success.")
        save_cookies_to_path(roc.get_cookies(), cookie_filename)
        return True
    else:
        __log("Login failure.")
        return False

def valid_captcha_method(method: str) -> bool:
    
    if method == "manual" or method == "none":
        return (True, None)
    if method == "ai":
        captcha_settings = captchaservices.get_captcha_settings(method)
        if captcha_settings is None:
            filename = captchaservices.create_captcha_settings_file(method)
            print(f"Created settings file {filename}. Please fill it out and restart")
            quit()
        base_url = captcha_settings["base_url"]
        return (True, captchaservices.RemoteCaptchaSolverService(
            solve_url= base_url + captcha_settings["solve_url"],
            report_url= base_url + captcha_settings["report_url"],
        ))
    return (False, "Invalid captcha method")

def runevent_new():
    # Start timing the entire event
    import time
    start_time = time.time()
    print("🚀 Starting Spy Event - Timer Started")
    
    filepaths = {
        "user": ("user.settings", UserSettings),
    }

    valid, solver = valid_captcha_method(captcha_method)
    if not valid:
        print(solver)
        quit()
        
    settings_file_error = False

    for settype, infotuple in filepaths.items():
        path, settingtype = infotuple
        if SettingsSetupHelper.needs_setup(path):
            settings_file_error = True
            SettingsSetupHelper.create_default_file(path, settingtype.DEFAULT_SETTINGS)
            print(f"Created settings file {path}.")

    if settings_file_error:
        print("Exiting. Please fill out settings files")
        return

    user_settings = UserSettings(filepath=filepaths["user"][0])
    
    # Create session manager and establish multiple login sessions
    session_start = time.time()
    print(f"Setting up {login_sessions} login sessions...")
    session_manager = SessionManager(user_settings, login_sessions)
    
    if not session_manager.create_sessions():
        print("Failed to create login sessions. Exiting.")
        quit()
    
    session_time = time.time() - session_start
    print(f"✅ Session setup completed in {session_time:.2f} seconds")
    
    # Create battlefield scanning workers
    bf_scan_start = time.time()
    print(f"Setting up battlefield scanning with {bf_scan_workers} workers, {bf_async_scan_pages} pages per batch...")
    bf_scanner = BattlefieldScanningWorkers(session_manager, bf_scan_workers, bf_async_scan_pages)
    
    # Scan battlefield pages
    print("Scanning battlefield pages...")
    all_users = bf_scanner.scan_battlefield_pages()
    
    if not all_users:
        print("No users found during battlefield scan. Exiting.")
        quit()
    
    bf_scan_time = time.time() - bf_scan_start
    print(f"✅ Battlefield scanning completed in {bf_scan_time:.2f} seconds")
    
    # Filter users
    filter_start = time.time()
    filtered_users = [user for user in all_users if user_filter(user)]
    filter_time = time.time() - filter_start
    print(f"Found {len(filtered_users)} users to spy on after filtering ({filter_time:.2f}s)")
    
    if not filtered_users:
        print("No users to spy on after filtering. Exiting.")
        quit()
    
    # Create spy workers and perform spying
    spy_start = time.time()
    print(f"Setting up spy operations with {spy_workers} workers, {spy_async_spy_counts} attempts per user...")
    spy_worker_manager = SpyWorkers(session_manager, spy_workers, spy_async_spy_counts)
    
    # Perform spy operations
    spy_worker_manager.spy_on_users(filtered_users, user_filter, captcha_method, solver)
    
    spy_time = time.time() - spy_start
    total_time = time.time() - start_time
    
    print("\n" + "="*60)
    print("🏁 SPY EVENT COMPLETED!")
    print("="*60)
    print(f"📊 TIMING SUMMARY:")
    print(f"   Session Setup:     {session_time:.2f} seconds")
    print(f"   Battlefield Scan:  {bf_scan_time:.2f} seconds") 
    print(f"   User Filtering:    {filter_time:.2f} seconds")
    print(f"   Spy Operations:    {spy_time:.2f} seconds")
    print(f"   ⏱️  TOTAL TIME:      {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    print(f"📈 STATISTICS:")
    print(f"   Total Users Found: {len(all_users)}")
    print(f"   Users Spied On:    {len(filtered_users)}")
    print(f"   Users Completed:   {len(spy_worker_manager.completed_users)}")
    print("="*60)


runevent_new()

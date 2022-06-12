# roc-toolkit

Start with run.py

If this is your first run, or you're missing settings files, they will be created for you

Auto captcha solving using [2Captcha](https://2captcha.com/)

### User Settings

### Login Details  
**email:** email<span>@email.</span>com  
**password:** password123  


**auto_solve_captchas:** False or True  
**auto_captcha_key:** replace_with_2captcha_apikey  

**notify_soldier_amt:** 60  (currently unused)  

### Range of time before checking for captchas
**min_checktime_secs:** 300  
**max_checktime_secs:** 600    

### Switch to a second check range during a certain period of the day
**enable_nightmode:** False  
**nightmode_minwait_mins:** 60  
**nightmode_maxwait_mins:** 120  
**nightmode_begin:** 20:00  (Must be a time in format HH:MM or HH:MM:SS)  
**nightmode_end:** 09:00   (Must be a time in format HH:MM or HH:MM:SS)  

### Program exits if this many failures occur consecutively 
**max_consecutive_login_failures:** 2  
**max_consecutive_captcha_attempts:** 3 (Actual failed captcha attempts)  
**max_consecutive_answer_errors:** 5   (Receiving impossible answers i.e., letters)  

**captcha_save_path:** captcha_img/  (path to save captcha images to)  

#### Pull cookie from a browser you already use to login
**load_cookies_from_browser:** True or False  
**browser:** chrome or firefox

### Site Settings
All of the settings below must be a complete URL for identifying the webpage.

**roc_home:** ENTER_HOME_URL  
**roc_login:** ENTER_LOGIN_URL  
**roc_recruit:** ENTER_RECRUIT_URL  

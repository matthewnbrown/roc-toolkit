# roc-toolkit

Start with run.py, or install with `pip install .` and run using roc-toolkit-cli

If this is your first run, or you're missing settings files, they will be created for you

Auto captcha solving using [2Captcha](https://2captcha.com/) and [TrueCaptcha](https://truecaptcha.org/)

Windows installation notes:  
`pip install .` should install everything

Ubuntu installation notes:  
Install pillow and ImageTK:
`apt-get install python3-pil python3-pil.imagetk`  
Install tkinter:
`apt-get install python3-tk`  
Install lxml:
`apt-get install python3-lxml`  
`pip install .` for the rest

## User Settings

#### Login Details

**email:** email<span>@email.</span>com  
**password:** password123

**auto_solve_captchas:** False or 2captcha or truecaptcha

#### Range of time before checking for captchas

**min_checktime_secs:** 300  
**max_checktime_secs:** 600

#### Switch to a second check range during a certain period of the day

**enable_nightmode:** False  
**nightmode_minwait_mins:** 60  
**nightmode_maxwait_mins:** 120  
**nightmode_begin:** 20:00 (Must be a time in format HH:MM or HH:MM:SS)  
**nightmode_end:** 09:00 (Must be a time in format HH:MM or HH:MM:SS)

#### Program exits/times out if this many failures occur consecutively

**max_consecutive_login_failures:** 2  
**max_consecutive_captcha_attempts:** 3 (Actual failed captcha attempts)  
**max_consecutive_answer_errors:** 5 (Receiving impossible answers i.e., letters)  
**captcha_failure_timeout:** 0 (How long to wait in minutes after failures. 0 Exits)

#### Exception Handling

**enable_exception_timeout:** True/False (Enable timeout and retry for unhandled exceptions)  
**exception_timeout_minutes:** 30 (Number of minutes to wait before retrying after an unhandled exception)

**captcha_save_path:** captcha_img/ (path to save captcha images to)

#### Pull cookie from a browser you already use to login

**load_cookies_from_browser:** True or False  
**browser:** chrome or firefox

#### Remote Lookup

**remote_captcha_lookup:** None (API url to lookup captcha answer based on hash)  
**remote_captcha_add:** None (API call to add captcha answer to database)

## Buyer Settings

Gold is divided by the folloing formula for each weapon:

(gold) \* (weapon number) / (sum of all weapon numbers)

## Trainer settings

**train_soldiers:** True/False  
**soldier_weapon_match:** True/False (Should soldiers be purchased to match weapons)  
**soldier_dump_type:** attack/defense/spies/sentries (All excess untrained dumped to this category)  
**soldier_round_amount:** Integer > 0 (Instead of matching weaponcount exactly, round up this amount (nearest 100, 1000 etc)  
**min_train_purchase_size:** Integer > 0 (Minimum size to complete a training purchase)

# Loads settings from a filepath in setting:value format
# if must_match is true, then a settings_dict must be passed. Values will only be UPDATED
# if must_have_value is true then if
def load_settings(filepath, settings_dict = None, must_match = False, must_have_value = False) -> dict:
    if settings_dict is None:
        settings_dict = {}

    with open(filepath) as f:
        lines = f.readlines()

        for line in lines:
            setting_name, value = line.split(':',maxsplit=1)
            setting_name = setting_name.strip()
            value = value.strip()
            if must_match and setting_name not in settings_dict:
                continue
            if setting_name == '':
                print("Warning: A setting existed with no value")
                continue
            if must_have_value and value == '':
                print("Warning: setting {} has no value".format(setting_name))
                continue
            settings_dict[setting_name] = value
                
    return settings_dict

def __check_dict_int(setdic, key, default) -> None:
    if key not in setdic:
        setdic[key] = default
    else:
        setdic[key] = int(setdic[key])

# loads user settings, does some checks and casts
def load_user_settings(filepath, settings_dict = None) -> dict:
    settings_dict = load_settings(filepath, settings_dict)

    mandatory_user_settings = ['email', 'password']

    count = 0
    for setting in mandatory_user_settings:
        if setting not in settings_dict:
            print("ERROR: {} setting not set!".format(setting))
            count += 1
    
    if count > 0:
        quit()

    if 'auto_solve_captchas' not in settings_dict:
        settings_dict['auto_solve_captchas'] = False
    else:
        settings_dict['auto_solve_captchas'] = settings_dict['auto_solve_captchas'].lower() == 'true'

    default_ints = {'notify_soldier_amt':60, 'min_checktime_secs':300, 'max_checktime_secs':600 }

    for key,val in default_ints.items():
        __check_dict_int(settings_dict, key, val)

    return settings_dict
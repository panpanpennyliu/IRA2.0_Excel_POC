import pygetwindow as gw

def switch_window(window_title):
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        window.activate()
        window.maximize()
    except IndexError:
        print(f"can not find '{window_title}'")
        raise Exception(f"Window '{window_title}' not found.")
    except Exception as e:
        print(f"Switch window error: {e}")
        raise Exception(f"Error switching to window '{window_title}': {e}")

def fuzzy_match_window(keyword):
    all_windows = gw.getAllWindows()
    matching_windows = []
    for window in all_windows:
        if window.title and keyword.lower() in window.title.lower():
            matching_windows.append(window)

    if not matching_windows:
        print(f"Can not find windows containing keyword: '{keyword}'")

    return matching_windows

def get_all_window_titles():
    all_windows = gw.getAllWindows()
    window_titles = [window.title for window in all_windows if window.title]
    return window_titles
 
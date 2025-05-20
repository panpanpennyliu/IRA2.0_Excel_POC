import pygetwindow as gw

from core.llm_chat import LLMChat
from prompt.action_executor import SWITCH_SELECT_WINDOW
from replay_agent.planner.replayer_action import ReplayerAction

def switch_window(window_title):
    try:
        windows = gw.getWindowsWithTitle(window_title)
        index = 0
        if len(windows) > 1:
            titles_dict = {index: window.title for index, window in enumerate(windows)}
            index = int(select_window(titles_dict, window_title))
            window_title = titles_dict[index]
        #     selected_window = None
        windows[index].activate()
        windows[index].maximize()
        return window_title
    
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

def select_window(windows, window_title):
    switch_select_window = SWITCH_SELECT_WINDOW.format(window_title = window_title)
    chat = LLMChat()
    replayerAction = ReplayerAction(chat)
    switch_select_window_list = ["index"]
    switch_select_window_json = replayerAction.get_respond_prompt(switch_select_window_list, switch_select_window, windows )
        
    return switch_select_window_json["index"]
 
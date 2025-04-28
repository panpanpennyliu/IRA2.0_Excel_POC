import win32gui
import win32con

def switch(window_title):
    hwnd = find_window_by_title(window_title)
    if hwnd:
        print(f"找到窗口，句柄为: {hwnd}")
        maximize_window(hwnd)
    else:
        print(f"未找到标题为 '{window_title}' 的窗口")
        raise Exception(f"未找到标题为 '{window_title}' 的窗口")


def find_window_by_title(title):
    hwnd = win32gui.FindWindow(None, title)
    return hwnd

def minimize_window(hwnd):
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

def maximize_window(hwnd):
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

def close_window(hwnd):
    if hwnd:
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)


    
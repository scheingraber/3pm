from plyer import notification as pn
from threading import Thread as thread
import sys, os
import struct
import time
import platform
# detect system
if platform.system() == 'Windows':
    import win32con
    from win32api import *
    from win32gui import *


class WindowsBalloonTip:
    def __init__(self):
        message_map = {
                win32con.WM_DESTROY: self.OnDestroy,
        }
        # Register the Window class.
        wc = WNDCLASS()
        self.hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = "PythonTaskbar"
        wc.lpfnWndProc = message_map # could also specify a wndproc.
        self.classAtom = RegisterClass(wc)

    def ShowWindow(self, title, msg, timeout):
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = CreateWindow( self.classAtom, "Taskbar", style, \
                0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, \
                0, 0, self.hinst, None)
        UpdateWindow(self.hwnd)
        iconPathName = os.path.abspath(os.path.join( sys.path[0], "balloontip.ico" ))
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        try:
           hicon = LoadImage(self.hinst, iconPathName, \
                    win32con.IMAGE_ICON, 0, 0, icon_flags)
        except:
          hicon = LoadIcon(0, win32con.IDI_APPLICATION)
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, hicon, "tooltip")
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY, \
                         (self.hwnd, 0, NIF_INFO, win32con.WM_USER+20,\
                          hicon, "Balloon  tooltip", msg, 200, title))
        DestroyWindow(self.hwnd)

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0) # Terminate the app.


class Notification(object):
    """
    Another wrapper around plyer notification facade, because
    plyer.notification crashes on packaged PyInstaller apps.
    """

    def __init__(self, **kwargs):
        # detect system
        if platform.system() == 'Windows':
            # init notification class once
            self.balloon_tip = WindowsBalloonTip()

    def notify(self, title='', message='', app_name='', app_icon='',
               timeout=10):
        """
        Send a notification.

        :param title: Title of the notification
        :param message: Message of the notification
        :param app_name: Name of the app launching this notification
        :param app_icon: Icon to be displayed along with the message
        :param timeout: time to display the message for, defaults to 10
        :type title: str
        :type message: str
        :type app_name: str
        :type app_icon: str
        :type timeout: int
        """
        self._notify(title=title, message=message, app_icon=app_icon,
                     app_name=app_name, timeout=timeout)

    # private
    def _notify(self, **kwargs):
        # detect system
        if platform.system() == 'Windows':
            # custom notification on windows since plyer does not work with PyInstaller
            thread(target=self.balloon_tip.ShowWindow,
                   args=(kwargs['title'], kwargs['message'], kwargs['timeout'])).start()

        else:
            # plyer for everything else
            pn.notify(title=kwargs['title'], message=kwargs['message'],
                      timeout=kwargs['timeout'])

import wx
from view.Interface import *

if __name__ == '__main__':
    app = wx.App()
    frame = Interface(None)
    frame.Show()
    app.MainLoop()
# Copyright 2009-2010 Ram Rachum. No part of this program may be used, copied
# or distributed without explicit written permission from Ram Rachum.

import pkg_resources
import wx

from garlicsim_wx.general_misc import wx_tools

import garlicsim, garlicsim_wx

from .cruncher_selection_dialog import CruncherSelectionDialog

    
class CruncherControls(wx.Panel):
    '''tododoc'''
    
    def __init__(self, parent, frame, *args, **kwargs):
        
        assert isinstance(frame, garlicsim_wx.Frame)
        self.frame = frame
        self.gui_project = frame.gui_project
        
        wx.Panel.__init__(self, parent, *args, **kwargs)
        
        self.SetBackgroundColour(wx_tools.get_background_color())

        
        self.main_v_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.SetSizer(self.main_v_sizer)
        
        self.title_text = wx.StaticText(self, -1, 'Cruncher in use:')
        
        self.main_v_sizer.Add(self.title_text, 0)
        
        self.cruncher_in_use_static_text = wx.StaticText(self, -1, '')
        self.cruncher_in_use_static_text.SetFont(
            wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL)
        )
        
        self.main_v_sizer.Add(self.cruncher_in_use_static_text, 0,
                              wx.EXPAND | wx.ALL, 5)
        
        
        self.change_cruncher_button = wx.Button(self, -1, 'Change...')
        self.Bind(wx.EVT_BUTTON, self.on_change_cruncher_button,
                  self.change_cruncher_button)
        
        self.main_v_sizer.Add(self.change_cruncher_button, 0,
                              wx.ALIGN_RIGHT, 0)
        
        self.gui_project.cruncher_type_changed_emitter.add_output(
            self._recalculate
        )
        
        
    def on_change_cruncher_button(self, event):
        cruncher_selection_dialog = CruncherSelectionDialog()
        cruncher_selection_dialog.ShowModal()
        
    
    def _recalculate(self):
        self.cruncher_in_use_static_text.SetLabel(
            self.gui_project.project.crunching_manager.Cruncher.__name__
        )
        


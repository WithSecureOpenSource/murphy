'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

TBD
user automation with windows specific extensions, other os's (ios, android,
etc) should use same extension mechanism
'''
import time

from murphy.user_simulation import user_automation

class WindowsUser(user_automation.UserAutomation):

    def run_command(self, cmd):
        '''
        Executes the given command by typing it in the search box in the
        taskbar, note this is not the run command dialog!
        '''
        self.open_start_menu()
        #FIXME: for now
        #self.wait_stable_screen()
        time.sleep(0.1)
        self.keyboard.enters(cmd + '{enter}')
        
        
    def open_start_menu(self):
        '''
        Opens the start menu
        '''
        self.wait_stable_screen()
        self.keyboard.enters("{+ctrl}{esc}{-ctrl}")

        
    def show_desktop(self):
        '''
        Shows the windows desktop by clicking on the far right lower corner button
        '''
        self.wait_stable_screen()
        screen = self.grab_screen()
        #FIXME: taskbar is / may be cropped!
        x, y = screen.size[0] - 5, screen.size[1] - 10
        self.mouse.click(x, y)

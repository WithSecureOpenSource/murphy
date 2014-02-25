'''
Automatically generated from a model extractor
'''

#Needed due to mismatch with json...
true = True
false = False

HERE = {'desc': 'Node 0',
        'snapshots': ['node_00.0.bmp'],
        'snapshots mask': [None],
        'reference snapshots': ['node_00.0.ref.bmp'],
        'custom': {}}


WORKER = None


def launch_application():
    '''
    Launches the desired application
    '''
    import time
    
    use_command = WORKER.properties.get('command to launch', '')
    if use_command == '':
        use_command = r'\utils\runurl.py http://192.168.56.1:8901/files/7z_newer.vbs'
    
    WORKER.Wait(HERE['desc'])
    #We need a bit more time to finish booting...
    time.sleep(3)
    
    WORKER.input.keyboard.enters('{+ctrl}{esc}{-ctrl}')
    WORKER.input.keyboard.enters(use_command)
    WORKER.input.keyboard.enters('{enter}')



V_ELEM_00 = {'desc': 'Launch application',
             'goes to': 'Welcome To 7Zip Installer Press Ok To Continue 7Zip Installation',
             'how': launch_application,
             'custom': {}}


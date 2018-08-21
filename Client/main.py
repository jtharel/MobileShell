#qpy:kivy

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
import time
import threading
import os
import paramiko

Builder.load_string('''
<MyInterface>:
    orientation: 'vertical'

    BoxLayout
        id: login_layout
        orientation: 'vertical'
        padding: [10,50,10,50]
        spacing: 50

        Label:
            text: 'Client Setup'
            font_size: 64

        BoxLayout:
            orientation: 'vertical'

            Label:
                text: 'Username'
                font_size:36
                halign: 'left'
                
            TextInput:
                id: login
                multiline:False
                font_size: 36

        BoxLayout:
            orientation: 'vertical'
            
            Label:
                text: 'Password'
                halign: 'left'
                font_size: 36
               
            TextInput:
                id: password
                multiline:False
                password: True
                font_size: 36

        BoxLayout:
            orientation: 'vertical'
            
            Label:
                text: 'Server IP Address'
                halign: 'left'
                font_size: 36
                
            TextInput:
                id: ip
                multiline:False
                password: False
                font_size: 36

        MyButton:
            text: 'Connect'
            font_size: 48
            on_press:self.buttonClicked(login, password, ip)

            
''')

class MyInterface(BoxLayout):
    pass

class MyButton(Button):

    def buttonClicked(self, login, password, ip):
        if password.text == '':
            popup = Popup(title="Error!", content=Label(text="Password can't be blank."),size_hint=(0.7,0.3))
            popup.open()
            return
        elif login.text == '':
            popup = Popup(title="Error!", content=Label(text="Name can't be blank."),size_hint=(0.7,0.3))
            popup.open()
            return
        elif ip.text == '':
            popup = Popup(title="Error!", content=Label(text="IP can't be blank."),size_hint=(0.7,0.3))
            popup.open()
            return
        else:
            
            def sftp(path):
                try:
                    t = paramiko.Transport((ip.text, 22))
                    t.connect(username=login.text, password=password.text)
                    sftp_client=paramiko.SFTPClient.from_transport(t)
                    sftp_client.put(path, '/root/temp/'+path)
                    sftp_client.close()
                    transport.close()
                except:
                    pass

            def connect():
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(ip.text, 222, username=login.text, password=password.text)
                chan = client.get_transport().open_session()
                chan.send("Hello, this is the client! :-) ")
                print chan.recv(1024)

                while True:

                    command = chan.recv(1024)
                    if 'quit' in command:
                        break

                    elif 'pwd' in command:
                        chan.send( os.getcwd() )

                    elif 'ps' in command:
                        pscmd = 'ps'
                        psoutput = os.popen(pscmd).read()
                        chan.send( psoutput )

                    elif 'am' in command:
                        amcmd = 'am'
                        amoutput = os.popen(amcmd).read()
                        chan.send( amoutput )
                        chan.send( "Coming Soon...." )
                        
                    elif 'libs' in command:
                        try:
                            code,pid = command.split (' ')
                            libscmd = 'cat /proc/' + pid + '/maps |grep \.so'
                            libsoutput = os.popen(libscmd).read()
                            chan.send( libsoutput )
                        except:
                            chan.send( 'Error, is that a valid PID' )
                            
                    elif 'ls' in command:
                        try:
                            cmd = 'ls -la'
                            result = os.popen(cmd).read()
                            chan.send( result )
                        except:
                            chan.send( "Something went wrong :-(" )
                
                    elif 'cd' in command:
                        try:
                            code,directory = command.split (' ')
                            os.chdir(directory)
                            chan.send( "pwd is " + os.getcwd() )
                        except:
                            chan.send( "Error, what is the directory name?" )

                    elif 'uname' in command:
                        chan.send ( str(os.uname()) )

                    elif 'cat' in command:
                        try:
                            code,filename = command.split (' ')
                            with open(filename, 'r') as fin:
                                chan.send( fin.read() )
                            fin.close()
                        except:
                            chan.send( "Error, what is the file name?" )

                    elif 'scp' in command:
                        scp,path = command.split(' ')
                        threading.Thread(target=sftp, args=(path,)).start()
                        chan.send ('Sending Files')

                    elif 'id' in command:
                        idcmd = 'id'
                        idoutput = os.popen(idcmd).read()
                        chan.send( idoutput )

                    elif 'ifconfig' in command:
                        ifconfigcmd = 'ifconfig wlan0'
                        ifoutput = os.popen(ifconfigcmd).read()
                        chan.send( ifoutput )

                    elif 'help' in command:
                        helplist = '''
 am              Activity Manager - coming soon!
 cat             Concatenate and print files
 cd              Change the current directory
 help            Return this menu
 id              Return user identity
 ifconfig        Show IP address
 libs            Show libraries in use given a PID. i.e. libs <pid>
 ls              List directory contents
 pwd             Return working directory name
 ps              Process status list
 quit            Quit this program
 scp             Secure copy to /root/temp of server. i.e. scp <filename>
 uname           Print os name
                            '''
                        chan.send( helplist )
                                   
                    else:
                        chan.send("I dont' understand, try again")

            connect()

    
        
class MyApp(App):
    def build(self):
        return MyInterface()

MyApp().run()






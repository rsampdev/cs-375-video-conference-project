import errno
import select
import socket
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

HEADER_LENGTH = 10

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title('Video Conference Client')
        self.geometry('250x500')

        self.style = ttk.Style(self)
        self.configure(background='light blue')

        self.username_label = tk.Label(text="Username:", relief=tk.RAISED)
        self.username_label.pack(anchor = tk.CENTER, expand = True)

        self.username = tk.StringVar()
        self.username.trace("w", lambda name, index, mode, username=self.username: username.get())

        self.username_box = ttk.Entry(self, width=25, justify='center', textvariable=self.username)
        self.username_box.pack(anchor = tk.CENTER, expand = True)

        self.server_ip_label = tk.Label(text="Server IP:", relief=tk.RAISED)
        self.server_ip_label.pack(anchor = tk.CENTER, expand = True)

        self.server_ip = tk.StringVar()
        self.server_ip.trace("w", lambda name, index, mode, ip=self.server_ip: ip.get())

        self.server_ip_box = ttk.Entry(self, width=25, justify='center', textvariable=self.server_ip)
        self.server_ip_box.pack(anchor = tk.CENTER, expand = True)

        self.server_port_label = tk.Label(text="Server Port:", relief=tk.RAISED)
        self.server_port_label.pack(anchor = tk.CENTER, expand = True)

        self.server_port = tk.StringVar()
        self.server_port.trace("w", lambda name, index, mode, port=self.server_port: port.get())

        self.server_port_box = ttk.Entry(self, width=25, justify='center', textvariable=self.server_port)
        self.server_port_box.pack(anchor = tk.CENTER, expand = True)

        self.is_connected = False
        self.connect_button = ttk.Button(self, text = 'Connect', width=20, command=self.connectionHandler)
        self.connect_button.pack(anchor = tk.CENTER, expand = True)

        self.sharing_video = False
        self.video_button = ttk.Button(self, text = 'Share Video', width=20, command=self.videoHandler)
        self.video_button.pack(anchor = tk.CENTER, expand = True)

        self.sharing_audio = False
        self.audio_button = ttk.Button(self, text='Share Audio', width=20, command=self.audioHandler)
        self.audio_button.pack(anchor = tk.CENTER, expand = True)

        self.chat_text = tk.StringVar()
        self.chat_text.trace("w", lambda name, index, mode, chat_text=self.chat_text: chat_text.get())

        self.server_ip_label = tk.Label(text="Chat:", relief=tk.RAISED)
        self.server_ip_label.pack(anchor = tk.CENTER, expand = True)

        self.text_area = ScrolledText(self, width = 25, height = 10, state = tk.DISABLED)
        self.text_area.pack(anchor = tk.CENTER, expand = True)

        self.chat_button = ttk.Button(self, text = 'Send Message', width = 25, command=self.textHandler)
        self.chat_button.pack(anchor = tk.CENTER, expand = True)

        self.chat_box = ttk.Entry(self, width=25, textvariable=self.chat_text)
        self.chat_box.pack(anchor = tk.CENTER, expand = True)
    
    def encodeStringVar(self, sv):
        return sv.get().encode('utf-8')

    def connectionHandler(self):
        if self.is_connected:
            self.connect_button.configure(text='Connect to Server')

            self.client_socket.close()

        elif self.username and self.server_ip and self.server_port:
            self.connect_button.configure(text='Disconnect from Server')

            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.client_socket.connect((self.server_ip.get(), int(self.server_port.get())))

            self.client_socket.setblocking(False)

            username_header = f"{len(self.username.get()):<{HEADER_LENGTH}}".encode('utf-8')

            temp_username = self.encodeStringVar(self.username)

            self.client_socket.send(username_header + temp_username)

        self.is_connected = not self.is_connected
        
        print(f"Doing connection stuff Haha")

    def videoHandler(self):
        if self.sharing_video:
            self.video_button.configure(text='Share Video')
        else:
            self.video_button.configure(text='Stop Sharing Video')

        self.sharing_video = not self.sharing_video
        
        print(f"Video Haha")

    def audioHandler(self):
        if self.sharing_audio:
            self.audio_button.configure(text='Share Audio')
        else:
            self.audio_button.configure(text='Stop Sharing Audio')

        self.sharing_audio = not self.sharing_audio

        print(f"Audio Haha")

    def textHandler(self):
        text = f"{self.chat_text.get()}"
        
        self.chat_text.set("")
        self.chat_box.delete(0, len(text))
        
        if text:
            print(f"{text} Haha")

            self.text_area.configure(state=tk.NORMAL)
            self.text_area.insert(tk.INSERT, f"{self.username.get()}: {text}\n")
            self.text_area.see(tk.END)
            self.text_area.configure(state=tk.DISABLED)

            username_header = f"{len(self.username.get()):<{HEADER_LENGTH}}".encode('utf-8')

            temp_username = self.encodeStringVar(self.username)

            self.client_socket.send(username_header + temp_username)

if __name__ == "__main__":
    app = App()
    app.mainloop()
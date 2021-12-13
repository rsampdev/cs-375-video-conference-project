import json
import errno
import select
import socket
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

import socket
import cv2
import pickle
import struct
import imutils

from PIL import Image
from PIL import ImageTk

FORMAT = "utf-8"
HEADER_LENGTH = 10

IS_CONNECTED = False
IS_SHARING_VIDEO = False
IS_SHARING_AUDIO = False

CLIENT_VIDEOS = {}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Video Conference Client")
        self.geometry("250x500")

        self.style = ttk.Style(self)
        self.configure(background="light blue")

        self.username_label = tk.Label(text="Username:", relief=tk.RAISED)
        self.username_label.pack(anchor = tk.CENTER, expand = True)

        self.username = tk.StringVar()
        self.username.trace("w", lambda name, index, mode, username=self.username: username.get())

        self.username_box = ttk.Entry(self, width=25, justify="center", textvariable=self.username)
        self.username_box.pack(anchor = tk.CENTER, expand = True)

        self.server_ip_label = tk.Label(text="Server IP:", relief=tk.RAISED)
        self.server_ip_label.pack(anchor = tk.CENTER, expand = True)

        self.server_ip = tk.StringVar()
        self.server_ip.trace("w", lambda name, index, mode, ip=self.server_ip: ip.get())

        self.server_ip_box = ttk.Entry(self, width=25, justify="center", textvariable=self.server_ip)
        self.server_ip_box.pack(anchor = tk.CENTER, expand = True)

        self.server_port_label = tk.Label(text="Server Port:", relief=tk.RAISED)
        self.server_port_label.pack(anchor = tk.CENTER, expand = True)

        self.server_port = tk.StringVar()
        self.server_port.trace("w", lambda name, index, mode, port=self.server_port: port.get())

        self.server_port_box = ttk.Entry(self, width=25, justify="center", textvariable=self.server_port)
        self.server_port_box.pack(anchor = tk.CENTER, expand = True)

        self.connect_button = ttk.Button(self, text = "Connect", width=20, command=self.connectionHandler)
        self.connect_button.pack(anchor = tk.CENTER, expand = True)

        self.video_button = ttk.Button(self, text = "Share Video", width=20, command=self.videoHandler)
        self.video_button.pack(anchor = tk.CENTER, expand = True)
        
        self.audio_button = ttk.Button(self, text="Share Audio", width=20, command=self.audioHandler)
        self.audio_button.pack(anchor = tk.CENTER, expand = True)

        self.chat_text = tk.StringVar()
        self.chat_text.trace("w", lambda name, index, mode, chat_text=self.chat_text: chat_text.get())

        self.server_ip_label = tk.Label(text="Chat:", relief=tk.RAISED)
        self.server_ip_label.pack(anchor = tk.CENTER, expand = True)

        self.text_area = ScrolledText(self, width = 25, height = 10, state = tk.DISABLED)
        self.text_area.pack(anchor = tk.CENTER, expand = True)

        self.chat_box = ttk.Entry(self, width=25, textvariable=self.chat_text)
        self.chat_box.pack(anchor = tk.CENTER, expand = True)

        self.chat_button = ttk.Button(self, text = "Chat", width = 25, command=self.textHandler)
        self.chat_button.pack(anchor = tk.CENTER, expand = True)

        self.messages_thread = threading.Thread(target=self.receive_message)
        self.messages_thread.start()

        self.video_thread = threading.Thread(target=self.send_video)
        self.video_thread.start()

    def connectionHandler(self):
        global IS_CONNECTED

        if IS_CONNECTED:
            self.connect_button.configure(text="Connect to Server")
            self.client_socket.close()
        elif self.username and self.server_ip and self.server_port:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.server_ip.get(), int(self.server_port.get())))
                self.client_socket.setblocking(False)

                username_header = f"{len(self.username.get()):<{HEADER_LENGTH}}".encode(FORMAT)
                username = self.username.get().encode(FORMAT)

                connect_data = json.dumps({"type":"connect", "data":"Joined the room!"}).encode(FORMAT)
                connect_header = f"{len(connect_data):<{HEADER_LENGTH}}".encode(FORMAT)

                self.client_socket.send(username_header + username)
                self.client_socket.send(connect_header + connect_data)

                self.connect_button.configure(text="Disconnect from Server")
            except:
                pass

        IS_CONNECTED = not IS_CONNECTED

    def send_video(self):
        global IS_CONNECTED
        global IS_SHARING_VIDEO

        while True:
            if IS_CONNECTED and IS_SHARING_VIDEO:
                device = cv2.CAP_ANY
                capture = cv2.VideoCapture(device)

                if not capture.isOpened():
                    capture.open(device)

                while IS_SHARING_VIDEO and IS_CONNECTED and capture.isOpened():
                    success, frame = capture.read()

                    if IS_SHARING_VIDEO and IS_CONNECTED and success:
                        data = {"type":"video", "data":f"{frame}"}
                    else:
                        data = {"type":"video", "data":None}

                    message = json.dumps(data).encode(FORMAT)
                    message_header = f"{len(message):<{HEADER_LENGTH}}".encode(FORMAT)
                        
                    self.client_socket.send(message_header + message)
        
    def videoHandler(self):
        global IS_SHARING_VIDEO

        if IS_SHARING_VIDEO:
            self.video_button.configure(text="Share Video")
        else:
            self.video_button.configure(text="Stop Sharing Video")

        IS_SHARING_VIDEO = not IS_SHARING_VIDEO
        
    def audioHandler(self):
        global IS_SHARING_AUDIO

        if IS_SHARING_AUDIO:
            self.audio_button.configure(text="Share Audio")
        else:
            self.audio_button.configure(text="Stop Sharing Audio")

        IS_SHARING_AUDIO = not IS_SHARING_AUDIO

    def insertText(self, text):
        self.text_area.configure(state=tk.NORMAL)
        self.text_area.insert(tk.INSERT, text)
        self.text_area.see(tk.END)
        self.text_area.configure(state=tk.DISABLED)

    def textHandler(self):
        text = f"{self.chat_text.get()}"
        
        self.chat_text.set("")
        self.chat_box.delete(0, len(text))

        global IS_CONNECTED
        
        if IS_CONNECTED and text:
            self.insertText(f"{self.username.get()}: {text}\n")

            data = {"type":"text", "data":f"{text}"}

            message = json.dumps(data).encode(FORMAT)
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode(FORMAT)

            self.client_socket.send(message_header + message)

    def receive_message(self):
        while True:
            try:
                username_header = self.client_socket.recv(HEADER_LENGTH)
                
                if not len(username_header):
                    continue

                username_length = int(username_header.decode(FORMAT).strip())
                username = self.client_socket.recv(username_length).decode(FORMAT)

                if not (username in CLIENT_VIDEOS):
                    CLIENT_VIDEOS[username] = None
                    
                message_header = self.client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode(FORMAT).strip())
                message = self.client_socket.recv(message_length).decode(FORMAT)

                data = json.loads(message)

                if (data["type"] == "connect"):
                    text = data["data"]
                    self.insertText(f"{username}: {text}\n")
                elif (data["type"] == "video"):
                    pass

                    # frame_data = data["data"]
                    # cv2.imshow("Receiving...", frame_data)

                    # image = cv2.cvtColor(frame_data, cv2.COLOR_BGR2RGB)
                    # image = Image.fromarray(image)
                    # image = ImageTk.PhotoImage(image)

                    # if CLIENT_VIDEOS[username]:
                    #     window = CLIENT_VIDEOS[username]
                    #     tk.Label(window, image=image).pack()
                    # else:
                    #     newWindow = tk.Toplevel(self)
                    #     newWindow.title(username)
                    #     newWindow.geometry("200x200")
                    #     tk.Label(window, image=image).pack()
                    #     CLIENT_VIDEO[username] = newWindow

                elif (data["type"] == "audio"):
                    pass
                elif (data["type"] == "text"):
                    text = data["data"]
                    self.insertText(f"{username}: {text}\n")

            except:
                continue

if __name__ == "__main__":
    app = App()
    app.mainloop()
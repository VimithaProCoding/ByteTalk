import customtkinter as ctk
from PIL import Image
import os, time, socket, threading, hashlib, json, queue, webbrowser
from CTkMessagebox import CTkMessagebox
from rich import print as printc
my_path = os.path.dirname(os.path.abspath(__file__))
appdata_path = os.environ.get("APPDATA")

LOGIN = False
chat_messages = {}
login_username = ""
real_login_username = ""
user_butn_wigets = {}
msg_frames_dict = {}
msg_frame_label = {}
in_chat_now = "You"
CLIENT = None
TAG = "7b32c669abf7bb0292e7465a5613140f2672c6bb08a78c9872ac24e016c1e9b8"
w = ctk.CTk()
sever_conection = False

w.geometry(f"1025x650+400+150")
w.title("ByteTalk")
#w.resizable(False,False)
ctk.set_appearance_mode("light")
############################################################################################### queue list ##########################################################################################
login_recv_queue = queue.Queue()
register_recv_queue = queue.Queue()
add_frend_recv_queue = queue.Queue()
auto_load_chat_recv_queue = queue.Queue()
income_msg_recv_queue = queue.Queue()

def main_recver():
    printc('[bold green]Main_recver Thread Started')
    global sever_conection
    if sever_conection:
        while True:
            try:
                raw_data = CLIENT.recv(1024).decode('ascii')
                data = raw_data.split('|@|')

                if data[0] == 'login_check':
                    login_recv_queue.put(data[1])

                elif data[0] == 'register_new':
                    register_recv_queue.put(data[1])

                elif data[0] == 'add_frend_try':
                    add_frend_recv_queue.put(data[1])

                elif data[0] == 'auto_load_chat':
                    auto_load_chat_recv_queue.put(data[1])
                elif data[0] == 'income_msg':
                    income_msg_recv_queue.put(data[1])
                else:
                    printc(f'[bold blue]Unkown Recv From Server : {data[1]}')

            except Exception as e:
                printc('[bold red]ERROR in MAIN-Recver Code : ', e)
                printc('[bold red]Main_recver Thread Stoped.')
                sever_conection = False
                break

############################################################################################### Define ##########################################################################################

def conection_test():
    while True:
        if sever_conection:
            status.configure(image=online_img)#text="Online",text_color="#02ff41"
            top_frame.configure(fg_color="#3b81da")

        else:
            global LOGIN
            LOGIN = False
            global msg_frame_label
            for widget_label in msg_frame_label:
                msg_frame_label[widget_label].destroy()
            msg_frame_label = {}

            global user_butn_wigets
            for widget_label in user_butn_wigets:
                user_butn_wigets[widget_label].destroy()
            user_butn_wigets = {}

            status.configure(image=offline_img)#text="Offline",text_color="#dd0000"
            top_frame.configure(fg_color="#ff6262")
            msg_frame.grid_forget()
            main_frame.grid_forget()
            side_frame.grid_forget()
            add_acc_btn.grid_forget()

            main_frame2.grid(row=1, column=1,sticky="nsew")
            main_frame2.rowconfigure(0, weight=1)
            main_frame2.columnconfigure(0, weight=1)
            
        w.after(200)    

        time.sleep(2)

def click_login():
    def send_msg(msg1,msg2):
        try:
            global login_button
            login_button.configure(state="disabled")
            CLIENT.send(f"{TAG}:{msg1}:{msg2}".encode("ascii"))
            time.sleep(1)
        except Exception as e:
            print("\nError Send_msg : ",e)
            global sever_conection
            sever_conection = False
    def recv_msg():
        try:
            global login_button
            global LOGIN
            ch = login_recv_queue.get()
            if ch == "correct":
                login_username_entry.configure(border_color="#82EE91")
                login_password_entry.configure(border_color="#82EE91")
                # show and hide frames
                main_frame2.grid_forget()
                main_frame.grid(row=1, column=1,sticky="nsew",rowspan=2)
                main_frame.rowconfigure(0, weight=1)
                main_frame.columnconfigure(0, weight=1)
                side_frame.grid(row=1, column=0,sticky="nsew")
                add_acc_btn.grid(row=2, column=0,sticky="nsew")
            
                msg_frame.grid(row=0, column=0, sticky="nsew", pady=10,padx=10, columnspan=2)
                msg_frame.grid_columnconfigure(0, weight=1), msg_frame.grid_columnconfigure(1, weight=1)
                msg_frame.grid_rowconfigure(0, weight=1)
                LOGIN = True
                t = threading.Thread(target=display_unkown_msg, daemon=True)
                auto_load_db_chats()
                t.start()
                
                CTkMessagebox(title="Success", message="Logged in Successfully", icon="check")
            elif ch == "incorrect2":
                login_password_entry.configure(border_color="red")
                login_username_entry.configure(border_color="red")
                CTkMessagebox(title="Warning", message="This Account Is Using...", icon="warning")

            else: 
                login_password_entry.configure(border_color="red")
                login_username_entry.configure(border_color="red")
            time.sleep(1)
            login_button.configure(state="normal")
        except Exception as e:
            print("\nError recv_msg : ",e)
            global sever_conection
            sever_conection = False

    global sever_conection
    global login_username
    global real_login_username
    login_username = login_username_entry.get().lower().replace(" ","")
    real_login_username = login_username_entry.get()
    login_password = login_password_entry.get()
    if sever_conection:
        if login_username == "":
            login_username_entry.configure(border_color="red")
        else:
            login_username_entry.configure(border_color="#82EE91")
            if login_password == "":
                login_password_entry.configure(border_color="red")
            else:
                login_password_entry.configure(border_color="#82EE91")
                try:
                    send_thread = threading.Thread(target=send_msg,args=("login_check", f"{login_username};{hashlib.sha256(login_password.encode()).hexdigest()}"),daemon=True)
                    recv_thread = threading.Thread(target=recv_msg)
                    print("Sending...")
                    send_thread.start()
                    print("Recving...")
                    recv_thread.start()

                except Exception as e:
                    sever_conection = False
                    print("click_login Error e : ", e)

    else:
        CTkMessagebox(title="Warning", message="Your Disconnected\nFirst Conect To Server", icon="warning")

def click_register():
    def send_msg(msg1,msg2):
        try:
            global register_button
            register_button.configure(state="disabled")
            CLIENT.send(f"{TAG}:{msg1}:{msg2}".encode("ascii"))
            time.sleep(1)
            register_button.configure(state="normal")
        except Exception as e:
            print("\nError Send_msg : ",e)
            global sever_conection
            sever_conection = False
    def recv_msg():
        try:
            global register_button
            ch = register_recv_queue.get()
            if ch == "saved":
                register_username_entry.configure(border_color="#82EE91"), register_psw_entry.configure(border_color="#82EE91")
                CTkMessagebox(title="Success", message="Registered Successfully\nYou can Login Now.", icon="info")

            else:
                CTkMessagebox(title="Warning", message="Invalid Name\nPlease Enter Another name that name is invalid!.", icon="warning")
                register_username_entry.configure(border_color="red"), register_psw_entry.configure(border_color="red")
            time.sleep(1)
            register_button.configure(state="normal")

        except Exception as e:
            print("\nError (register)recv_msg : ",e)
            global sever_conection
            sever_conection = False


    global sever_conection
    register_username = register_username_entry.get().lower().replace(" ","")
    real_register_username = register_username_entry.get()
    register_psw = register_psw_entry.get()
    isdigest_t = False
    for r in register_psw:
        if r.isdigit():
            isdigest_t = True

    if sever_conection:
        if register_username == "":
            register_username_entry.configure(border_color="red")
        else:
            register_username_entry.configure(border_color="#82EE91")
        if register_psw == "":
            register_psw_entry.configure(border_color="red")
        else:
            register_psw_entry.configure(border_color="#82EE91")
            if len(register_psw) > 7 and isdigest_t:
                register_psw_entry.configure(border_color="#82EE91")
                try:
                    ask = CTkMessagebox(title="Configure", message="Are You Sure?",icon="question", option_1="Yes", option_2="No")
                    response = ask.get()
                    if response == "Yes":
                        send_thread = threading.Thread(target=send_msg,args=("register_new", f"{register_username};{real_register_username};{hashlib.sha256(register_psw.encode()).hexdigest()}"),daemon=True)
                        recv_thread = threading.Thread(target=recv_msg)
                        print("Sending...")
                        send_thread.start()
                        print("Recving...")
                        recv_thread.start()

                    print("Done...")                 

                except Exception as e:
                    sever_conection = False
                    print("click register Error e: ",e)
                
            else:
                register_psw_entry.configure(border_color="red")
    else:
        CTkMessagebox(title="Warning", message="Your Disconnected\nFirst Conect To Server", icon="warning")

def popup_conection():
    def connect():
        ip = ip_entry.get()
        port = port_entry.get()
        ip_entry.configure(border_color="red") if ip == "" else ip_entry.configure(border_color="#82EE91")
        port_entry.configure(border_color="red") if port == "" else port_entry.configure(border_color="#82EE91")
        if ip and port:
            try:
                global sever_conection
                global CLIENT
                client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                client.connect((ip, int(port)))
                ip_entry.configure(border_color="#82EE91"), port_entry.configure(border_color="#82EE91")
                CTkMessagebox(title="Success", message="Conected", icon="check")
                IP.set(ip)
                PORT.set(int(port))
                CLIENT = client
                sever_conection = True
                main_recver_t = threading.Thread(target=main_recver, daemon=True)
                main_recver_t.start()
                popup.destroy()        
            except Exception as e:
                ip_entry.configure(border_color="red"), port_entry.configure(border_color="red")
                CTkMessagebox(title="Warning", message=f"Wrong Ip and Port..  \nError Code : {e}", icon="warning")
    def disconnect():
        global sever_conection
        global CLIENT
        sever_conection = False
        try:
            CLIENT.send(f"{TAG}:disconnect:{login_username_entry.get()}".encode("ascii"))
        except:
            CLIENT.send(f"{TAG}:disconnect:None".encode("ascii"))
        CLIENT = None
        popup.destroy()

    popup = ctk.CTkToplevel(w)
    popup.title("Missing Server")
    popup.geometry("350x250+720+410")
    popup.attributes("-topmost", True)

    ctk.CTkLabel(popup, text="Enter Server Details", font=("Arial", 15, "bold")).pack(pady=10)

    ip_entry = ctk.CTkEntry(popup, placeholder_text="Enter IP", width=250)
    if IP.get() != "":
        ip_entry.insert(0, IP.get())
    ip_entry.pack(pady=10)

    port_entry = ctk.CTkEntry(popup, placeholder_text="Enter Port", width=250)
    if PORT.get() != 0:
        port_entry.insert(0, str(PORT.get()))
    port_entry.pack(pady=10)
    
    btn = ctk.CTkButton(popup)
    if sever_conection:
        btn.configure(fg_color="#f05454", hover_color="#2b0f0f", text="Disconect",command=disconnect)
        ip_entry.configure(state="disabled"), ip_entry.configure(fg_color="#838383")
        port_entry.configure(state="disabled"), port_entry.configure(fg_color="#838383")  
    else:
        btn.configure(fg_color="#64B5F6", hover_color="#223344", text="Connect", command=connect)
        ip_entry.configure(state="normal"), ip_entry.configure(fg_color="#ffffff")
        port_entry.configure(state="normal"), port_entry.configure(fg_color="#ffffff")
    btn.pack(pady=20)

def popup_add_acc():
    def add():
        name = name_entry.get()
        if sever_conection:
            if name:
                try:
                    if name == login_username:
                        CTkMessagebox(title="invalid", message=f"Invalid Name", icon="warning")
                    else:
                        CLIENT.send(f"{TAG}:add_frend_try:{name}".encode("ascii"))
                        response = add_frend_recv_queue.get()
                        if response == "invalid":
                            name_entry.configure(border_color="red")
                            CTkMessagebox(title="invalid", message=f"Invalid Name", icon="warning")
                        else:
                            p = True
                            for u in user_butn_wigets:
                                if u == name:
                                    p = False
                            if p:
                                add_user_btn(name)
                            popup.destroy()

                except Exception as e:
                    print("error from add_frend : ",e)

            else:
                name_entry.configure(border_color="red")
        else:
            popup.destroy()

    popup = ctk.CTkToplevel(w)
    popup.title("Add Frend")
    popup.geometry("350x200+720+410")
    popup.attributes("-topmost", True)

    ctk.CTkLabel(popup, text="Enter Frend Name", font=("Impact", 15)).pack(pady=10)
    name_entry = ctk.CTkEntry(popup, placeholder_text="Enter Frend Name", width=250)
    name_entry.pack(pady=10)
    btn = ctk.CTkButton(popup, fg_color="#64B5F6", hover_color="#223344", text="Add Frend",font=("Impact", 16), command=add)
    btn.pack(pady=20)

def popup_abaout(parent):
    about_win = ctk.CTkToplevel(parent)
    about_win.title("About ByteTalk")
    about_win.geometry("400x550")
    about_win.resizable(False, False)
    about_win.configure(fg_color="#F0F8FF") 
    
    about_win.attributes("-topmost", True)
    about_win.grab_set()

    main_frame = ctk.CTkFrame(
        about_win, 
        fg_color="white", 
        corner_radius=25, 
        border_width=2, 
        border_color="#3b81da"
    )
    main_frame.pack(padx=25, pady=25, fill="both", expand=True)

    logo_label = ctk.CTkLabel(
        main_frame, text="ByteTalk", 
        font=ctk.CTkFont(family="Helvetica", size=50, weight="bold"),
        text_color="white",
        fg_color="#3b81da",
        width=100, height=100, corner_radius=50
    )
    logo_label.pack(pady=(30, 10))


    info_text = "Secure Online Chat Application\nSocket & Threading Powered\nDatabase: SQLite3\nSmooth and Clear - GUI\n\nDesigned and developed by a 14-year-old enthusiast\nfocusing on robust networking and \nreal-time data synchronization.\n\nPowerd By - Python"
    ctk.CTkLabel(main_frame, text=info_text, font=("Segoe UI", 13), text_color="#555").pack(pady=10)

    bio_frame = ctk.CTkFrame(main_frame, fg_color="#E1F5FE", corner_radius=15)
    bio_frame.pack(pady=15, padx=30, fill="x")

    ctk.CTkLabel(
        bio_frame, 
        text="Vimitha S | Python inheritance Level", 
        font=("Impact", 17),
        text_color="#003655"
    ).pack(pady=10)

    def open_github():
        webbrowser.open("https://github.com/VimithaProCoding")

    btn = ctk.CTkButton(
        main_frame, text="GitHub Profile", 
        command=open_github,
        fg_color="#006EFF", hover_color="#6FC5FA",
        corner_radius=10,
        font=('Impact', 20)
    )
    btn.pack(pady=20)

def test():
    main_frame2.grid_forget()
    main_frame.grid(row=1, column=1,sticky="nsew",rowspan=2)
    main_frame.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)
    side_frame.grid(row=1, column=0,sticky="nsew")

    msg_frame.grid(row=0, column=0, sticky="nsew", pady=10,padx=10, columnspan=2)
    msg_frame.grid_columnconfigure(0, weight=1), msg_frame.grid_columnconfigure(1, weight=1)
    msg_frame.grid_rowconfigure(0, weight=1)
    auto_load_db_chats()

############################################################################################### Customtkinter ##########################################################################################
try:
    user_img = ctk.CTkImage(dark_image=Image.open(f"{my_path}\\geust.png"), size=(30, 30))
    online_img = ctk.CTkImage(dark_image=Image.open(f"{my_path}\\online.png"),
                              light_image=Image.open(f"{my_path}\\online.png"), size=(28, 28))
    offline_img = ctk.CTkImage(dark_image=Image.open(f"{my_path}\\offline.png"),
                              light_image=Image.open(f"{my_path}\\offline.png"), size=(28, 28))
    abaout_img = ctk.CTkImage(dark_image=Image.open(f"{my_path}\\about.png"),
                              light_image=Image.open(f"{my_path}\\about.png"), size=(28, 28))
except FileNotFoundError:
    CTkMessagebox(title="error", message='ByteTalk files Not Found !\nError Code : images not found', icon="warning")

IP = ctk.StringVar()
PORT = ctk.IntVar()

w.columnconfigure(1, weight=1)
w.rowconfigure(1, weight=1)

# other Frames
top_frame = ctk.CTkFrame(master=w, fg_color="#3b81da", height=50,corner_radius=0)
top_frame.grid(row=0, column=0,sticky="ew", columnspan=2)
top_frame.grid_columnconfigure(1, weight=1)

about_logo = ctk.CTkButton(top_frame, text="", image=abaout_img, width=0, height=0, fg_color='transparent', hover_color='#6493cf', command=lambda: popup_abaout(w))
about_logo.grid(row=0, column=0, ipadx=3)
logo_l = ctk.CTkLabel(top_frame, text="ByteTalk", font=("Impact", 25), text_color="#ffffff")
logo_l.grid(row=0, column=1, padx=0, sticky='w')
logo_l2 = ctk.CTkLabel(top_frame, text=f"{"\t"*8}   Status   :", font=("Impact", 20), text_color="#e0e0e0")
logo_l2.grid(row=0, column=2)

status = ctk.CTkButton(top_frame, text="", font=("Impact", 20), fg_color="transparent", hover_color="#6493cf",width=80, command=popup_conection)
status.grid(row=0, column=3, padx=15)

threade_conection_test = threading.Thread(target=conection_test, daemon=True)
threade_conection_test.start()
side_frame = ctk.CTkScrollableFrame(master=w, width=141, label_text="Online Users", fg_color="#6faeff", corner_radius=0, scrollbar_button_color="#3b81da", scrollbar_button_hover_color="#27538d", label_text_color="#FFFFFF", label_fg_color="#6faeff")
side_frame.grid_forget()

add_acc_btn = ctk.CTkButton(w, text="Add Frend", font=("Impact", 19), text_color="#ffffff", fg_color="#3b81da", hover_color="#27538d",corner_radius=0, height=38, command=popup_add_acc)
side_frame.grid_forget()

class create_side_user_button(ctk.CTkFrame):
    def __init__(self, master, username, **kwargs):
        super().__init__(master, **kwargs)
        def clicked_user():
            try:
                if in_chat_now == self.username:
                        self.name_button.configure(fg_color="#27538d")
                        self.name_buttonimg.configure(fg_color="#27538d")
                else:
                    self.name_button.configure(fg_color="#3b81da")
                    self.name_buttonimg.configure(fg_color="#3b81da")
                self.after(200, clicked_user)
            except: pass
                                

        def clicked_user_btn():
            global in_chat_now
            global msg_frame
            in_chat_now = self.username
            try:
                msg_frames_dict[in_chat_now].configure(label_text=in_chat_now)
            except:
                new_msg_frame1 = create_msg_frame(msg_frame, username)
                msg_frames_dict[username] = new_msg_frame1

        self.username = username = f"{username[0:8]}.." if len(username) >= 11 else username

        self.configure(height=50, fg_color="#5a92f1", corner_radius=0)
        self.grid_columnconfigure(1, weight=1)
        try:
            self.name_buttonimg = ctk.CTkButton(self, text="", font=("Impact", 19), text_color="#ffffff", fg_color="#3b81da", hover_color="#27538d",corner_radius=0,image=user_img, compound="left",width=0,height=0)
            self.name_buttonimg.grid(row=0, column=0, sticky="w")
        except: pass
        self.name_button = ctk.CTkButton(self, text=self.username, font=("Impact", 19), text_color="#ffffff", fg_color="#3b81da", hover_color="#27538d",corner_radius=0, height=38, command=clicked_user_btn)
        self.name_button.grid(row=0, column=1, sticky="w")
        t = threading.Thread(target=clicked_user, daemon=True)
        t.start()
        self.pack(pady=0, padx=0, fill="x")

def add_user_btn(username):
    new_btn = create_side_user_button(side_frame, username)
    found = True
    for btn in user_butn_wigets:
        if btn == username:
            found = False
    if found:
        user_butn_wigets[username] = new_btn
def remove_user_btn(username):
    if username in user_butn_wigets:
        widget = user_butn_wigets[username]
        widget.destroy() 
        del user_butn_wigets[username]
        print(f"{username} widget removed from UI")

#add_user_btn("You")
# msg frames
main_frame = ctk.CTkFrame(w,corner_radius=0, fg_color="#d5e2f5")
main_frame.grid(row=1, column=1,sticky="nsew",rowspan=2)
main_frame.rowconfigure(0, weight=1)
main_frame.columnconfigure(0, weight=1)
main_frame.grid_forget()

msg_frame = ctk.CTkFrame(main_frame, fg_color="#fefefe",corner_radius=0, )
msg_frame.grid(row=0, column=0, sticky="nsew", pady=10,padx=10, columnspan=2)


def save_chat(account, l_or_r, msg):
    have = True
    for k in chat_messages:
        if k == account:
            have = False
            break
    if have:
        chat_messages[account] = []

    chat_messages[account].append(f"{l_or_r}:{msg}")

    try:
        CLIENT.send(f"{TAG}|auto_save_chat|{str(json.dumps(chat_messages))};{login_username}".encode("ascii"))
        print(f"sended msges to DATA BASE")

    except Exception as e:
        print("Error in save_chat : ", e)

def auto_load_db_chats():
    def apect_chat():
        if not chat_messages == {}:
            for acount in chat_messages:
                global in_chat_now
                in_chat_now = acount

                btn_ = True
                for u in user_butn_wigets:
                    if u == acount:
                        btn_ = False
                if btn_:
                    add_user_btn(acount)
                    new_msg_frame1 = create_msg_frame(msg_frame, acount)
                    msg_frames_dict[acount] = new_msg_frame1

                for msg in chat_messages[acount]:
                    msg = msg.split(":")
                    display_msg(msg[1], "me" if msg[0] == "right" else "left", "auto")
            in_chat_now = "You"
    
    global chat_messages
    global income_messages
    if chat_messages == {} or user_butn_wigets == {}:
        add_user_btn("You")
        new_msg_frame1 = create_msg_frame(msg_frame, "You")
        msg_frames_dict["You"] = new_msg_frame1

    try:
        CLIENT.send(f"{TAG}:auto_load_chat:{login_username}".encode("ascii"))
        recv_str = auto_load_chat_recv_queue.get()
        chat_messages = json.loads(recv_str)
        #printc(f"[bold green]auto load (chat_messages) : {chat_messages}")
        apect_chat()

    except Exception as e:
        print("Error in auto_load_db_chat : ", e)

class create_msg_frame(ctk.CTkScrollableFrame):
    def __init__(self, master, name, **kwargs):
        super().__init__(master, **kwargs)
        def grid_grid():
            if in_chat_now == name:
                self.grid_columnconfigure(1, weight=1)
                self.grid(row=0, column=0, sticky="nsew", pady=10,padx=10, columnspan=2)
            else:
                self.grid_forget()
            self.after(300, grid_grid)

        self.configure(height=50, fg_color="#fefefe",label_text=name, corner_radius=0, scrollbar_button_color="#3b81da", scrollbar_button_hover_color="#27538d", label_text_color="#FFFFFF", label_fg_color="#0f4a96", label_font=("Impact", 27))
        t = threading.Thread(target=grid_grid, daemon=True)
        t.start()

class class_display_msg(ctk.CTkFrame):
    def __init__(self, master, msg, to, auto, **kwargs):
        super().__init__(master, **kwargs)

        self.configure(height=50, fg_color="#fefefe", corner_radius=36)
        self.grid_columnconfigure(0, weight=1)

        if len(msg) >= 31 and len(msg) <= 60:
            self.msg = f"{msg[0:30]}\n{msg[30:len(msg)]}"
        elif len(msg) >= 1 and len(msg) <= 30:
            self.msg = msg
        elif len(msg) >= 61 and len(msg) <= 90:
            self.msg = f"{msg[0:30]}\n{msg[30:60]}\n{msg[60:len(msg)]}"
        elif len(msg) >= 91 and len(msg) <= 120:
            self.msg = f"{msg[0:30]}\n{msg[30:60]}\n{msg[60:90]}\n{msg[90:len(msg)]}"
        elif len(msg) >= 121 and len(msg) <= 150:
            self.msg = f"{msg[0:30]}\n{msg[30:60]}\n{msg[60:90]}\n{msg[90:120]}\n{msg[120:len(msg)]}"
        elif len(msg) >= 151 and len(msg) <= 180:
            self.msg = f"{msg[0:30]}\n{msg[30:60]}\n{msg[60:90]}\n{msg[90:120]}\n{msg[120:150]}\n{msg[150:len(msg)]}"
        elif len(msg) >= 181 and len(msg) <= 210:
            self.msg = f"{msg[0:30]}\n{msg[30:60]}\n{msg[60:90]}\n{msg[90:120]}\n{msg[120:150]}\n{msg[150:180]}\n{msg[180:len(msg)]}"
        else:
            self.msg = f"Masseg Is Too Long.. only(1-210)"

        self.msg_label = ctk.CTkLabel(self, text=self.msg, font=("Comic Sans MS3", 30, "bold"), text_color="#FFFFFF",corner_radius=36, height=38)

        if to == "me":
            self.msg_label.grid(row=0, column=1, sticky="w", pady=5, padx=5, ipady =10)
            self.msg_label.configure(fg_color="#7ab1f8")
        else:
            self.msg_label.grid(row=0, column=0, sticky="w", pady=5, padx=5, ipady=10)
            self.msg_label.configure(fg_color="#143868")# fg_color="#143868

        self.pack(pady=0, padx=0, fill="x",)
        master.update_idletasks()
        master._parent_canvas.yview_moveto(1.0)

def display_unkown_msg():
    while True:
        if LOGIN and sever_conection:
            raw_recv_msg = income_msg_recv_queue.get()
            if raw_recv_msg:
                from_, msg_ = raw_recv_msg.split('@|@')
                have = True
                for w in user_butn_wigets:
                    if w == from_:
                        have = False
                if have:
                    add_user_btn(from_)
                    new_msg_frame1 = create_msg_frame(msg_frame, from_)
                    msg_frames_dict[from_] = new_msg_frame1

                new_msg_label = class_display_msg(msg_frames_dict[from_], msg_, 'left', 'auto')
                msg_frame_label[msg_] = new_msg_label

def send_msg(from_, to_, msg_):
    try:
        CLIENT.send(f'{TAG}:{'send_msg'}:{from_};{to_};{msg_}'.encode('ascii'))
    except Exception as e:
        print('Error in send_msg : ', e)

def display_msg(msg, to, auto):
    if chat_messages == {}:
        new_msg_frame1 = create_msg_frame(msg_frame, "You")
        msg_frames_dict["You"] = new_msg_frame1

    new_msg_label = class_display_msg(msg_frames_dict[in_chat_now], msg, to, auto)
    msg_frame_label[msg] = new_msg_label

def send_totextbox(event=None):
    msg = msg_entry.get().replace(':', '?').replace(';', '?').replace('|', '?')
    if msg:
        msg_entry.delete("0","end")
        display_msg(msg, 'me', "not auto")
        save_chat(in_chat_now, 'right', msg)
        if in_chat_now != 'You':
            send_msg(login_username, in_chat_now, msg)


msg_entry = ctk.CTkEntry(main_frame, placeholder_text="Type your message...", fg_color="#fefefe", width=570, height=45, border_width=1,border_color="#dde4ec", font=("Comic Sans MS3",15, "bold"), text_color="#232933")
msg_entry.grid(row=1, column=0,pady=10)
msg_entry.bind('<Return>', send_totextbox)
msg_btn = ctk.CTkButton(main_frame, text="Send",font=("Impact", 20), fg_color="#3a81dc", border_width=1, border_color="#2870cf", text_color="#fefeff", command=send_totextbox)
msg_btn.grid(row=1, column=1,padx=10)

# login/register page...
main_frame2 = ctk.CTkFrame(w,corner_radius=0, fg_color="#66a5f8")
main_frame2.grid(row=1, column=1,sticky="nsew")
main_frame2.rowconfigure(0, weight=1)
main_frame2.columnconfigure(0, weight=1)

tabview = ctk.CTkTabview(main_frame2, width=950, height=600, 
                                      fg_color="#F0F3F7",
                                      segmented_button_fg_color="#F0F3F7",
                                      segmented_button_selected_color="#64B5F6",
                                      segmented_button_selected_hover_color="#4F79A2",
                                      segmented_button_unselected_color="#F0F3F7",
                                      segmented_button_unselected_hover_color="#E0E5EC",
                                      text_color="#333333",
                                      corner_radius=15)
tabview.grid(row=0, column=0,pady=20, padx=20)
tabview._segmented_button.configure(font=("Arial", 23, "bold"), height=50)
login_tab = tabview.add(" LOGIN ")
login_tab.grid_rowconfigure(0, weight=1)
login_tab.grid_columnconfigure(0, weight=1)
tabview.set(" LOGIN ")
register_tab = tabview.add("REGISTER")
register_tab.grid_rowconfigure(0, weight=1)
register_tab.grid_columnconfigure(0, weight=1)


label = ctk.CTkLabel(login_tab, text="Welcome To,\nLOGIN", font=("Impact", 22), text_color="#333333")
label.grid(row=0, column=0, pady=(10,5), padx=10)

labe2 = ctk.CTkLabel(login_tab, text="Name", font=("Arial", 14, "bold"), text_color="#333333")
labe2.grid(row=1, column=0, pady=(10,5), padx=10)

login_username_entry = ctk.CTkEntry(login_tab, placeholder_text="Enter your username", width=250, height=35, corner_radius=10,
                                                 fg_color="white", text_color="#333333", border_color="#B0C4DE")
login_username_entry.grid(row=2, column=0, pady=(0,10), padx=10)

label2 = ctk.CTkLabel(login_tab, text="Password", font=("Arial", 14, "bold"), text_color="#333333")
label2.grid(row=3, column=0, pady=(10,5), padx=10)

login_password_entry = ctk.CTkEntry(login_tab, placeholder_text="Enter your password", show="*", width=250, height=35, corner_radius=10,
                                                 fg_color="white", text_color="#333333", border_color="#B0C4DE")
login_password_entry.grid(row=4, column=0, pady=(0,20), padx=10)

ls_psw = ctk.CTkCheckBox(login_tab, text="Show Password", font=("Arial", 10), text_color="#333333", command=lambda: login_password_entry.configure(show="" if ls_psw.get() else "*"))
ls_psw.grid(row=5, column=0, pady=(0,20), padx=10)

login_button = ctk.CTkButton(login_tab, text="LOGIN", width=200, height=40, corner_radius=10,fg_color="#64B5F6", hover_color="#4F79A2", font=("Arial", 16, "bold"), text_color="white",command=click_login)
login_button.grid(row=6, column=0, pady=10, padx=10)
l_em = ctk.CTkLabel(login_tab, text="\n", font=("Arial", 50))
l_em.grid(row=7, column=0, pady=5, padx=10)


label3 = ctk.CTkLabel(register_tab, text="Welcome To,\nREGISTER", font=("Impact", 22), text_color="#333333")
label3.grid(row=0, column=0, pady=(10,5), padx=10)

labe132 = ctk.CTkLabel(register_tab, text="New Name", font=("Arial", 14, "bold"), text_color="#333333")
labe132.grid(row=1, column=0, pady=(10,5), padx=10)

register_username_entry = ctk.CTkEntry(register_tab, placeholder_text="Enter Your Name", width=250, height=35, corner_radius=10,fg_color="white", text_color="#333333", border_color="#B0C4DE")
register_username_entry.grid(row=2, column=0, pady=(0,10), padx=10)

label4 = ctk.CTkLabel(register_tab, text="New Password", font=("Arial", 14, "bold"), text_color="#333333")
label4.grid(row=3, column=0, pady=(10,5), padx=10)

register_psw_entry = ctk.CTkEntry(register_tab, placeholder_text="Enter Strong Password", width=250, height=35, corner_radius=10,fg_color="white", text_color="#333333", border_color="#B0C4DE", show="*")
register_psw_entry.grid(row=4, column=0, pady=(0,20), padx=10)

cb_newpsw = ctk.CTkCheckBox(register_tab, text="Show Password", font=("Arial", 10), text_color="#333333", command=lambda: register_psw_entry.configure(show="" if cb_newpsw.get() else "*"))
cb_newpsw.grid(row=5, column=0, pady=(0,20), padx=10)

register_button = ctk.CTkButton(register_tab, text="REGISTER", width=200, height=40, corner_radius=10,fg_color="#649FF6", hover_color="#4F79A2", font=("Arial", 16, "bold"), text_color="white",command=click_register)
register_button.grid(row=6, column=0, pady=10, padx=10)
l_em = ctk.CTkLabel(register_tab, text="\n", font=("Arial", 50))
l_em.grid(row=7, column=0, pady=5, padx=10)



def on_closing():
    msg = CTkMessagebox(title="Exit?", message="Close Confirm?",
                        icon="question", option_1="Yes", option_2="No")
    
    response = msg.get()
    
    if response == "Yes":
        w.destroy()
    else:
        pass

popup_conection()
w.protocol("WM_DELETE_WINDOW", on_closing)
w.mainloop()
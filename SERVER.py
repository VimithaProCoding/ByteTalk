import os, json, time, socket, threading, hashlib, sqlite3
from rich.console import Console
from rich.panel import Panel
from rich import print as printc
console = Console()

my_path = os.path.dirname(os.path.abspath(__file__))

if not os.path.exists(f'{my_path}\\Server DB'):
    os.mkdir(f'{my_path}\\Server DB')

if not os.path.exists(f'{my_path}\\Server DB\\DataBase.db'):
    db = sqlite3.connect(f'{my_path}\\Server DB\\DataBase.db')
    cmd = db.cursor()
    db.execute('PRAGMA journal_mode=WAL;')
    cmd.execute('''
    CREATE TABLE IF NOT EXISTS clients(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    real_username TEXT,
                    password TEXT,
                    chat_messages TEXT                 
    )
    ''')
    db.close()
    printc('[bold green]New DataBase Created...')


my_path = os.path.dirname(os.path.abspath(__file__))
with open(f'{my_path}\\settings.json') as f:
    data = json.load(f)
    IP = data['IP']
    PORT = data['PORT']
    clients = []
    Members = []
    online_users = []
    online_users_clients = {}
    TOKEN = hashlib.sha256(data['TOKEN'].encode()).hexdigest()

def broadcast(message, _client):
    for client in clients:
        if client != _client:
            try:
                client.send(message)
            except:
                clients.remove(client)

def handle_client(client, user_name):
    global user_count
    dc_mode = 0
    while True:
        try:
            msg = client.recv(1024).decode('ascii')
            if not msg:
                dc_mode += 1
                if dc_mode >= 150:
                    clients.remove(client)
                    Members.remove(user_name)
                    try:
                        online_users.remove(u_name)
                        del online_users_clients[u_name]
                    except:
                        printc('[bold red]pass remove u_name')
                    user_count -= 1
                    client.close()
                    printc(f"no conction yet. \n[bold red]{user_name} Disconected")
                    break

            split_msg = msg.split(':')
            split_msg2 = msg.split('|')
            check = True if split_msg[0] != '' and split_msg[1] != '' and split_msg[2] != '' and len(split_msg) == 3 else False          
            if check and split_msg[0] == TOKEN:

                if split_msg[1] == 'send_msg':
                    printc(f'[bold yellow]try to send_msg')
                    from_, to_, msg_ = split_msg[2].split(';')
                    printc(Panel(f'[bold blue]From: {from_}\nTo: {to_}\nMsg: {msg_}',title='Sending Message'))
                    user_online = False
                    for u in online_users_clients:
                        if u == to_:
                            user_online = True
                    if user_online:
                        try:
                            online_users_clients[to_].send(f'income_msg|@|{from_}@|@{msg_}'.encode('ascii'))
                        except Exception as e:
                            printc('[bold red] Its not working yet? msg online labba')                    
                    try:
                        db = sqlite3.connect(f'{my_path}\\Server DB\\DataBase.db', timeout=10)
                        cmd = db.cursor()
                        cmd.execute('SELECT * FROM clients WHERE username = ?', (to_,))
                        user_send_data = cmd.fetchone()
                        user_chat_msg = json.loads(user_send_data[4])
        
                        have = False
                        for k in user_chat_msg:
                              if k == from_:
                                have = True
                                break
                        if not have:
                              user_chat_msg[from_] = []
                        user_chat_msg[from_].append(f'{'left'}:{msg_}')
                        db.close()

                        try:
                            db = sqlite3.connect(f'{my_path}\\Server DB\\DataBase.db', timeout=10)
                            cmd = db.cursor()
                            cmd.execute('UPDATE clients SET chat_messages = ? WHERE username = ?', (json.dumps(user_chat_msg), to_))
                            db.commit()
                            printc('[bold yellow] updated chat_messages')
                        except Exception as e:
                            printc('[bold red]Error in send_msg(part II) : ',e)
    
                    except Exception as e:
                        printc('[bold red]Error in send_msg(part I) : ',e)
                    finally:
                        db.close()


                if split_msg[1] == 'auto_load_chat':
                    printc(f'[bold yellow]try to get user messages : {split_msg[2]}')
                    db = sqlite3.connect(f'{my_path}\\Server DB\\DataBase.db', timeout=10)
                    cmd = db.cursor()
                    try:
                        cmd.execute('SELECT * FROM clients WHERE username = ?',(split_msg[2],))
                        user_details = cmd.fetchone()
                        client.send(f'{'auto_load_chat'}|@|{user_details[4]}'.encode('ascii'))

                    except Exception as e:
                        printc(f'[bold red]Error in try auto_load_chat : ',e)
                    finally:
                        db.close()                    

                if split_msg[1] == 'add_frend_try':
                    printc(f'[bold yellow]try add_frend\n {split_msg[2]}')
                    frend_name = split_msg[2]

                    db = sqlite3.connect(f'{my_path}\\Server DB\\DataBase.db', timeout=10)
                    cmd = db.cursor()
                    try:
                        cmd.execute('SELECT * FROM clients WHERE username = ?',(frend_name,))
                        user_details = cmd.fetchone()
                        if user_details == None:
                            client.send('add_frend_try|@|invalid'.encode('ascii'))
                        else:
                            client.send('add_frend_try|@|valid'.encode('ascii'))
                    except Exception as e:
                        printc(f'[bold red]Error in try add_frend : ',e)
                    finally:
                        db.close()

                if split_msg[1] == 'test':
                    printc(Panel(f"[bold yellow][{user_name}]: {split_msg[2]}",title='TEST'))

                if split_msg[1] == 'disconnect':
                    if split_msg[2] != 'None':
                        try:
                            online_users.remove(split_msg[2])
                            del online_users_clients[split_msg[2]]
                        except:
                            printc('[bold red]pass remove u_name')
                        clients.remove(client)
                        Members.remove(user_name)
                        user_count -= 1
                        client.close()
                        printc(f"[bold red]{user_name} Disconected") 
                        break

                    else:
                        clients.remove(client)
                        Members.remove(user_name)
                        user_count -= 1
                        client.close()
                        printc(f"[bold red]{user_name} Disconected") 
                        break
                if split_msg[1] == 'login_check':
                    printc('[bold yellow]Trying to login_check')
                    u_name, u_psw = split_msg[2].split(';')
                    printc(f'[bold yellow] un : {u_name}\n np : {u_psw}')

                    db = sqlite3.connect(f'{my_path}\\Server DB\\DataBase.db')
                    cmd = db.cursor()
                    cmd.execute('SELECT * FROM clients WHERE username = ?',(u_name,))
                    user_data = cmd.fetchone()

                    try:
                        
                        if user_data != None and u_psw == user_data[3]:
                            user_online_name_check = True
                            for u in online_users:
                                if u == u_name:
                                    user_online_name_check = False
                            if user_online_name_check:
                                client.send(f'login_check|@|correct'.encode('ascii'))
                                online_users.append(u_name)
                                online_users_clients[u_name] = client
                                print('='*15)
                                print(online_users)
                                print(clients)
                                print(Members)
                                print('='*15)
                                
                            else:
                                client.send('login_check|@|incorrect2'.encode('ascii'))
                                
                        else:
                            client.send('login_check|@|incorrect'.encode('ascii'))
                            print(user_data)
                    except:
                        printc("[bold red]Login_check Can't send.")
                    finally:
                        db.close()

                if split_msg[1] == 'register_new':
                    printc('[bold yellow]Trying to register_new')
                    ru_name, real_ru_name, ru_psw = split_msg[2].split(';')
                    printc(f'[bold yellow] un : {ru_name}\n np : {ru_psw}')

                    db = sqlite3.connect(f'{my_path}\\Server DB\\DataBase.db', timeout=10)
                    cmd = db.cursor()
                    try:
                        cmd.execute('INSERT INTO clients (username, real_username, password, chat_messages) VALUES (?, ?, ?, ?)', (ru_name, real_ru_name, ru_psw, "{}"))
                        db.commit()
                        client.send('register_new|@|saved'.encode('ascii'))
                        printc('[bold green]New User Added to DataBase...')
                    except sqlite3.IntegrityError:
                        client.send('register_new|@|allready_have'.encode('ascii'))
                    finally:
                        db.close()

            else:
                if split_msg2[1] == 'auto_save_chat':
                    messages, username_ = split_msg2[2].split(';')
                    db = sqlite3.connect(f'{my_path}\\Server DB\\DataBase.db', timeout=10)
                    cmd = db.cursor()
                    try:
                        cmd.execute('UPDATE clients SET chat_messages = ? WHERE username = ?', (messages, username_))
                        db.commit()
                        printc('[bold yellow] updated chat_messages')

                    except Exception as e:
                        printc(f'[bold red]Error in try auto_save_chat : ',e)
                    finally:
                        db.close()


        except sqlite3.OperationalError as oe:
            printc(f'[bold red] DATABASE ERROR : {oe}')
    
        except Exception as e:
            if e == 'list index out of range':
                printc(f'[bold red] Split Error')
            else:
                printc(f'[bold red] ERROR EEE : {e}')

            clients.remove(client)
            Members.remove(user_name)
            try:
                online_users.remove(u_name)
                del online_users_clients[u_name]
            except:
                printc('[bold red]pass remove u_name')
            user_count -= 1
            client.close()
            printc(f"[bold red]{user_name} Disconected")
            break


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.bind(('0.0.0.0', 5050))
except Exception as e:
    printc(f'[bold red]Error Code : {e}')
    printc(f'[blue]Our Server Hacked By [reverse] Hacker ')
    input('press any key to exit...')
    exit()

server.listen()

user_count = 1

printc(Panel('[italic cyan]SERVER - HOST',border_style='cyan'))

with console.status('',spinner='arc',spinner_style='bold blue') as s:
    s.update('[bold blue]Server Starting...')
    s.start()
    time.sleep(1)
    s.stop()
printc(f'[bold green]Server Started...\nPort : {PORT}')

while True:
    print()
    if user_count == 1:
        printc(f'[bold yellow]Waiting for Clients..')
    client, addr = server.accept()

    user_n = f"User {user_count}"

    clients.append(client) 
    Members.append(user_n)

    printc(f"[bold green]{user_n} Joined To Server ({addr})")

       
    thread = threading.Thread(target=handle_client, args=(client, user_n))
    thread.start()
    user_count += 1
    


    #printc('[bold red]Incorrect Token.')
    #printc(f'[bold red]{user_count} Removed From Server.')
    #client.close()


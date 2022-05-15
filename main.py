import socket
import asyncio

from login import LRform
from commands import Executor

# Connection Data
host = ''
port = 4000


# Lists For Clients and Their Nicknames
clients = []
nicknames = []

# Sending Messages To All Connected Clients
async def broadcast(nickname, message):
    loop = asyncio.get_event_loop()
    msg = nickname + message.decode('ascii')
    for client in clients:
        await loop.sock_sendall(client, msg.encode('ascii'))

async def handle(client, login):
    loop = asyncio.get_event_loop()
    cmd = Executor(login)
    while True:
        try:
            index = clients.index(client)
            nickname = nicknames[index] + ": "
            # Broadcasting Messages
            message = (await loop.sock_recv(client, 1024)).decode('ascii').strip()
            if message == "":
                continue
            if message[0] == "!":
                if cmd.checkPerms(0) == "1":
                    message = str(message[1:]) + "\n"
                    await broadcast(nickname, message.encode('ascii'))
                else:
                    await loop.sock_sendall(client, 'You not have permissions to chat\n'.encode('ascii'))
            else:
                if not cmd.checkCommand(message):
                    await loop.sock_sendall(client, 'Not correct command! For see command list write "help"\n'.encode('ascii'))
                else:
                    msg = cmd.makeCommand(message) + "\n"
                    if msg[0] == "c":
                        match msg[1]:
                            case "0": 1 / 0 # Error for quit =)
                    await loop.sock_sendall(client, msg.encode('ascii'))            
        except Exception as err:
            print(err)
            # Removing And Closing Clients
            print("{} disconnected!".format(client.getpeername()))
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            await broadcast("SERVER: ", '{} left!\n'.format(nickname).encode('ascii'))
            nicknames.remove(nickname)
            cmd.stop()
            break

# Receiving / Listening Function
async def receive():
    # Starting Server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    server.setblocking(False)

    loop = asyncio.get_event_loop()
    
    while True:
        form = LRform()
        cmd = None
        # Accept Connection
        client, address = await loop.sock_accept(server)
        print("Connected with {}".format(str(address)))
        
        # Has account or not
        successLogin = False
        hasAcc = ""
        login = ""
        nickname = ""
        password = ""
        try:
            while True:
                client.send('Has account? [y/n] '.encode('ascii'))
                hasAcc = (await loop.sock_recv(client, 1024)).decode('ascii').strip()
                if hasAcc in "yes" or hasAcc in "not":
                    break
            while not successLogin:
                if hasAcc in "not":
                    client.send('Your login: '.encode('ascii'))
                    login = (await loop.sock_recv(client, 1024)).decode('ascii').strip()
                    client.send('Your nickname: '.encode('ascii'))
                    nickname = (await loop.sock_recv(client, 1024)).decode('ascii').strip()
                    client.send('Your password: '.encode('ascii'))
                    password = (await loop.sock_recv(client, 1024)).decode('ascii').strip()
                    successLogin = form.registration(login, nickname, password)
                    if not successLogin:
                        msg = "Login {} already used\n".format(login)
                        client.send(msg.encode('ascii'))
                elif hasAcc in "yes":
                    client.send('Your login: '.encode('ascii'))
                    login = (await loop.sock_recv(client, 1024)).decode('ascii').strip()
                    client.send('Your password: '.encode('ascii'))
                    password = (await loop.sock_recv(client, 1024)).decode('ascii').strip()
                    successLogin, nickname = form.login(login, password)
                    if not successLogin:
                        client.send('Not correct login or password\n'.encode('ascii'))
            cmd = Executor(login)

            if cmd.checkPerms(1) == "0":
                client.send('This account has banned\n'.encode('ascii'))
                print("{} disconnected!".format(address))
                form.stop()
                client.close()
                continue
        except Exception as err:
            print(err)
            print("{} disconnected!".format(address))
            form.stop()
            client.close()
            continue

        nicknames.append(nickname)
        clients.append(client)

        # Print And Broadcast Nickname
        print("Nickname is", nickname)
        client.send('Connected to server!\n'.encode('ascii'))
        msg = str(nickname) + " joined!\n"
        await broadcast("SERVER: ", msg.encode('ascii'))

        form.stop()

        loop.create_task(handle(client, login))

if __name__ == "__main__":
    print("---=== SERVER START ===---")
    print("Host:", host)
    print("Port:", port)
    asyncio.run(receive())

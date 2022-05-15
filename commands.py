import sqlite3

# Permissions: "p000000" (default: "p100000")
# \/ index
# 0. p (NOT TOUCH INDEX 0!!!)
# 1. Chat 
# 2. Unban
# 3. Can ban users
# 4. Can mute users
# 5. Other
# 6. Other
#
# 0 - false; 1 - true
# -------------------------------------------
# Codes: "c0-[arg(optional)]" (example: "c0")
# 0. quit

class Executor():
    
    commands = [    # Perms to change user perms \/
            "help",      # print all commands
            "ban",       # ban user,     p3 == 1, 
            "quit",      # quit from server
            "unban",     # unban user,        p3 == 1
            "mute",      # mute user,         p4 == 1
            "unmute",    # unmute user,       p4 == 1
            ]

    def __init__(self, login):
        self.conn = sqlite3.connect("databases/accounts")
        self.cursor = self.conn.cursor()
        self.login = login
    
    def checkPerms(self, perm):
        self.cursor.execute("SELECT * FROM users WHERE name = ?", (self.login, ))
        perms = self.cursor.fetchone()
        return str(perms[3])[perm + 1]
    
    def checkCommand(self, command):
        command = command.partition(" ")[0]
        if command in self.commands:
            return True
        return False

    def makeCommand(self, command):
        commandCopy = command
        arguments = commandCopy.partition(" ")[2]
        command = command.partition(" ")[0]
        index = self.commands.index(command)
        match index:
            # help
            case 0:
                msg = str(self.commands)
                return msg
            # ban
            case 1:
                if self.checkPerms(3) == "1":
                    print("User", arguments, "bunned by", self.login)
                    msgs = [
                            "User {} not found!".format(arguments),
                            "User {} already banned!".format(arguments),
                            "User {} bunned success!".format(arguments)
                            ]
                    return self.changePerm(arguments, 2, False, msgs)
                else:
                    msg = "You dont have permissions for use this command!"
                    return msg
            # quit
            case 2:
                return "c0"
            # unban
            case 3:
                if self.checkPerms(3) == "1":
                    print("User", arguments, "unbunned by", self.login)
                    msgs = [
                            "User {} not found!".format(arguments),
                            "User {} already unbanned!".format(arguments),
                            "User {} unbunned success!".format(arguments)
                            ]
                    return self.changePerm(arguments, 2, True, msgs)
                else:
                    msg = "You dont have permissions for use this command!"
                    return msg
            # mute
            case 4:
                if self.checkPerms(4) == "1":
                    print("User", arguments, "muted by", self.login)
                    msgs = [
                            "User {} not found!".format(arguments),
                            "User {} already muted!".format(arguments),
                            "User {} muted success!".format(arguments)
                            ]
                    return self.changePerm(arguments, 1, False, msgs)
                else:
                    msg = "You dont have permissions for use this command!"
                    return msg
            # unmute
            case 5:
                if self.checkPerms(4) == "1":
                    print("User", arguments, "unmuted by", self.login)
                    msgs = [
                            "User {} not found!".format(arguments),
                            "User {} already unmuted!".format(arguments),
                            "User {} unmuted success!".format(arguments)
                            ]
                    return self.changePerm(arguments, 1, True, msgs)
                else:
                    msg = "You dont have permissions for use this command!"
                    return msg

    def changePerm(self, user, perm, value, msgs):
        self.cursor.execute("SELECT permissions FROM users WHERE name = ?", (user, ))
        banUserPerms = self.cursor.fetchone()[0]
        if banUserPerms == None:
            return msgs[0]
        elif banUserPerms[perm] == value:
            return msgs[1]
        list1 = list(banUserPerms)
        list1[perm] = str(int(value))
        str1 = "".join(list1)
        self.cursor.execute("UPDATE users SET permissions = ? WHERE name = ?", (str1, user, ))
        self.conn.commit()
        return msgs[2]

    def stop(self):
        self.conn.close()


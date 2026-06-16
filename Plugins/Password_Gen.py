from random import shuffle, choice
import string

from src.MiddleManKit.MiddleMan import *
util.build()

characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
ask = Render("How long do you want your password to be", 'Password Generator').Input()
length = int(ask)
shuffle(characters)
password = []
for i in range(length):
    password.append(choice(characters))
password_str = ''.join(str(e) for e in password)
# RD.CommandSay(answer=("".join(password)), color='OKGREEN')
password = ''.join(password)
Render(f'Your Password Is: {password}').Push()
Render("Would You like to export the password to a text file").Choice()
if 'yes' in Render.Quest_result.lower():
    with open(f"{Data().get_base_folder()}/../password.txt", "w") as f:
        f.write(password_str)
    Render('The File Is Saved', 'Password Generator').Push()
    from subprocess import call 
    file_to_show = f"{Render().get_base_folder()}/../Password.txt"
    call(["open", "-R", file_to_show])
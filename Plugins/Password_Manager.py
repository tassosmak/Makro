import json, os
from src.MiddleManKit.MiddleMan import *
util.build()

class PasswordManager:
    
    def __init__(self):
        self.file_path = f'{Data().get_base_folder()}/../Plugins/src/pwdfile.json'
        self.username = str
        self.password = str
        self.filename = str
        
    def manage_file(self, name: str, username: str, password: str):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as recover:
                try:
                    data = json.load(recover)
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        data[name] = {
            "Name": username,
            "Password": password
        }

        with open(self.file_path, 'w') as recover:
            json.dump(data, recover, indent=4)

                                                                                                                                                                                         
    def add_password(self):
        self.filename = Render('Give a name for the login').Input()
        self.username = Render("Type the Username Of the Passwords You Want to Add").Input()
        
        self.password = Render("Type the Passwords You Want to Add").Input()
        correct_pwd = False
        while not correct_pwd:
            confirm_password = Render("Confirm the Password").Input()
            if confirm_password == self.password:
                correct_pwd = True
            else:
                Render("Passwords do not match, please try again.").Info()
        self.password = Cryptography(self.password).Encrypt()
        
        self.manage_file(self.filename, self.username, self.password)

    
    def view_passwords(self):
        correct_name = False
        while correct_name == False:
            self.filename = Render("Enter the name of the Usesname/Password Combo you want to view").Input()
            print(self.filename)
            try:
                self.username = JSON(self.file_path).json_read(self.filename, 'Name')
                self.password = JSON(self.file_path).json_read(self.filename, 'Password')
                correct_name = True
                Render(f"Your Username is: {self.username} and Password is: {Cryptography(self.password).decryptor()}").Info()
            except FileNotFoundError:
                Render("Password file not found.").Info()
            except:
                correct_name = False
                
    def del_login(self):
        correct_name = False
        while not correct_name:
            array = Render("Enter the name of the login you want to delete").Input()
            if not array.lower() == 'exit':
                try:
                    JSON(self.file_path).json_delete(array)
                    correct_name = True
                except KeyError: Render("Login not found. Please try again.").Info()
            else:
                correct_name = True
                

    def greet(self):
        Render("Welcome to the Makro Password Manager\nWhat would you like to do?").b3_Choice(Button1='Delete Login', Button2='View Login', Button3='New Login')
        ask = Render.Quest_result.lower().strip(' ')
        if ask.lower().strip(' ') == 'new login':
            self.add_password()
        elif ask.lower().strip(' ') == 'view login':
            self.view_passwords()
        elif ask.lower().strip(' ') == 'delete login':
            self.del_login()
            

        
if __name__ == "__main__":
    passwd = PasswordManager()
    passwd.greet()
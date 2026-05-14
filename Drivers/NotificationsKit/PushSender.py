from Makro.Drivers.NotificationsKit.ntfpy import NTFYServer, NTFYUser, NTFYClient, NTFYPushMessage, NTFYViewAction
from Makro.MakroCore.RendererKit import Renderer as RD
from Makro.MakroCore.SystemCalls import break_after
from Makro.MakroCore import flags
from Makro.MakroCore.CryptographyKit import utils



class Notifications():
    
    def __init__(self):
         pass
    
    @break_after(3)
    def Sender(self, content):
        self.server = NTFYServer("http://192.168.1.63:80")
        self.user = NTFYUser("tassosmak", "8596")
        self.client = NTFYClient(self.server, "PyTerminal_Information_System", self.user)
        self.action = NTFYViewAction("Github Link", "https://www.github.com/tassosmak/pyterminal")
        self.message = NTFYPushMessage(content)
        self.message.addAction(self.action)
        self.message.title = flags.Default_text
        # self.message.addTag("warning")
        self.client.send_message(self.message)
        return content

    def Code_Sender(self, num=4):
            self.code = utils._gen_safe_password(num)
            self.Sender(self.code)
            return self.code
        
    def adv_auth():
        """
        Advanced Authorization Method
        - It sends a code to the user phone to make sure that its him doing the task
        - If the code is inputed correct it returns True
        """
        if not flags.MODE == "9":
            if not flags.safe_md:
                verified = False
                try:
                    code = Notifications().Code_Sender()
                except:
                    RD.CommandShow(msg='This action is unavailable at the moment').Show('WARNING')
                
                while not verified:
                    ask_code = RD.CommandShow('Check The Code We Sent You: ', "Advanced Auth").Input()
                    if ask_code == code:
                        return True
            else:
                RD.CommandShow("This action is unavailable at the moment").Show("WARNING")
        else: return True
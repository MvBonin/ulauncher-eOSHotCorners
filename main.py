import json
import os
import os.path
import pathlib
import json
from gi.repository import Notify
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.event import SystemExitEvent
from ulauncher.api.shared.event import ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
import subprocess





##on init read hot corners
##maybe event for quit, to revert hot corners

##or write hot corners in file

##function to get current hot corners
##function to set hot corners
class Utils:
    @staticmethod
    def get_path(filename):
        current_dir = pathlib.Path(__file__).parent.absolute()
        return f"{current_dir}/{filename}"
    @staticmethod
    def notify(title, message): ##Thanks to plibither8 from nordvpn extension :)
        Notify.init("eOSHotCornersExt")
        notification = Notify.Notification.new(title, message, Utils.get_path("images/logo.png"),)
        notification.set_timeout(1000)
        notification.show()

    @staticmethod
    def create_item(name, icon, keyword, description, on_enter):
        return (
            keyword,
            ExtensionResultItem(
                name=name,
                description=description,
                icon=Utils.get_path("images/logo.png"),
                on_enter=RunScriptAction(on_enter, None),
                #            on_enter=RunScriptAction('xfce4-session-logout --{}'.format(on_enter), None),
            )
        )
    @staticmethod
    def get_conf_file_name():
        return str(os.environ['HOME'] + "/.config/ulauncher/hcSettings.json")

    @staticmethod
    def get_list_from_json(input):
        return json.loads(input)

    @staticmethod
    def save_to_json(jsondata, filename):
        #Save Settings to json file
        print("Saving to json: " + filename)
        with open(filename, "w") as json_file:
            json.dump(jsondata, json_file)
    
    @staticmethod
    def load_from_json(filename):
        #load settings from json
        print("Loading from json: " + filename)
        with open(filename) as json_file:
            data = json.load(json_file)
            json_file.close()
            return data
            

class HotCorners():
    
    def getHCSettings(self):
        currentHCSettings = []
        for hc in self.hclist:
            process = subprocess.Popen(['gsettings', 'get', 'org.pantheon.desktop.gala.behavior', hc], stdout=subprocess.PIPE)
            output = process.stdout.readline().decode('utf-8').strip()
            if output:
                currentHCSettings.append(output)
        return(currentHCSettings)

    def isOn(self):
        for c in self.currSettings:
            if str(c) != "'none'":
                return True
        return False


    def hcOn(self):
        #turn hcsettings on
        if len(self.currSettings) == len(self.hclist):
            Utils.notify("Pantheon HotCorners Extension", "Setting Hot Corners to on.", )
            for i in range(0, len(self.currSettings)):
                os.system('gsettings set org.pantheon.desktop.gala.behavior ' + self.hclist[i] + " " + self.currSettings[i])

    def hcOff(self):
        #turn hcsettings off
        currSettings = self.getHCSettings()
        if len(self.currSettings) == len(self.hclist) and self.isOn():
            Utils.notify("Pantheon Hot Corners Extension", "Setting Hot Corners to off.", )
            for i in range(0, len(self.currSettings)):
                os.system('gsettings set org.pantheon.desktop.gala.behavior  ' + self.hclist[i]+ " " + 'none')
            Utils.save_to_json(self.currSettings, Utils.get_conf_file_name())

    def __init__(self):
        #super(HotCorners, self).__init__()
        self.hclist = ["hotcorner-topleft", "hotcorner-custom-command", "hotcorner-topright", "hotcorner-bottomright", "hotcorner-bottomleft"]
        self.currSettings = self.getHCSettings()
        #Check, if enabled. If not, and json file exists, load json to memory.
        if self.isOn():
            print("ON")
        else:
            print("OFF")
            if os.path.exists(Utils.get_conf_file_name()):
                #load settings from last time disabling
                data = Utils.load_from_json(Utils.get_conf_file_name())
                self.currSettings = data
                print("eOSHotCorners: Loaded data from json on startup")
                for k in data:
                    print(k)
                


class HotCornersExtension(Extension):
    def __init__(self):
        super(HotCornersExtension, self).__init__()
        # register events
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(SystemExitEvent, SystemExitEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.hotcorners = HotCorners()



class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        items = []
        argument = event.get_argument() or ""
        command, arg = (argument.split(" ") + [None])[:2]
        items.extend(
            [
                ExtensionResultItem(
                    icon = Utils.get_path("images/logo.png"),
                    name = "Enable",
                    description = "Turn Hot Corners ON in elementary OS.",
                    on_enter=ExtensionCustomAction({"action": "HCON"}),
                ),
                ExtensionResultItem(
                    icon = Utils.get_path("images/logo.png"),
                    name = "Disable",
                    description = "Turn Hot Corners OFF in elementary OS.",
                    on_enter=ExtensionCustomAction({"action": "HCOFF"}),
                ),
            ]
        )

        return RenderResultListAction(items)

class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        action = data["action"]
       
        if action == "HCON":
            return extension.hotcorners.hcOn()

        if action == "HCOFF":
            return extension.hotcorners.hcOff()

class SystemExitEventListener(EventListener):
    def on_event(self, event, extension):
        print("Closing")
        #return extension.hotcorners.hcOn()


if __name__ == "__main__":
    HotCornersExtension().run()
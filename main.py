import json
import os
import os.path
import pathlib
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
        notification = Notify.Notification.new(title, message, Utils.get_path("images/logo.png"))

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

class HotCorners():
    
    def getHCSettings(self):
        currentHCSettings = []
        for hc in self.hclist:
            process = subprocess.Popen(['gsettings', 'get', 'org.pantheon.desktop.gala.behavior', hc], stdout=subprocess.PIPE)
            output = process.stdout.readline().decode('utf-8').strip()
            if output:
                currentHCSettings.append(output)
        return(currentHCSettings)

    def hcOn(self):
        #turn hcsettings on
        if len(self.currSettings) == len(self.hclist):
            for i in range(0, len(self.currSettings)):
                os.system('gsettings set org.pantheon.desktop.gala.behavior ' + self.hclist[i] + " " + self.currSettings[i])

    def hcOff(self):
        #turn hcsettings off
        currSettings = self.getHCSettings()
        if len(self.currSettings) == len(self.hclist):
            for i in range(0, len(self.currSettings)):
                os.system('gsettings set org.pantheon.desktop.gala.behavior  ' + self.hclist[i]+ " " + 'none')

    def __init__(self):
        #super(HotCorners, self).__init__()
        self.hclist = ["hotcorner-topleft", "hotcorner-custom-command", "hotcorner-topright", "hotcorner-bottomright", "hotcorner-bottomleft"]
        self.currSettings = self.getHCSettings()

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
        return extension.hotcorners.hcOn()


if __name__ == "__main__":
    HotCornersExtension().run()
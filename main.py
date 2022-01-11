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



#gsettings variables
topright = ""
topleft = ""
bottomright = ""
bottomleft = ""


##on init read hot corners
##maybe event for quit, to revert hot corners

##or write hot corners in file

##function to get current hot corners
##function to set hot corners
class Utils:
    hclist = ["hotcorner-topleft", "hotcorner-custom-command", "hotcorner-topright", "hotcorner-bottomright", "hotcorner-bottomleft"]
    @staticmethod
    def getHCSettings():
        process = subprocess.Popen(
            ['gsettings', 'get', 'org.pantheon.desktop.gala.behavior', 'hotcorner-topleft'], stdout=subprocess.PIPE)
            output = process.stdout.readline().decode('utf-8').strip()


        print("")

    @staticmethod
    def setHCSettings(isOn):
        print("")
    
    @staticmethod
    def notify(title, message): ##Thanks to plibither8 from nordvpn extension :)
        Notify.init("eOSHotCornersExt")
        notification = Notify.Notification.new(title, message, Utils.get_path("images/icon.svg"))

class HotCorners():
    def hcOn(self):
        #turn hcsettings on
        Utils.setHCSettings(True)

    def hcOff(self):
        #turn hcsettings off
        Utils.setHCSettings(False)


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
        items.extend(
            [
                ExtensionResultItem(
                    icon = Utils.get_path("images/icon.svg"),
                    name = "Enable",
                    description = "Turn Hot Corners ON in elementary OS.",
                    on_enter=ExtensionCustomAction({"action": "HCON"}),
                ),
                ExtensionResultItem(
                    icon = Utils.get_path("images/icon.svg"),
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
            return RenderResultListAction(extension.get_country_ext_result_items())

        if action == "HCOFF":
            return extension.hotcorners.hcOff()

class SystemExitEventListener(EventListener):
    def on_event(self, event, extension):
        print("shutting down")


if __name__ == "__main__":
    HotCorners().run()
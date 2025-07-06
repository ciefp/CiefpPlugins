from enigma import eTimer, getDesktop, gFont
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Sources.List import List
from Components.config import config, ConfigSubsection, ConfigSelection
from Components.MultiContent import MultiContentEntryPixmapAlphaTest, MultiContentEntryText
from Tools.LoadPixmap import LoadPixmap
import os
import subprocess
import logging


# Verzija plugina
PLUGIN_VERSION = "1.5"

# Setup logging to a file for better debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/ciefp_plugin.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Plugin configuration
config.plugins.CiefpPlugins = ConfigSubsection()
config.plugins.CiefpPlugins.language = ConfigSelection(default="en", choices=[("sr", "Serbian"), ("en", "English")])

# Plugin list with normalized file names
PLUGIN_LIST = [
    ("Ciefpsettings Motor", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpsettingsMotor.png", "wget https://raw.githubusercontent.com/ciefp/CiefpsettingsMotor/main/installer.sh -O - | /bin/sh", "CiefpsettingsMotor"),
    ("Ciefpsettings Panel", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpsettingsPanel.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpsettingsPanel/main/installer.sh -O - | /bin/sh", "CiefpsettingsPanel"),
    ("Ciefpsettings Downloader", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpsettingsDownloader.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSettingsDownloader/main/installer.sh -O - | /bin/sh", "CiefpsettingsDownloader"),
    ("Ciefp Enigma2 Converter", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpEnigma2Converter.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpE2Converter/main/installer.sh -O - | /bin/sh", "CiefpEnigma2Converter"),
    ("Ciefp Satellites.xml Editor", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpSatellitesXmlEditor.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSatelliteXmlEditor/main/installer.sh -O - | /bin/sh", "CiefpSatelliteXmlEditor"),
    ("Ciefp Select Satellite", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpSelectSatellite.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSelectSatellite/main/installer.sh -O - | /bin/sh", "CiefpSelectSatellite"),
    ("Ciefp Channel Manager", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpChannelManager.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpChannelManager/main/installer.sh -O - | /bin/sh", "CiefpChannelManager"),
    ("CiefpScreenGrab", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpScreenGrab.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpScreenGrab/main/installer.sh -O - | /bin/sh", "CiefpScreenGrab"),
    ("CiefpTvProgramSK", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpTvProgramSK.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpTvProgramSK/main/installer.sh -O - | /bin/sh", "CiefpTvProgramSK"),
    ("CiefpTvProgram", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpTvProgram.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpTvProgram/main/installer.sh -O - | /bin/sh", "CiefpTvProgram"),
    ("CiefpMojTvEPG", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpMojTvEPG.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpMojTvEPG/main/installer.sh -O - | /bin/sh", "CiefpMojTvEPG"),
    ("Ciefp IPTV Bouquets", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpIPTVBouquets.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpIPTVBouquets/main/installer.sh -O - | /bin/sh", "CiefpIPTVBouquets"),
    ("Ciefp Bouquet Updater", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpBouquetUpdater.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpBouquetUpdater/main/installer.sh -O - | /bin/sh", "CiefpBouquetUpdater"),
    ("Ciefp Whitelist Streamrelay", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpWhitelistStreamrelay.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpWhitelistStreamrelay/main/installer.sh -O - | /bin/sh", "CiefpWhitelistStreamrelay"),
    ("Ciefp Streamrelay py2", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpStreamrelayPy2.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSettingsStreamrelayPY2/main/installer.sh -O - | /bin/sh", "CiefpStreamrelayPy2"),
    ("Ciefp Streamrelay py3", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpStreamrelayPy3.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSettingsStreamrelay/main/installer.sh -O - | /bin/sh", "CiefpStreamrelayPy3"),
    ("Ciefp T2Mi Abertis", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpT2MiAbertis.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSettingsT2miAbertis/main/installer.sh -O - | /bin/sh", "CiefpT2MiAbertis"),
    ("Ciefp T2Mi Abertis OpenPli", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpT2MiAbertisOpenPli.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSettingsT2miAbertisOpenPLi/main/installer.sh -O - | /bin/sh", "CiefpT2MiAbertisOpenPli"),
    ("Ciefp Plugins", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpPlugins.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpPlugins/main/installer.sh -O - | /bin/sh", "CiefpPlugins"),
]

class CiefpPluginsPanel(Screen):
    skin = """
    <screen name="CiefpPluginsPanel" position="center,center" size="1600,850" title="..:: Ciefp Plugins ::..">
        <!-- Title -->
        <widget name="title" position="0,0" size="1600,100" font="Regular;60" halign="center" foregroundColor="#FFFFFF" backgroundColor="#000000" />
        <!-- Icons and Names (Left Side) -->
        <widget source="pluginlist" render="Listbox" position="50,100" size="400,680" scrollbarMode="showOnDemand" enableWrapAround="1">
            <convert type="TemplatedMultiContent">
                {"template": [
                    MultiContentEntryPixmapAlphaTest(pos=(10,10), size=(150,150), png=0, flags=1),
                    MultiContentEntryText(pos=(170,10), size=(220,150), font=0, text=1, flags=RT_VALIGN_CENTER|RT_WRAP),
                ],
                "fonts": [gFont("Regular", 24)],
                "itemHeight": 170}
            </convert>
        </widget>
        <!-- Description (Right Side) -->
        <widget name="description" position="470,100" size="1100,680" font="Regular;26" scrollbarMode="showOnDemand" />
        <!-- Colored Buttons -->
        <eLabel text="Exit" position="50,800" size="150,40" font="Regular;22" foregroundColor="#FF0000" halign="center" backgroundColor="#3F0000" />
        <eLabel text="Install" position="210,800" size="150,40" font="Regular;22" foregroundColor="#00FF00" halign="center" backgroundColor="#003F00" />
        <eLabel text="Serbian" position="370,800" size="150,40" font="Regular;22" foregroundColor="#FFFF00" halign="center" backgroundColor="#3F3F00" />
        <eLabel text="English" position="530,800" size="150,40" font="Regular;22" foregroundColor="#0000FF" halign="center" backgroundColor="#00003F" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.language = config.plugins.CiefpPlugins.language.value
        self.focusOnDescription = False  # Default focus is on plugin list

        # Plugin list with one item per row (icon + name)
        self.pluginList = []
        for name, icon, install_cmd, desc_file in PLUGIN_LIST:
            pixmap = None
            if os.path.exists(icon):
                pixmap = LoadPixmap(icon)
                if pixmap:
                    logger.debug(f"Successfully loaded icon: {icon}")
                else:
                    logger.warning(f"Failed to load pixmap for icon: {icon}")
            else:
                default_icon = "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/placeholder.png"
                if os.path.exists(default_icon):
                    pixmap = LoadPixmap(default_icon)
                    if pixmap:
                        logger.debug(f"Successfully loaded default icon: {default_icon}")
                    else:
                        logger.warning(f"Failed to load pixmap for default icon: {default_icon}")
                else:
                    logger.warning(f"Icon not found: {icon}, default icon also missing: {default_icon}")
            
            self.pluginList.append((pixmap, name, install_cmd, desc_file))

        # Components
        self["pluginlist"] = List(self.pluginList)
        self["description"] = ScrollLabel("")
        self["title"] = Label("..:: Ciefp Plugins ::..")  # Explicitly set title component
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"], {
            "cancel": self.exit,
            "red": self.exit,
            "green": self.installPlugin,
            "yellow": self.setLanguageSr,
            "blue": self.setLanguageEn,
            "ok": self.toggleFocus,
            "up": self.moveUp,
            "down": self.moveDown,
            "left": self.moveLeft,
            "right": self.moveRight,
        }, -2)

        self.onLayoutFinish.append(self.updateDescription)

    def moveUp(self):
        if self.focusOnDescription:
            self["description"].pageUp()  # Scroll up in description
            logger.debug("Scrolled up in description")
        else:
            self["pluginlist"].up()
            self.updateDescription()
            logger.debug("Moved up in plugin list")

    def moveDown(self):
        if self.focusOnDescription:
            self["description"].pageDown()  # Scroll down in description
            logger.debug("Scrolled down in description")
        else:
            self["pluginlist"].down()
            self.updateDescription()
            logger.debug("Moved down in plugin list")

    def moveLeft(self):
        if self.focusOnDescription:
            self["description"].pageUp()  # Scroll up in description (same as up)
            logger.debug("Scrolled up (left) in description")
        else:
            logger.debug("Left key ignored in plugin list")

    def moveRight(self):
        if self.focusOnDescription:
            self["description"].pageDown()  # Scroll down in description (same as down)
            logger.debug("Scrolled down (right) in description")
        else:
            logger.debug("Right key ignored in plugin list")

    def toggleFocus(self):
        self.focusOnDescription = not self.focusOnDescription
        if self.focusOnDescription:
            logger.debug("Focus switched to description for scrolling")
            self["description"].setText(self["description"].getText())  # Refresh to ensure focus
        else:
            logger.debug("Focus switched back to plugin list")
        self.updateDescription()

    def updateDescription(self):
        current = self["pluginlist"].getCurrent()
        if current:
            name, install_cmd, desc_file = current[1:4]
            desc_path = f"/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/descriptions/{self.language}/{desc_file}.txt"
            if os.path.exists(desc_path):
                with open(desc_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Remove emojis to avoid Unicode errors
                    content = ''.join(char for char in content if ord(char) < 0x10000)
                    self["description"].setText(f"Name: {name}\n\n{content}")
                    logger.debug(f"Loaded description: {desc_path}")
            else:
                self["description"].setText(f"Name: {name}\n\nDescription not available: File {desc_path} does not exist.")
                logger.warning(f"Description file not found: {desc_path}")
        else:
            self["description"].setText("No plugin available at this position.")
            logger.debug("No plugin available at this position.")

    def setLanguageSr(self):
        config.plugins.CiefpPlugins.language.value = "sr"
        config.plugins.CiefpPlugins.language.save()
        self.language = "sr"
        self.updateDescription()
        logger.debug("Language set to Serbian")

    def setLanguageEn(self):
        config.plugins.CiefpPlugins.language.value = "en"
        config.plugins.CiefpPlugins.language.save()
        self.language = "en"
        self.updateDescription()
        logger.debug("Language set to English")

    def installPlugin(self):
        if not self.focusOnDescription:
            current = self["pluginlist"].getCurrent()
            if current:
                install_cmd = current[2]
                if install_cmd:
                    self.session.openWithCallback(
                        self.installPluginCallback,
                        MessageBox,
                        "Do you want to install this plugin?",
                        MessageBox.TYPE_YESNO,
                        default=False
                    )
                    logger.debug(f"Prompting for install confirmation for command: {install_cmd}")
                else:
                    logger.debug("No install command for this plugin")
        else:
            logger.debug("Install ignored while focus is on description")

    def installPluginCallback(self, result):
        if result:  # True means "Yes"
            current = self["pluginlist"].getCurrent()
            if current:
                install_cmd = current[2]
                self["description"].setText("Installation in progress...\n")
                try:
                    subprocess.run(install_cmd, shell=True, check=True)
                    self["description"].setText(self["description"].getText() + "Installation successful!")
                    logger.debug(f"Installation successful for command: {install_cmd}")
                except subprocess.CalledProcessError as e:
                    self["description"].setText(self["description"].getText() + f"Error during installation: {str(e)}")
                    logger.error(f"Installation failed: {str(e)}")
        else:  # False means "No"
            self["description"].setText("Installation cancelled.")
            logger.debug("Installation cancelled by user")

    def exit(self):
        self.close()
        logger.debug("Exiting CiefpPluginsPanel")

def main(session, **kwargs):
    session.open(CiefpPluginsPanel)

def Plugins(**kwargs):
    from Plugins.Plugin import PluginDescriptor
    return [PluginDescriptor(name="Ciefp Plugins", description=f"Panel for Ciefp plugins (Version {PLUGIN_VERSION})", where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main, icon="plugin.png")]
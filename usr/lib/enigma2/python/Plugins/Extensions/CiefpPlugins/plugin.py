from enigma import eTimer, getDesktop, gFont, eConsoleAppContainer
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
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import os
import subprocess
import logging
import glob
import shutil

# Verzija plugina
PLUGIN_VERSION = "1.9"  # Vraćeno na stabilnu verziju

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

# URL za proveru verzije
VERSION_URL = "https://raw.githubusercontent.com/ciefp/CiefpPlugins/refs/heads/main/version.txt"

# Komanda za ažuriranje plugina
UPDATE_COMMAND = "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpPlugins/main/installer.sh -O - | /bin/sh"

# Fajl za čuvanje instaliranih plugina
INSTALLED_PLUGINS_FILE = "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/installed_plugins.txt"

# Privremena lokacija za backup fajla
BACKUP_PLUGINS_FILE = "/tmp/ciefp_plugins_backup.txt"

# Plugin configuration
config.plugins.CiefpPlugins = ConfigSubsection()
language_choices = [("en", "English")]  # Defaultni jezik
config.plugins.CiefpPlugins.language = ConfigSelection(default="en", choices=language_choices)

# Plugin list with normalized file names
PLUGIN_LIST = [
    ("Ciefpsettings Motor", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpsettingsMotor.png", "wget https://raw.githubusercontent.com/ciefp/CiefpsettingsMotor/main/installer.sh -O - | /bin/sh", "CiefpsettingsMotor"),
    ("Ciefpsettings Panel", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpsettingsPanel.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpsettingsPanel/main/installer.sh -O - | /bin/sh", "CiefpsettingsPanel"),
    ("Ciefpsettings Downloader", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpsettingsDownloader.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSettingsDownloader/main/installer.sh -O - | /bin/sh", "CiefpsettingsDownloader"),
    ("Ciefp Enigma2 Converter", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpEnigma2Converter.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpE2Converter/main/installer.sh -O - | /bin/sh", "CiefpEnigma2Converter"),
    ("Ciefp Satellites.xml Editor", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpSatellitesXmlEditor.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSatelliteXmlEditor/main/installer.sh -O - | /bin/sh", "CiefpSatellitesXmlEditor"),
    ("Ciefp Select Satellite", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpSelectSatellite.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSelectSatellite/main/installer.sh -O - | /bin/sh", "CiefpSelectSatellite"),
    ("Ciefp Channel Manager", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpChannelManager.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpChannelManager/main/installer.sh -O - | /bin/sh", "CiefpChannelManager"),
    ("CiefpScreenGrab", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpScreenGrab.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpScreenGrab/main/installer.sh -O - | /bin/sh", "CiefpScreenGrab"),
    ("CiefpEPGshare", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpEPGshare.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpEPGshare/main/installer.sh -O - | /bin/sh", "CiefpEPGshare"),
    ("CiefpTvProgramSBB", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpTvProgramSBB.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpTvProgramSBB/main/installer.sh -O - | /bin/sh", "CiefpTvProgramSBB"),
    ("CiefpTvProgramSK", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpTvProgramSK.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpTvProgramSK/main/installer.sh -O - | /bin/sh", "CiefpTvProgramSK"),
    ("CiefpTvProgramA1HR", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpTvProgramA1HR.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpTvProgramA1HR/main/installer.sh -O - | /bin/sh", "CiefpTvProgramA1HR"),
    ("CiefpTvTodayDE", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpTvTodayDE.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpTvTodayDE/main/installer.sh -O - | /bin/sh", "CiefpTvTodayDE"),
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

# Dinamički popuni listu jezika na osnovu foldera u descriptions
def getAvailableLanguages():
    desc_path = "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/descriptions/"
    if os.path.exists(desc_path):
        folders = [f for f in os.listdir(desc_path) if os.path.isdir(os.path.join(desc_path, f))]
        language_choices = [(f, f.capitalize()) for f in folders]
        if not language_choices:
            language_choices = [("en", "English")]
        return language_choices
    return [("en", "English")]

language_choices = getAvailableLanguages()
config.plugins.CiefpPlugins.language.choices = language_choices

class ImageViewerScreen(Screen):
    skin = """
    <screen name="ImageViewerScreen" position="center,center" size="1600,850" title="..:: Image Viewer ::..">
        <widget name="image" position="50,100" size="1500,680" zPosition="1" alphatest="on" scale="1" />
        <widget name="image_label" position="50,780" size="1500,40" font="Regular;24" halign="center" foregroundColor="#FFFFFF" />
        <eLabel text="Exit" position="50,800" size="150,40" font="Regular;22" foregroundColor="#FFFFFF" halign="center" backgroundColor="#3F0000" />
        <eLabel text="Previous" position="210,800" size="150,40" font="Regular;22" foregroundColor="#FFFFFF" halign="center" backgroundColor="#003F00" />
        <eLabel text="Next" position="370,800" size="150,40" font="Regular;22" foregroundColor="#FFFFFF" halign="center" backgroundColor="#00003F" />
    </screen>"""

    def __init__(self, session, images, plugin_name):
        Screen.__init__(self, session)
        self.session = session
        self.images = images
        self.current_index = 0
        self.plugin_name = plugin_name

        self["image"] = Pixmap()
        self["image_label"] = Label()
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"], {
            "cancel": self.exit,
            "red": self.exit,
            "green": self.prevImage,
            "blue": self.nextImage,
            "left": self.prevImage,
            "right": self.nextImage,
        }, -2)

        self.onLayoutFinish.append(self.showImage)

    def showImage(self):
        if self.images:
            image_path = self.images[self.current_index]
            pixmap = LoadPixmap(image_path)
            if pixmap:
                self["image"].instance.setPixmap(pixmap)
                self["image_label"].setText(f"Image {self.current_index + 1}/{len(self.images)}: {os.path.basename(image_path)}")
                logger.debug(f"Showing image: {image_path}")
            else:
                self["image_label"].setText(f"Error loading image: {os.path.basename(image_path)}")
                logger.error(f"Failed to load image: {image_path}")
        else:
            self["image_label"].setText(f"No images available for {self.plugin_name}")
            logger.debug(f"No images available for {self.plugin_name}")

    def nextImage(self):
        if self.images:
            self.current_index = (self.current_index + 1) % len(self.images)
            self.showImage()
            logger.debug(f"Moved to next image: {self.current_index}")

    def prevImage(self):
        if self.images:
            self.current_index = (self.current_index - 1) % len(self.images)
            self.showImage()
            logger.debug(f"Moved to previous image: {self.current_index}")

    def exit(self):
        self.close()
        logger.debug("Exiting ImageViewerScreen")

class CiefpPluginsPanel(Screen):
    skin = """
    <screen name="CiefpPluginsPanel" position="center,center" size="1600,850" title="..:: Ciefp Plugins ::.. (Version {version})">
        <!-- Title -->
        <widget name="title" position="0,0" size="1600,100" font="Regular;60" halign="center" foregroundColor="#FFFFFF" backgroundColor="#000000" />
        <!-- Icons and Names (Left Side) -->
        <widget source="pluginlist" render="Listbox" position="50,100" size="400,680" scrollbarMode="showOnDemand" enableWrapAround="1">
            <convert type="TemplatedMultiContent">
                {{"template": [
                    MultiContentEntryPixmapAlphaTest(pos=(10,10), size=(150,150), png=0, flags=1),
                    MultiContentEntryText(pos=(170,10), size=(220,150), font=0, text=1, flags=RT_VALIGN_CENTER|RT_WRAP),
                ],
                "fonts": [gFont("Regular", 24)],
                "itemHeight": 170}}
            </convert>
        </widget>
        <!-- Description (Right Side) -->
        <widget name="description" position="470,100" size="1100,680" font="Regular;26" scrollbarMode="showOnDemand" />
        <!-- Colored Buttons -->
        <eLabel text="Exit" position="50,800" size="150,40" font="Regular;22" foregroundColor="#FFFFFF" halign="center" backgroundColor="#3F0000" />
        <eLabel text="Install" position="210,800" size="150,40" font="Regular;22" foregroundColor="#FFFFFF" halign="center" backgroundColor="#003F00" />
        <eLabel text="Language" position="370,800" size="150,40" font="Regular;22" foregroundColor="#FFFFFF" halign="center" backgroundColor="#3F3F00" />
        <eLabel text="Image Viewer" position="530,800" size="150,40" font="Regular;22" foregroundColor="#FFFFFF" halign="center" backgroundColor="#00003F" />
        <!-- Status Label -->
        <widget name="status_label" position="690,800" size="900,40" font="Regular;22" foregroundColor="#FFFFFF" halign="left" transparent="1" />
    </screen>""".format(version=PLUGIN_VERSION)

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.language = config.plugins.CiefpPlugins.language.value
        self.focusOnDescription = False  # Default focus is on plugin list
        self.available_languages = [choice[0] for choice in getAvailableLanguages()]
        self.version_check_in_progress = False
        self.version_buffer = b''

        # Plugin list with one item per row (icon + name)
        self.pluginList = []
        for name, icon, install_cmd, desc_file in PLUGIN_LIST:
            pixmap = None
            icon_path = resolveFilename(SCOPE_PLUGINS, icon.replace("/usr/lib/enigma2/python/Plugins/", ""))
            default_icon = resolveFilename(SCOPE_PLUGINS, "Extensions/CiefpPlugins/icons/placeholder.png")
            if os.path.exists(icon_path):
                pixmap = LoadPixmap(icon_path)
                if pixmap:
                    logger.debug(f"Successfully loaded icon: {icon_path}")
                else:
                    logger.warning(f"Failed to load pixmap for icon: {icon_path}")
            elif os.path.exists(default_icon):
                pixmap = LoadPixmap(default_icon)
                if pixmap:
                    logger.debug(f"Successfully loaded default icon: {default_icon}")
                else:
                    logger.warning(f"Failed to load pixmap for default icon: {default_icon}")
            else:
                logger.warning(f"Icon not found: {icon_path}, default icon also missing: {default_icon}")
            
            self.pluginList.append((pixmap, name, install_cmd, desc_file))

        # Components
        self["pluginlist"] = List(self.pluginList)
        self["description"] = ScrollLabel("")
        self["status_label"] = Label("")
        self["title"] = Label(f"..:: Ciefp Plugins ::.. (Version {PLUGIN_VERSION})")
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"], {
            "cancel": self.exit,
            "red": self.exit,
            "green": self.installPlugin,
            "yellow": self.changeLanguage,
            "blue": self.openImageViewer,
            "ok": self.toggleFocus,
            "up": self.moveUp,
            "down": self.moveDown,
            "left": self.moveLeft,
            "right": self.moveRight,
        }, -2)

        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.command_finished)
        self.container.dataAvail.append(self.version_data_avail)

        self.onLayoutFinish.append(self.updateDescription)

        # Automatska provera verzije pri pokretanju
        self.check_version_timer = eTimer()
        self.check_version_timer.callback.append(self.check_for_updates)
        self.check_version_timer.start(1000, True)

    def moveUp(self):
        if self.focusOnDescription:
            self["description"].pageUp()
            logger.debug("Scrolled up in description")
        else:
            self["pluginlist"].up()
            self.updateDescription()
            logger.debug("Moved up in plugin list")

    def moveDown(self):
        if self.focusOnDescription:
            self["description"].pageDown()
            logger.debug("Scrolled down in description")
        else:
            self["pluginlist"].down()
            self.updateDescription()
            logger.debug("Moved down in plugin list")

    def moveLeft(self):
        if self.focusOnDescription:
            self["description"].pageUp()
            logger.debug("Scrolled up (left) in description")
        else:
            logger.debug("Left key ignored in plugin list")

    def moveRight(self):
        if self.focusOnDescription:
            self["description"].pageDown()
            logger.debug("Scrolled down (right) in description")
        else:
            logger.debug("Right key ignored in plugin list")

    def toggleFocus(self):
        self.focusOnDescription = not self.focusOnDescription
        if self.focusOnDescription:
            logger.debug("Focus switched to description for scrolling")
            self["description"].setText(self["description"].getText())
        else:
            logger.debug("Focus switched back to plugin list")
        self.updateDescription()

    def updateDescription(self):
        current = self["pluginlist"].getCurrent()
        if current:
            name, install_cmd, desc_file = current[1:4]
            desc_path = f"/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/descriptions/{self.language}/{desc_file}.txt"
            content = ""
            if os.path.exists(desc_path):
                with open(desc_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    content = ''.join(char for char in content if ord(char) < 0x10000)
                    logger.debug(f"Loaded description: {desc_path}")
            else:
                content = "Description not available."
                logger.warning(f"Description file not found: {desc_path}")
            self["description"].setText(f"Name: {name}\n\n{content}")
            logger.debug(f"Updated description for plugin: {name}")
        else:
            self["description"].setText("No plugin available at this position.")
            logger.debug("No plugin available at this position.")

    def changeLanguage(self):
        if self.available_languages:
            current_idx = self.available_languages.index(self.language) if self.language in self.available_languages else 0
            next_idx = (current_idx + 1) % len(self.available_languages)
            self.language = self.available_languages[next_idx]
            config.plugins.CiefpPlugins.language.value = self.language
            config.plugins.CiefpPlugins.language.save()
            self.updateDescription()
            logger.debug(f"Language changed to: {self.language}")

    def openImageViewer(self):
        current = self["pluginlist"].getCurrent()
        if current:
            name, install_cmd, desc_file = current[1:4]
            image_prefix = desc_file.lower().replace(" ", "_")
            pictures_path = "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/pictures/"
            images = glob.glob(f"{pictures_path}{image_prefix}_*.jpg") + glob.glob(f"{pictures_path}{image_prefix}_*.png")
            images.sort()
            if images:
                self.session.open(ImageViewerScreen, images, name)
                logger.debug(f"Opening ImageViewerScreen with {len(images)} images for {name}")
            else:
                self["description"].setText(f"No images found for {name} in {pictures_path}")
                logger.warning(f"No images found for {name} in {pictures_path}")
        else:
            self["description"].setText("No plugin selected.")
            logger.debug("No plugin selected for image viewer")

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
        if result:
            current = self["pluginlist"].getCurrent()
            if current:
                install_cmd = current[2]
                self["status_label"].setText("Installation in progress...")
                try:
                    subprocess.run(install_cmd, shell=True, check=True)
                    self["status_label"].setText("Installation successful!")
                    logger.debug(f"Installation successful for command: {install_cmd}")
                    self.log_installed_plugin(current[1])  # Loguj instalirani plugin
                    self.updateDescription()  # Osveži opis nakon instalacije
                except subprocess.CalledProcessError as e:
                    self["status_label"].setText(f"Error during installation: {str(e)}")
                    logger.error(f"Installation failed: {str(e)}")
        else:
            self["status_label"].setText("Installation cancelled.")
            logger.debug("Installation cancelled by user")

    def log_installed_plugin(self, plugin_name):
        try:
            plugin_dir = os.path.dirname(INSTALLED_PLUGINS_FILE)
            if not os.path.exists(plugin_dir):
                os.makedirs(plugin_dir)
                logger.debug(f"Created directory: {plugin_dir}")

            existing_plugins = set()
            if os.path.exists(INSTALLED_PLUGINS_FILE):
                with open(INSTALLED_PLUGINS_FILE, "r") as f:
                    existing_plugins = {line.strip() for line in f if line.strip()}

            if plugin_name not in existing_plugins:
                with open(INSTALLED_PLUGINS_FILE, "a") as f:
                    f.write(f"{plugin_name}\n")
                logger.debug(f"Logged plugin {plugin_name} to {INSTALLED_PLUGINS_FILE}")
        except Exception as e:
            logger.error(f"Error logging plugin {plugin_name}: {str(e)}")
            self["status_label"].setText(f"Error logging plugin {plugin_name}: {str(e)}")

    def check_for_updates(self):
        try:
            if self.version_check_in_progress:
                return
            self.version_check_in_progress = True
            self["status_label"].setText("Checking for updates...")
            self.version_buffer = b''
            self.container.execute(f"wget -q -O - {VERSION_URL}")
        except Exception as e:
            self.version_check_in_progress = False
            self["status_label"].setText(f"Update error: {str(e)}")
            logger.error(f"Error checking for updates: {str(e)}")

    def version_data_avail(self, data):
        self.version_buffer += data

    def command_finished(self, retval):
        if self.version_check_in_progress:
            self.version_check_closed(retval)
        else:
            self.update_completed(retval)

    def version_check_closed(self, retval):
        self.version_check_in_progress = False
        if retval == 0:
            try:
                remote_version = self.version_buffer.decode().strip()
                if remote_version != PLUGIN_VERSION:
                    self.session.openWithCallback(
                        self.start_update,
                        MessageBox,
                        f"Update available ({remote_version}). Install now?",
                        MessageBox.TYPE_YESNO
                    )
                else:
                    self["status_label"].setText("Plugin is up to date.")
            except Exception as e:
                self["status_label"].setText(f"Update check failed: {str(e)}")
                logger.error(f"Error decoding version data: {str(e)}")
        else:
            self["status_label"].setText("Update check failed.")
            logger.error(f"Version check failed with return value: {retval}")

    def start_update(self, answer):
        if answer:
            try:
                self["status_label"].setText("Backing up installed plugins list...")
                if os.path.exists(INSTALLED_PLUGINS_FILE):
                    shutil.copy2(INSTALLED_PLUGINS_FILE, BACKUP_PLUGINS_FILE)
                    logger.debug(f"Backed up {INSTALLED_PLUGINS_FILE} to {BACKUP_PLUGINS_FILE}")
                else:
                    logger.debug(f"No {INSTALLED_PLUGINS_FILE} found for backup")

                self["status_label"].setText("Updating plugin...")
                self.container.execute(UPDATE_COMMAND)
            except Exception as e:
                self["status_label"].setText(f"Backup error: {str(e)}")
                logger.error(f"Error during backup: {str(e)}")

    def update_completed(self, retval):
        try:
            if os.path.exists(BACKUP_PLUGINS_FILE):
                plugin_dir = os.path.dirname(INSTALLED_PLUGINS_FILE)
                if not os.path.exists(plugin_dir):
                    os.makedirs(plugin_dir)
                    logger.debug(f"Created directory: {plugin_dir}")

                shutil.move(BACKUP_PLUGINS_FILE, INSTALLED_PLUGINS_FILE)
                logger.debug(f"Restored {BACKUP_PLUGINS_FILE} to {INSTALLED_PLUGINS_FILE}")
            else:
                logger.debug(f"No backup file {BACKUP_PLUGINS_FILE} found for restoration")

            if retval == 0:
                self["status_label"].setText("Update successful. Restarting...")
                self.container.execute("init 4 && init 3")
            else:
                self["status_label"].setText("Update failed.")
                logger.error(f"Update failed with return value: {retval}")
        except Exception as e:
            self["status_label"].setText(f"Restore error: {str(e)}")
            logger.error(f"Error during restore: {str(e)}")

    def exit(self):
        self.close()
        logger.debug("Exiting CiefpPluginsPanel")

def main(session, **kwargs):
    session.open(CiefpPluginsPanel)

def Plugins(**kwargs):
    from Plugins.Plugin import PluginDescriptor
    return [PluginDescriptor(name="Ciefp Plugins", description=f"Panel for Ciefp plugins (Version {PLUGIN_VERSION})", where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main, icon="plugin.png")]
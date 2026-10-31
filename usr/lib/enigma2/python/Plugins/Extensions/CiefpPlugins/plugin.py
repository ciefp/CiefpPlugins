from enigma import eTimer, getDesktop, gFont, eConsoleAppContainer, ePoint
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
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
import urllib.request
import requests  # <--- DODAJ OVO
import uuid
import json
from Components.config import ConfigText
# Plugin version
PLUGIN_VERSION = "4.7"

# Setup logging
LOG_FILE = "/tmp/ciefp_plugin.log"
FALLBACK_LOG_FILE = "/tmp/ciefp_plugin_fallback.log"

def setup_logging():
    logger = logging.getLogger("CiefpPlugins")
    logger.propagate = False
    if logger.handlers:
        logger.handlers.clear()

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    try:
        handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except Exception as e:
        try:
            fallback = logging.FileHandler(FALLBACK_LOG_FILE, mode='a', encoding='utf-8')
            fallback.setFormatter(formatter)
            logger.addHandler(fallback)
            logger.error(f"Primary log failed, using fallback: {str(e)}")
        except:
            pass

    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    logger.addHandler(stream)

    logger.info("Logging initialized for CiefpPlugins")
    return logger

logger = setup_logging()

# URLs and paths
VERSION_URL = "https://raw.githubusercontent.com/ciefp/CiefpPlugins/refs/heads/main/version.txt"
UPDATE_COMMAND = "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpPlugins/main/installer.sh -O - | /bin/sh"
INSTALLED_PLUGINS_FILE = "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/installed_plugins.txt"
BACKUP_PLUGINS_FILE = "/tmp/ciefp_plugins_backup.txt"
PICTURES_DIR = "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/pictures/"
LANGUAGE_FILE = "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/selected_language.txt"
PICTURES_FILE_PATHS = [
    "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/pictures.txt",
    "/tmp/pictures.txt",
    "/usr/share/enigma2/pictures.txt"
]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
TRANSLATION_CACHE_DIR = "/tmp/CiefpPlugins/translations/"

LANGUAGE_NAMES = [
    ("English", "en"), ("Serbian", "sr"), ("German", "de"),
    ("French", "fr"), ("Italian", "it"), ("Spanish", "es"),
    ("Croatian", "hr"), ("Slovenian", "sl"), ("Hungarian", "hu"),
    ("Polish", "pl"), ("Czech", "cs"), ("Slovak", "sk"),
    ("Romanian", "ro"), ("Bulgarian", "bg"), ("Greek", "el"),
    ("Turkish", "tr"), ("Russian", "ru"), ("Dutch", "nl"),
    ("Portuguese", "pt"), ("Swedish", "sv"),
]

# Plugin configuration
config.plugins.CiefpPlugins = ConfigSubsection()
language_choices = [("en", "English - en")]
config.plugins.CiefpPlugins.language = ConfigSelection(default="en", choices=language_choices)
config.plugins.CiefpPlugins.groq_api_key = ConfigText(default="", fixed_size=False)
config.plugins.CiefpPlugins.api_key_location = ConfigSelection(
    default="/etc/enigma2/CiefpPlugins/",
    choices=[
        ("/etc/enigma2/CiefpPlugins/", "/etc/enigma2/CiefpPlugins/"),
        ("/tmp/CiefpPlugins/", "/tmp/CiefpPlugins/"),
        ("/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/", "Plugin dir"),
    ]
)

# Plugin list
PLUGIN_LIST = [
    ("Ciefpsettings Motor", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpsettingsMotor.png", "wget https://raw.githubusercontent.com/ciefp/CiefpsettingsMotor/main/installer.sh -O - | /bin/sh", "CiefpsettingsMotor", "CiefpsettingsMotor"),
    ("Ciefpsettings Panel", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpsettingsPanel.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpsettingsPanel/main/installer.sh -O - | /bin/sh", "CiefpsettingsPanel", "CiefpsettingsPanel"),
    ("Ciefpsettings Downloader", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpsettingsDownloader.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSettingsDownloader/main/installer.sh -O - | /bin/sh", "CiefpsettingsDownloader", "CiefpSettingsDownloader"),
    ("Ciefp Enigma2 Converter", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpEnigma2Converter.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpE2Converter/main/installer.sh -O - | /bin/sh", "CiefpEnigma2Converter", "CiefpE2Converter"),
    ("Ciefp Satellites.xml Editor", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpSatellitesXmlEditor.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSatelliteXmlEditor/main/installer.sh -O - | /bin/sh", "CiefpSatellitesXmlEditor", "CiefpSatelliteXmlEditor"),
    ("Ciefp Select Satellite", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpSelectSatellite.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSelectSatellite/main/installer.sh -O - | /bin/sh", "CiefpSelectSatellite", "CiefpSelectSatellite"),
    ("Ciefp Channel Manager", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpChannelManager.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpChannelManager/main/installer.sh -O - | /bin/sh", "CiefpChannelManager", "CiefpChannelManager"),
    ("CiefpScreenGrab", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpScreenGrab.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpScreenGrab/main/installer.sh -O - | /bin/sh", "CiefpScreenGrab", "CiefpScreenGrab"),
    ("CiefpEPGshare", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpEPGshare.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpEPGshare/main/installer.sh -O - | /bin/sh", "CiefpEPGshare", "CiefpEPGshare"),
    ("CiefpTvProgramSBB", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpTvProgramSBB.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpTvProgramSBB/main/installer.sh -O - | /bin/sh", "CiefpTvProgramSBB", "CiefpTvProgramSBB"),
    ("CiefpTvProgramSK", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpTvProgramSK.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpTvProgramSK/main/installer.sh -O - | /bin/sh", "CiefpTvProgramSK", "CiefpTvProgramSK"),
    ("CiefpTvProgramA1HR", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpTvProgramA1HR.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpTvProgramA1HR/main/installer.sh -O - | /bin/sh", "CiefpTvProgramA1HR", "CiefpTvProgramA1HR"),
    ("CiefpTvTodayDE", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpTvTodayDE.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpTvTodayDE/main/installer.sh -O - | /bin/sh", "CiefpTvTodayDE", "CiefpTvTodayDE"),
    ("CiefpTvProgram", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpTvProgram.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpTvProgram/main/installer.sh -O - | /bin/sh", "CiefpTvProgram", "CiefpTvProgram"),
    ("CiefpMojTvEPG", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpMojTvEPG.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpMojTvEPG/main/installer.sh -O - | /bin/sh", "CiefpMojTvEPG", "CiefpMojTvEPG"),
    ("Ciefp IPTV Bouquets", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpIPTVBouquets.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpIPTVBouquets/main/installer.sh -O - | /bin/sh", "CiefpIPTVBouquets", "CiefpIPTVBouquets"),
    ("Ciefp Bouquet Updater", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpBouquetUpdater.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpBouquetUpdater/main/installer.sh -O - | /bin/sh", "CiefpBouquetUpdater", "CiefpBouquetUpdater"),
    ("CiefpOscamEditor", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpOscamEditor.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpOscamEditor/main/installer.sh -O - | /bin/sh", "CiefpOscamEditor", "CiefpOscamEditor"),
    ("CiefpSatelliteAnalyzer", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpSatelliteAnalyzer.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSatelliteAnalyzer/main/installer.sh -O - | /bin/sh", "CiefpSatelliteAnalyzer", "CiefpSatelliteAnalyzer"),
    ("CiefpOpenDirectories", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpOpenDirectories.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpOpenDirectories/main/installer.sh -O - | /bin/sh", "CiefpOpenDirectories", "CiefpOpenDirectories"),
    ("CiefpRottenTomatoes", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpRottenTomatoes.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpRottenTomatoes/main/installer.sh -O - | /bin/sh", "CiefpRottenTomatoes", "CiefpRottenTomatoes"),
    ("CiefpTMDBSearch", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpTMDBSearch.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpTMDBSearch/main/installer.sh -O - | /bin/sh", "CiefpTMDBSearch", "CiefpTMDBSearch"),
    ("CiefpVibes", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpVibes.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpVibes/main/installer.sh -O - | /bin/sh", "CiefpVibes", "CiefpVibes"),
    ("CiefpOpenSubtitles", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpOpenSubtitles.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpOpenSubtitles/main/installer.sh -O - | /bin/sh", "CiefpOpenSubtitles", "CiefpOpenSubtitles"),
    ("Titlovi Browser", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/TitloviBrowser.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/TitloviBrowser/main/installer.sh -O - | /bin/sh", "TitloviBrowser", "TitloviBrowser"),
    ("CiefpKingSat", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpKingSat.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpKingSat/main/installer.sh -O - | /bin/sh", "CiefpKingSat", "CiefpKingSat"),
    ("CiefpParabolaCZ", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpParabolaCZ.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpParabolaCZ/main/installer.sh -O - | /bin/sh", "CiefpParabolaCZ", "CiefpParabolaCZ"),
    ("CiefpSRTplayer", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpSRTplayer.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSRTplayer/main/installer.sh -O - | /bin/sh", "CiefpSRTplayer", "CiefpSRTplayer"),
    ("CiefpEasySetup", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpEasySetup.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpEasySetup/main/installer.sh -O - | /bin/sh", "CiefpEasySetup", "CiefpEasySetup"),
    ("CiefpPicturePlayer", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpPicturePlayer.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpPicturePlayer/main/installer.sh -O - | /bin/sh", "CiefpPicturePlayer", "CiefpPicturePlayer"),
    ("CiefpVideoPlayer", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpVideoPlayer.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpVideoPlayer/main/installer.sh -O - | /bin/sh", "CiefpVideoPlayer", "CiefpVideoPlayer"),
    ("CiefpYouTube", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpYouTube.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpYouTube/main/installer.sh -O - | /bin/sh", "CiefpYouTube", "CiefpYouTube"),
    ("CiefpE2editor", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpE2editor.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpE2editor/main/installer.sh -O - | /bin/sh", "CiefpE2editor", "CiefpE2editor"),
    ("CiefpBootlogo", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpBootlogo.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpBootlogo/main/installer.sh -O - | /bin/sh", "CiefpBootlogo", "CiefpBootlogo"),
    ("CiefpPiconManager", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpPiconManager.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpPiconManager/main/installer.sh -O - | /bin/sh", "CiefpPiconManager", "CiefpPiconManager"),
    ("CiefpSignalInfo", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpSignalInfo.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSignalInfo/main/installer.sh -O - | /bin/sh", "CiefpSignalInfo", "CiefpSignalInfo"),
    ("CiefpEPGinfo", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpEPGinfo.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpEPGinfo/main/installer.sh -O - | /bin/sh", "CiefpEPGinfo", "CiefpEPGinfo"),
    ("CiefpDishPointer", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpDishPointer.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpDishPointer/main/installer.sh -O - | /bin/sh", "CiefpDishPointer", "CiefpDishPointer"),
    ("CiefpXfiles", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpXfiles.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpXfiles/main/installer.sh -O - | /bin/sh", "CiefpXfiles", "CiefpXfiles"),
    ("CiefpChannelHistory", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpChannelHistory.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpChannelHistory/main/installer.sh -O - | /bin/sh", "CiefpChannelHistory", "CiefpChannelHistory"),
    ("Ciefp Whitelist Streamrelay", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpWhitelistStreamrelay.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpWhitelistStreamrelay/main/installer.sh -O - | /bin/sh", "CiefpWhitelistStreamrelay", "CiefpWhitelistStreamrelay"),
    ("Ciefp T2Mi Abertis", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpT2MiAbertis.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSettingsT2miAbertis/main/installer.sh -O - | /bin/sh", "CiefpT2MiAbertis", "CiefpSettingsT2miAbertis"),
    ("Ciefp T2Mi Abertis OpenPli", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpT2MiAbertisOpenPli.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSettingsT2miAbertisOpenPLi/main/installer.sh -O - | /bin/sh", "CiefpT2MiAbertisOpenPli", "CiefpSettingsT2miAbertisOpenPLi"),
    ("Ciefp Streamrelay py2", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpStreamrelayPy2.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSettingsStreamrelayPY2/main/installer.sh -O - | /bin/sh", "CiefpStreamrelayPy2", "CiefpSettingsStreamrelayPY2"),
    ("Ciefp Streamrelay py3", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpStreamrelayPy3.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpSettingsStreamrelay/main/installer.sh -O - | /bin/sh", "CiefpStreamrelayPy3", "CiefpSettingsStreamrelay"),
    ("WebCamE2PrenjSF", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/WebCamE2PrenjSF.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/WebCamE2PrenjSF/main/installer.sh -O - | /bin/sh", "WebCamE2PrenjSF", "WebCamE2PrenjSF"),
    ("Ciefp Plugins", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/icons/CiefpPlugins.png", "wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpPlugins/main/installer.sh -O - | /bin/sh", "CiefpPlugins", "CiefpPlugins"),
]

def load_pictures_map():
    pictures_map = {}
    for path in PICTURES_FILE_PATHS:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    current_plugin = None
                    for line in f.read().splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        if line.endswith(":"):
                            current_plugin = line[:-1].strip().lower()
                            pictures_map[current_plugin] = []
                        elif current_plugin and line.startswith("https://"):
                            pictures_map[current_plugin].append(line)
                    logger.info(f"Loaded images for {len(pictures_map)} plugins from pictures.txt")
                    return pictures_map
            except Exception as e:
                logger.error(f"Error reading pictures.txt at {path}: {str(e)}")
    logger.warning("pictures.txt not found in any expected location.")
    return pictures_map

PICTURES_MAP = load_pictures_map()

# Load selected language from file
def load_selected_language(available_languages):
    logger.info(f"Attempting to load language from {LANGUAGE_FILE}")
    if os.path.exists(LANGUAGE_FILE):
        try:
            with open(LANGUAGE_FILE, "r", encoding="utf-8") as f:
                line = f.readline().strip()
                if line:
                    lang_code = line.split("-")[-1].strip()
                    if lang_code in available_languages:
                        logger.debug(f"Loaded language from file: {lang_code}")
                        return lang_code
                    else:
                        logger.warning(f"Invalid language code in {LANGUAGE_FILE}: {lang_code}")
        except Exception as e:
            logger.error(f"Error reading {LANGUAGE_FILE}: {str(e)}")
    else:
        logger.debug(f"No language file found at {LANGUAGE_FILE}")
    return None

# Get available languages
def getAvailableLanguages():
    # Vraća listu tuple-ova: (kod, "Naziv - kod")
    return [(code, f"{name} - {code}") for name, code in LANGUAGE_NAMES]

language_choices = getAvailableLanguages()
config.plugins.CiefpPlugins.language.choices = language_choices

def is_plugin_installed(plugin_name):
    """Provera da li je plugin instaliran."""
    if not plugin_name:
        return False

    # 1. Provera direktnog foldera (Extensions)
    plugin_path = f"/usr/lib/enigma2/python/Plugins/Extensions/{plugin_name}"
    if os.path.exists(plugin_path):
        return True

    # 2. Provera Systems foldera (neki plugini se tu instaliraju)
    system_path = f"/usr/lib/enigma2/python/Plugins/SystemPlugins/{plugin_name}"
    if os.path.exists(system_path):
        return True

    # 3. Provera za settings plugine (koji nemaju svoj folder)
    settings_plugins = [
        "CiefpsettingsMotor", "CiefpsettingsPanel",
        "CiefpStreamrelayPy2", "CiefpStreamrelayPy3",
        "CiefpT2MiAbertis", "CiefpT2MiAbertisOpenPli"
    ]
    if plugin_name in settings_plugins:
        return os.path.exists("/etc/enigma2/satellites.xml")

    return False


def load_api_key():
    """Učitava Groq API ključ iz fajla ili config-a."""
    key_file = os.path.join(
        config.plugins.CiefpPlugins.api_key_location.value,
        "groqapikey.txt"
    )
    if os.path.exists(key_file):
        try:
            with open(key_file, "r", encoding="utf-8") as f:
                key = f.read().strip()
                if key:
                    logger.info(f"Loaded API key from {key_file}")
                    return key
        except Exception as e:
            logger.error(f"Error reading API key file: {e}")
    return config.plugins.CiefpPlugins.groq_api_key.value or ""


def translate_text(text, target_language, api_key):
    """Prevod teksta preko Groq API (koristi requests, identično kao CiefpEPGinfo)."""
    if not api_key:
        logger.error("No API key for translation")
        return None
    if not text or not text.strip():
        return text

    # Koristimo model koji sigurno radi (isti kao u CiefpEPGinfo)
    model = "openai/gpt-oss-120b"

    try:
        # Priprema instrukcija za LLM
        system_prompt = (
            f"You are a professional translator. "
            f"Translate the following text into {target_language}. "
            f"Keep formatting and line breaks. "
            f"Return ONLY the translation, no explanations."
        )

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            "temperature": 0.3,
            "max_tokens": 4000,
        }

        headers = {
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        }

        # KORISTIMO REQUESTS umesto urllib (rešava 403 Forbidden)
        r = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        if r.status_code == 200:
            data = r.json()
            translated = data["choices"][0]["message"]["content"].strip()
            logger.info(f"Translation successful to {target_language}")
            return translated
        else:
            logger.error(f"Translation HTTP error {r.status_code}: {r.text[:300]}")
            return None

    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return None

def get_cached_translation(plugin_name, language):
    cache_file = os.path.join(TRANSLATION_CACHE_DIR, f"{plugin_name}_{language}.txt")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return f.read()
        except:
            pass
    return None


def save_translation_cache(plugin_name, language, text):
    try:
        os.makedirs(TRANSLATION_CACHE_DIR, exist_ok=True)
        cache_file = os.path.join(TRANSLATION_CACHE_DIR, f"{plugin_name}_{language}.txt")
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        logger.error(f"Error saving translation cache: {e}")


class ImageViewerScreen(Screen):
    skin = """
    <screen name="ImageViewerScreen" position="center,center" size="1920,1080"  backgroundColor="#000000">
        <widget name="image" position="60,80" size="1800,860" zPosition="1" alphatest="on" scale="1" />
        <widget name="image_label" position="60,960" size="1800,50" font="Regular;28" halign="center" foregroundColor="#FFFFFF" backgroundColor="#000000" />
        <eLabel text="Exit" position="60,1020" size="180,50" font="Regular;24" foregroundColor="#FFFFFF" halign="center" backgroundColor="#3F0000" />
        <eLabel text="Previous" position="260,1020" size="180,50" font="Regular;24" foregroundColor="#FFFFFF" halign="center" backgroundColor="#003F00" />
        <eLabel text="Next" position="460,1020" size="180,50" font="Regular;24" foregroundColor="#FFFFFF" halign="center" backgroundColor="#00003F" />
        <eLabel text="Info: Use Arrows or Colored Buttons to navigate" position="660,1020" size="1200,50" font="Regular;24" foregroundColor="#888888" halign="left" />
    </screen>"""

    def __init__(self, session, image_urls, plugin_name):
        Screen.__init__(self, session)
        self.session = session
        self.image_urls = image_urls
        self.current_index = 0
        self.plugin_name = plugin_name
        self.temp_files = []

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
        
    def download_image(self, url):
        temp_file = f"/tmp/ciefp_image_{uuid.uuid4().hex}.jpg"
        try:
            urllib.request.urlretrieve(url, temp_file)
            if os.path.exists(temp_file):
                self.temp_files.append(temp_file)
                logger.debug(f"Downloaded image to {temp_file}")
                return temp_file
        except Exception as e:
            logger.error(f"Error downloading image {url}: {str(e)}")
            return None

    def showImage(self):
        if not self.image_urls:
            self["image_label"].setText(f"No images available for {self.plugin_name}")
            return

        image_url = self.image_urls[self.current_index]
        temp_file = self.download_image(image_url)
        if temp_file and os.path.exists(temp_file):
            pixmap = LoadPixmap(temp_file)
            if pixmap:
                self["image"].instance.setPixmap(pixmap)
                self["image_label"].setText(f"Image {self.current_index + 1}/{len(self.image_urls)} - {self.plugin_name}")
            else:
                self["image_label"].setText("Failed to load image.")
                logger.error(f"LoadPixmap failed for: {temp_file}")
        else:
            self["image_label"].setText("Failed to download image.")
            logger.error(f"Download failed for: {image_url}")

    def nextImage(self):
        if self.image_urls:
            self.current_index = (self.current_index + 1) % len(self.image_urls)
            self.showImage()
            logger.debug(f"Moved to next image: {self.current_index}")

    def prevImage(self):
        if self.image_urls:
            self.current_index = (self.current_index - 1) % len(self.image_urls)
            self.showImage()
            logger.debug(f"Moved to previous image: {self.current_index}")

    def exit(self):
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.debug(f"Removed temporary file: {temp_file}")
            except Exception as e:
                logger.error(f"Error removing temporary file {temp_file}: {str(e)}")
        self.close()
        logger.debug("Exiting ImageViewerScreen")

class CiefpPluginsSettings(Screen):
    skin = """
    <screen name="CiefpPluginsSettings" position="center,center" size="1920,1080" backgroundColor="#011a2e">
        <widget name="separator0" position="0,0" size="1920,3" backgroundColor="#d5fa02" zPosition="1" />
        <widget name="title" position="0,5" size="1920,80" font="Regular;48" halign="center" foregroundColor="#FFFFFF" backgroundColor="#012e01" />
        <widget name="separator1" position="0,90" size="1920,3" backgroundColor="#d5fa02" zPosition="1" />
        <widget source="menu_list" render="Listbox" position="60,120" size="700,800" backgroundColor="#011a2e" scrollbarMode="showOnDemand" enableWrapAround="1">
            <convert type="TemplatedMultiContent">
                {"template": [
                    MultiContentEntryText(pos=(10,10), size=(680,40), font=0, text=0, flags=RT_HALIGN_LEFT|RT_VALIGN_CENTER),
                    MultiContentEntryText(pos=(10,50), size=(680,40), font=1, text=1, flags=RT_HALIGN_LEFT|RT_VALIGN_CENTER),
                ],
                "fonts": [gFont("Regular", 28), gFont("Regular", 22)],
                "itemHeight": 100}
            </convert>
        </widget>
        <widget name="settings_image" position="800,180" size="1000,700" alphatest="on" />
        <widget name="status_label" position="60,950" size="1300,40" font="Regular;24" foregroundColor="#FFFF00" halign="left" transparent="1" />
        <widget name="separator3" position="0,990" size="1920,3" backgroundColor="#d5fa02" zPosition="1" />
        <eLabel text="Exit" position="60,1000" size="350,40" font="Regular;24" foregroundColor="#FFFFFF" halign="center" backgroundColor="#3F0000" />
        <eLabel text="Save" position="430,1000" size="350,40" font="Regular;24" foregroundColor="#FFFFFF" halign="center" backgroundColor="#003F00" />
        <eLabel text="API Key" position="800,1000" size="350,40" font="Regular;24" foregroundColor="#FFFFFF" halign="center" backgroundColor="#3F3F00" />
        <eLabel text="Location" position="1170,1000" size="350,40" font="Regular;24" foregroundColor="#FFFFFF" halign="center" backgroundColor="#00003F" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self["separator0"] = Label()
        self["separator1"] = Label()
        self["separator3"] = Label()
        self["title"] = Label("..:: Ciefp Plugins Settings ::..")
        self["settings_image"] = Pixmap()
        self["menu_list"] = List([])
        self["menu_list"].onSelectionChanged.append(self.on_selection_changed)
        self["status_label"] = Label("")
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"], {
            "cancel": self.exit,
            "red": self.exit,
            "green": self.save_settings,
            "yellow": self.enter_api_key,
            "blue": self.change_location,
            "ok": self.select_item,
            "up": self.move_up,
            "down": self.move_down,
        }, -2)
        self.menu_items = []
        self.build_menu()
        self.onLayoutFinish.append(self.load_settings_image)

    def build_menu(self):
        # Dodajemo prazan string na treću poziciju da zadovoljimo parser ako je potrebno
        self.menu_items = [
            ("Language for translation", self.language_label()),
            ("API Key status", self.api_key_status()),
            ("API Key location", config.plugins.CiefpPlugins.api_key_location.value),
            ("Translation cache", "Clear cache"),
        ]
        self["menu_list"].setList(self.menu_items)
        # Forsiramo osvežavanje
        if self["menu_list"].getCurrent():
            self["menu_list"].setIndex(self["menu_list"].getSelectedIndex())

    def language_label(self):
        # Čitaj direktno iz fajla da bi uvek prikazao tačan jezik
        try:
            if os.path.exists(LANGUAGE_FILE):
                with open(LANGUAGE_FILE, "r", encoding="utf-8") as f:
                    current = f.readline().strip()
                    if current:
                        return f"Language: {current}"
        except Exception:
            pass
        # Fallback na config ako fajl ne postoji
        return f"Language: {config.plugins.CiefpPlugins.language.value}"

    def api_key_status(self):
        key = load_api_key()
        if key:
            return f"API Key: {'*' * 8}{key[-4:] if len(key) > 4 else '****'}"
        return "API Key: NOT SET"

    def load_settings_image(self):
        img_path = resolveFilename(SCOPE_PLUGINS, "Extensions/CiefpPlugins/pictures/settings.png")
        if os.path.exists(img_path):
            pixmap = LoadPixmap(img_path)
            if pixmap:
                self["settings_image"].instance.setPixmap(pixmap)

    def move_up(self):
        self["menu_list"].up()

    def move_down(self):
        self["menu_list"].down()

    def select_item(self):
        idx = self["menu_list"].getSelectedIndex()
        if idx == 0:
            self.change_language()
        elif idx == 3:
            self.clear_cache()

    def change_language(self):
        choices = [(f"{name} - {code}", code) for name, code in LANGUAGE_NAMES]
        self.session.openWithCallback(self.language_selected, ChoiceBox, title="Select translation language", list=choices)

    def language_selected(self, choice):
        if choice:
            code = choice[1]

            # 1. Upiši direktno u naš fajl (primarni izvor)
            try:
                with open(LANGUAGE_FILE, "w", encoding="utf-8") as f:
                    f.write(f"{code}\n")
                logger.info(f"Language written to file: {code}")
            except Exception as e:
                logger.error(f"Error writing language file: {e}")

            # 2. Ažuriraj config (samo vrednost, bez save())
            config.plugins.CiefpPlugins.language.value = code

            # 3. Osveži meni
            self.build_menu()
            self["status_label"].setText(f"Language set to: {code}")
            logger.info(f"Language changed and saved: {code}")

    def save_settings(self):
        # Sačuvaj samo API lokaciju i ključ (jezik je već sačuvan u language_selected)
        config.plugins.CiefpPlugins.api_key_location.save()
        config.plugins.CiefpPlugins.groq_api_key.save()

        # Pročitaj trenutni jezik iz fajla da potvrdimo
        current_lang = "en"
        try:
            if os.path.exists(LANGUAGE_FILE):
                with open(LANGUAGE_FILE, "r", encoding="utf-8") as f:
                    current_lang = f.readline().strip() or "en"
        except:
            pass

        self["status_label"].setText(f"Settings saved (Language: {current_lang})")
        logger.info(f"Settings saved. Language in file: {current_lang}")

    def enter_api_key(self):
        try:
            from Screens.VirtualKeyBoard import VirtualKeyBoard
        except:
            from Components.Sources.VirtualKeyBoard import VirtualKeyBoard
        current_key = load_api_key()
        self.session.openWithCallback(self.api_key_entered, VirtualKeyBoard, title="Enter Groq API Key", text=current_key)

    def api_key_entered(self, key):
        if key:
            config.plugins.CiefpPlugins.groq_api_key.value = key
            config.plugins.CiefpPlugins.groq_api_key.save()
            try:
                location = config.plugins.CiefpPlugins.api_key_location.value
                os.makedirs(location, exist_ok=True)
                with open(os.path.join(location, "groqapikey.txt"), "w") as f:
                    f.write(key)
                logger.info("API key saved")
                self["status_label"].setText("API key saved")
            except Exception as e:
                logger.error(f"Error saving API key to file: {e}")
                self["status_label"].setText(f"Error: {e}")
            self.build_menu()

    def change_location(self):
        locations = [
            ("/etc/enigma2/CiefpPlugins/", "/etc/enigma2/CiefpPlugins/"),
            ("/tmp/CiefpPlugins/", "/tmp/CiefpPlugins/"),
            ("Plugin directory", "/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/"),
        ]
        self.session.openWithCallback(self.location_selected, ChoiceBox, title="Select API Key location", list=locations)

    def location_selected(self, choice):
        if choice:
            config.plugins.CiefpPlugins.api_key_location.value = choice[1]
            config.plugins.CiefpPlugins.api_key_location.save()
            self.build_menu()

    def clear_cache(self):
        try:
            if os.path.exists(TRANSLATION_CACHE_DIR):
                shutil.rmtree(TRANSLATION_CACHE_DIR)
            self["status_label"].setText("Cache cleared")
            logger.info("Translation cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            self["status_label"].setText(f"Error: {e}")

    def on_selection_changed(self):
        # Ovo je opciono - možeš dodati logiku ako želiš
        pass

    def exit(self):
        self.close()

class CiefpPluginPreview(Screen):
    skin = """
    <screen name="CiefpPluginPreview" position="center,center" size="1920,1080" backgroundColor="#011a2e">
        <widget name="separator0" position="0,0" size="1920,3" backgroundColor="#d5fa02" zPosition="1" />  
        <widget name="title" position="0,5" size="1920,80" font="Regular;48" halign="center" foregroundColor="#FFFFFF" backgroundColor="#012e01" />
        <widget name="separator1" position="0,90" size="1920,3" backgroundColor="#d5fa02" zPosition="1" />  

        <!-- Prošireni prostor za tekst -->
        <widget name="description" position="60,120" size="1800,850" font="Regular;28" scrollbarMode="showOnDemand" backgroundColor="#00070d" foregroundColor="#FFFFFF" />

        <widget name="status_label" position="60,970" size="1800,30" font="Regular;24" foregroundColor="#FFFF00" halign="left" transparent="1" />

        <widget name="separator3" position="0,1000" size="1920,3" backgroundColor="#d5fa02" zPosition="1" />
        <eLabel text="Exit" position="60,1010" size="350,40" font="Regular;24" foregroundColor="#FFFFFF" halign="center" backgroundColor="#3F0000" />
    </screen>"""

    def __init__(self, session, plugin_name, desc_file, pixmap):
        Screen.__init__(self, session)
        self.session = session
        self.plugin_name = plugin_name
        self.desc_file = desc_file

        self["separator0"] = Label()
        self["separator1"] = Label()
        self["separator3"] = Label()
        self["title"] = Label(f"..:: {plugin_name} ::..")
        self["description"] = ScrollLabel("")
        self["status_label"] = Label("")

        self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"], {
            "cancel": self.exit,
            "red": self.exit,
            "up": self["description"].pageUp,
            "down": self["description"].pageDown,
            "left": self["description"].pageUp,
            "right": self["description"].pageDown,
        }, -2)

        self.onLayoutFinish.append(self.load_text)

    def load_text(self):
        # 1. Učitaj jezik
        lang = load_selected_language([choice[0] for choice in getAvailableLanguages()]) or "en"

        # 2. Provera keša
        cached = get_cached_translation(self.desc_file, lang)
        if cached:
            self["description"].setText(cached)
            self["status_label"].setText(f"Loaded from cache ({lang})")
            return

        # 3. Učitavanje engleskog originala
        desc_path = f"/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/descriptions/en/{self.desc_file}.txt"
        content = ""
        if os.path.exists(desc_path):
            with open(desc_path, "r", encoding="utf-8") as f:
                content = f.read()
                content = ''.join(char for char in content if ord(char) < 0x10000)
        else:
            content = "Description not available."

        if lang == "en":
            self["description"].setText(content)
            self["status_label"].setText("Showing English original.")
            return

        # 4. Prevod
        api_key = load_api_key()
        if api_key:
            self["status_label"].setText("Translating, please wait...")
            translated = translate_text(content, lang, api_key)
            if translated:
                save_translation_cache(self.desc_file, lang, translated)
                self["description"].setText(translated)
                self["status_label"].setText(f"Translated to {lang} successfully.")
            else:
                self["description"].setText(content)
                self["status_label"].setText("Translation failed - showing English.")
        else:
            self["description"].setText(content)
            self["status_label"].setText("No API key set - showing English.")

    def exit(self):
        self.close()

class CiefpPluginsPanel(Screen):
    skin = """
    <screen name="CiefpPluginsPanel" position="center,center" size="1920,1080" backgroundColor="#011a2e">
        <widget name="separator0" position="0,0" size="1920,3" backgroundColor="#d5fa02" zPosition="1" />  
        <widget name="title" position="0,5" size="1920,80" font="Regular;48" halign="center" foregroundColor="#FFFFFF" backgroundColor="#012e01" />
        <widget name="separator1" position="0,90" size="1920,3" backgroundColor="#d5fa02" zPosition="1" />  

        <!-- GRID (7x5) - Veličina ikonice 150x150 -->
        <!-- Red 0 -->
        <widget name="pix_0" position="30,120" size="150,150" alphatest="blend" />
        <widget name="pix_1" position="190,120" size="150,150" alphatest="blend" />
        <widget name="pix_2" position="350,120" size="150,150" alphatest="blend" />
        <widget name="pix_3" position="510,120" size="150,150" alphatest="blend" />
        <widget name="pix_4" position="670,120" size="150,150" alphatest="blend" />
        <widget name="pix_5" position="830,120" size="150,150" alphatest="blend" />
        <widget name="pix_6" position="990,120" size="150,150" alphatest="blend" />
        <widget name="pix_7" position="1150,120" size="150,150" alphatest="blend" />

        <!-- Red 1 -->
        <widget name="pix_8" position="30,280" size="150,150" alphatest="blend" />
        <widget name="pix_9" position="190,280" size="150,150" alphatest="blend" />
        <widget name="pix_10" position="350,280" size="150,150" alphatest="blend" />
        <widget name="pix_11" position="510,280" size="150,150" alphatest="blend" />
        <widget name="pix_12" position="670,280" size="150,150" alphatest="blend" />
        <widget name="pix_13" position="830,280" size="150,150" alphatest="blend" />
        <widget name="pix_14" position="990,280" size="150,150" alphatest="blend" />
        <widget name="pix_15" position="1150,280" size="150,150" alphatest="blend" />

        <!-- Red 2 -->
        <widget name="pix_16" position="30,440" size="150,150" alphatest="blend" />
        <widget name="pix_17" position="190,440" size="150,150" alphatest="blend" />
        <widget name="pix_18" position="350,440" size="150,150" alphatest="blend" />
        <widget name="pix_19" position="510,440" size="150,150" alphatest="blend" />
        <widget name="pix_20" position="670,440" size="150,150" alphatest="blend" />
        <widget name="pix_21" position="830,440" size="150,150" alphatest="blend" />
        <widget name="pix_22" position="990,440" size="150,150" alphatest="blend" />
        <widget name="pix_23" position="1150,440" size="150,150" alphatest="blend" />

        <!-- Red 3 -->
        <widget name="pix_24" position="30,600" size="150,150" alphatest="blend" />
        <widget name="pix_25" position="190,600" size="150,150" alphatest="blend" />
        <widget name="pix_26" position="350,600" size="150,150" alphatest="blend" />
        <widget name="pix_27" position="510,600" size="150,150" alphatest="blend" />
        <widget name="pix_28" position="670,600" size="150,150" alphatest="blend" />
        <widget name="pix_29" position="830,600" size="150,150" alphatest="blend" />
        <widget name="pix_30" position="990,600" size="150,150" alphatest="blend" />
        <widget name="pix_31" position="1150,600" size="150,150" alphatest="blend" />

        <!-- Red 4 -->
        <widget name="pix_32" position="30,760" size="150,150" alphatest="blend" />
        <widget name="pix_33" position="190,760" size="150,150" alphatest="blend" />
        <widget name="pix_34" position="350,760" size="150,150" alphatest="blend" />
        <widget name="pix_35" position="510,760" size="150,150" alphatest="blend" />
        <widget name="pix_36" position="670,760" size="150,150" alphatest="blend" />
        <widget name="pix_37" position="830,760" size="150,150" alphatest="blend" />
        <widget name="pix_38" position="990,760" size="150,150" alphatest="blend" />
        <widget name="pix_39" position="1150,760" size="150,150" alphatest="blend" />

        <!-- DESNA STRANA -->
        <widget name="time_label" position="1550,120" size="320,50" font="Regular;46" halign="center" valign="center" foregroundColor="#FFFFFF" transparent="1" />
        <widget name="date_label" position="1550,180" size="320,50" font="Regular;46" halign="center" valign="center" foregroundColor="#FFFFFF" transparent="1" />

        <widget name="selected_icon" position="1500,250" size="150,150" alphatest="blend" />
        <widget name="selected_status" position="1700,250" size="150,150" alphatest="blend" />
        <widget name="selected_name" position="1500,450" size="750,60" font="Regular;36" halign="left" valign="center" foregroundColor="#FFFFFF" backgroundColor="#011a2e" />

        <widget name="selection_frame" position="50,700" size="156,156" zPosition="10" alphatest="on"/>
        <widget name="logo" position="1500,550" size="400,200" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/logo.png" alphatest="blend" />

        <widget name="separator4" position="1450,93" size="3,897" backgroundColor="#d5fa02" zPosition="1" />        
        <widget name="page_label" position="30,950" size="960,40" font="Regular;26" halign="left" valign="center" foregroundColor="#FFFFFF" backgroundColor="#011a2e" />
        <widget name="status_label" position="1100,1000" size="750,40" font="Regular;26" foregroundColor="#00FF00" halign="right" transparent="1" />

        <widget name="separator3" position="0,990" size="1920,3" backgroundColor="#d5fa02" zPosition="1" />
        <eLabel text="Exit" position="40,1000" size="350,40" font="Regular;24" foregroundColor="#FFFFFF" halign="center" backgroundColor="#3F0000" />
        <eLabel text="Install" position="410,1000" size="350,40" font="Regular;24" foregroundColor="#FFFFFF" halign="center" backgroundColor="#003F00" />
        <eLabel text="Settings" position="780,1000" size="350,40" font="Regular;24" foregroundColor="#FFFFFF" halign="center" backgroundColor="#3F3F00" />
        <eLabel text="Image Viewer" position="1150,1000" size="350,40" font="Regular;24" foregroundColor="#FFFFFF" halign="center" backgroundColor="#00003F" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.available_languages = [choice[0] for choice in getAvailableLanguages()]

        self.language = load_selected_language(self.available_languages) or "en"
        logger.info(f"Initialized with language (from file): {self.language}")

        self.version_check_in_progress = False
        self.version_buffer = b''

        # Pripremi listu pluginova
        self.pluginList = []
        for name, icon, install_cmd, desc_file, folder_name in PLUGIN_LIST:
            pixmap = None
            icon_path = resolveFilename(SCOPE_PLUGINS, icon.replace("/usr/lib/enigma2/python/Plugins/", ""))
            default_icon = resolveFilename(SCOPE_PLUGINS, "Extensions/CiefpPlugins/icons/placeholder.png")
            if os.path.exists(icon_path):
                pixmap = LoadPixmap(icon_path)
            elif os.path.exists(default_icon):
                pixmap = LoadPixmap(default_icon)

            installed = is_plugin_installed(folder_name)
            status_icon_name = "installed.png" if installed else "not_installed.png"
            status_icon_path = resolveFilename(SCOPE_PLUGINS, f"Extensions/CiefpPlugins/icons/{status_icon_name}")
            status_pixmap = LoadPixmap(status_icon_path) if os.path.exists(status_icon_path) else None

            self.pluginList.append((pixmap, name, install_cmd, desc_file, installed, status_pixmap, folder_name))

        # Grid postavke (8x5)
        self.grid_columns = 8
        self.grid_rows = 5
        self.grid_page_size = self.grid_columns * self.grid_rows
        self.grid_index = 0


        # Inicijalizacija grid widgeta
        self.grid_pixmaps = []
        for i in range(self.grid_page_size):
            pix_key = f"pix_{i}"
            self[pix_key] = Pixmap()
            self.grid_pixmaps.append(self[pix_key])

        # Desna strana
        self["selected_icon"] = Pixmap()
        self["selected_name"] = Label("")
        self["selected_status"] = Pixmap()

        # Frame (umesto u skin-u, ovde ga inicijalizujemo)
        self["selection_frame"] = Pixmap()

        # Labels
        self["time_label"] = Label("")
        self["date_label"] = Label("")
        self["page_label"] = Label()
        self["status_label"] = Label("")
        self["logo"] = Pixmap()
        self["title"] = Label(f"..:: Ciefp Plugins (NO.47) ::.. (Version {PLUGIN_VERSION})")
        self["separator0"] = Label()
        self["separator1"] = Label()
        self["separator3"] = Label()
        self["separator4"] = Label()


        # Akcije
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"], {
            "cancel": self.exit,
            "red": self.exit,
            "green": self.installPlugin,
            "yellow": self.open_settings,
            "blue": self.openImageViewer,
            "ok": self.open_preview,
            "up": self.moveUp,
            "down": self.moveDown,
            "left": self.moveLeft,
            "right": self.moveRight,
        }, -2)

        self.onLayoutFinish.append(self.load_frame)
        self.onLayoutFinish.append(self.render_grid)

        # Timer za vreme
        self.time_timer = eTimer()
        self.time_timer.callback.append(self.updateTime)
        self.time_timer.start(1000)
        self.onClose.append(self.time_timer.stop)

        # Provera verzije
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.command_finished)
        self.container.dataAvail.append(self.version_data_avail)

        self.check_version_timer = eTimer()
        self.check_version_timer.callback.append(self.check_for_updates)
        self.check_version_timer.start(1000, True)

    # ---------------- VREME ----------------
    def updateTime(self):
        import time
        try:
            self["time_label"].setText(time.strftime("%H:%M"))
            self["date_label"].setText(time.strftime("%d.%m.%Y"))
        except:
            pass

    def load_frame(self):
        """Učitava frame.png i postavlja ga na selection_frame widget."""
        frame_path = resolveFilename(SCOPE_PLUGINS, "Extensions/CiefpPlugins/frame.png")
        if os.path.exists(frame_path):
            frame_pixmap = LoadPixmap(frame_path)
            if frame_pixmap and self["selection_frame"].instance:
                self["selection_frame"].instance.setPixmap(frame_pixmap)
                self["selection_frame"].show()
                logger.info(f"Loaded frame: {frame_path}")
            else:
                logger.warning(f"Failed to load frame pixmap: {frame_path}")
        else:
            logger.warning(f"frame.png not found at: {frame_path}")

    def render_grid(self):
        if not self.pluginList:
            return

        page = self.grid_index // self.grid_page_size
        start = page * self.grid_page_size
        end = min(start + self.grid_page_size, len(self.pluginList))
        visible = self.pluginList[start:end]

        for slot in range(self.grid_page_size):
            if slot < len(visible):
                pixmap = visible[slot][0]
                if pixmap and self.grid_pixmaps[slot].instance:
                    self.grid_pixmaps[slot].instance.setPixmap(pixmap)
            else:
                if self.grid_pixmaps[slot].instance:
                    self.grid_pixmaps[slot].instance.setPixmap(None)

        # Ažuriraj selektor (frame)
        self.update_selector()

        total_pages = (len(self.pluginList) + self.grid_page_size - 1) // self.grid_page_size
        current_page = page + 1
        self["page_label"].setText(f"Page {current_page} / {total_pages}")

        self.update_selected_info()

    def update_selector(self):
        """Pomera frame.png na trenutno selektovanu ikonicu."""
        slot = self.grid_index % self.grid_page_size
        row = slot // self.grid_columns
        col = slot % self.grid_columns

        # Koordinate na osnovu skin-a (x=30 + col*160, y=120 + row*160)
        x = 30 + (col * 160)
        y = 120 + (row * 160)

        if self["selection_frame"].instance:
            from enigma import ePoint
            self["selection_frame"].instance.move(ePoint(x, y))

    def update_selected_info(self):
        """Ažurira desnu stranu ekrana (ikonica, ime, status)."""
        if not self.pluginList or self.grid_index >= len(self.pluginList):
            return

        pixmap, name, install_cmd, desc_file, installed, status_pixmap, folder_name = self.pluginList[self.grid_index]

        # Ikonica
        if pixmap and self["selected_icon"].instance:
            self["selected_icon"].instance.setPixmap(pixmap)

        # Ime
        self["selected_name"].setText(name)

        # Status ikonica
        if status_pixmap and self["selected_status"].instance:
            self["selected_status"].instance.setPixmap(status_pixmap)

    def moveUp(self):
        new_index = self.grid_index - self.grid_columns
        if new_index >= 0:
            self.grid_index = new_index
            self.render_grid()

    def moveDown(self):
        new_index = self.grid_index + self.grid_columns
        if new_index < len(self.pluginList):
            self.grid_index = new_index
            self.render_grid()

    def moveLeft(self):
        if self.grid_index > 0:
            self.grid_index -= 1
            self.render_grid()

    def moveRight(self):
        if self.grid_index < len(self.pluginList) - 1:
            self.grid_index += 1
            self.render_grid()

    def open_preview(self):
        if not self.pluginList or self.grid_index >= len(self.pluginList):
            return
        pixmap, name, install_cmd, desc_file, installed, status_pixmap, folder_name = self.pluginList[self.grid_index]
        self.session.open(CiefpPluginPreview, name, desc_file, pixmap)

    def open_settings(self):
        self.session.openWithCallback(self.settings_closed, CiefpPluginsSettings)
        logger.debug("Opened settings screen")

    def settings_closed(self, *args):
        self.available_languages = [choice[0] for choice in getAvailableLanguages()]
        new_lang = load_selected_language(self.available_languages)
        if new_lang:
            self.language = new_lang
        else:
            self.language = "en"
        logger.info(f"Language reloaded from file after settings: {self.language}")

    def installPlugin(self):
        if not self.pluginList or self.grid_index >= len(self.pluginList):
            return

        install_cmd = self.pluginList[self.grid_index][2]
        if install_cmd:
            self.session.openWithCallback(
                self.installPluginCallback,
                MessageBox,
                "Do you want to install this plugin?",
                MessageBox.TYPE_YESNO,
                default=False
            )

    def installPluginCallback(self, result):
        if result:
            install_cmd = self.pluginList[self.grid_index][2]
            name = self.pluginList[self.grid_index][1]
            folder_name = self.pluginList[self.grid_index][6]  # folder_name je na indeksu 6

            self["status_label"].setText("Installation in progress...")
            try:
                subprocess.run(install_cmd, shell=True, check=True)
                self["status_label"].setText("Installation successful!")
                self.log_installed_plugin(name)

                installed = is_plugin_installed(folder_name)
                status_icon_name = "installed.png" if installed else "not_installed.png"
                status_icon_path = resolveFilename(SCOPE_PLUGINS, f"Extensions/CiefpPlugins/icons/{status_icon_name}")
                status_pixmap = LoadPixmap(status_icon_path) if os.path.exists(status_icon_path) else None

                idx = self.grid_index
                old = self.pluginList[idx]
                new_item = (old[0], old[1], old[2], old[3], installed, status_pixmap, old[6])
                self.pluginList[idx] = new_item

                self.render_grid()
            except subprocess.CalledProcessError as e:
                self["status_label"].setText(f"Error during installation: {str(e)}")
        else:
            self["status_label"].setText("Installation cancelled.")

    def openImageViewer(self):
        if not self.pluginList or self.grid_index >= len(self.pluginList):
            return

        name = self.pluginList[self.grid_index][1]
        desc_file = self.pluginList[self.grid_index][3]

        image_urls = PICTURES_MAP.get(desc_file.lower(), [])
        if image_urls:
            self.session.open(ImageViewerScreen, image_urls, name)
        else:
            self["status_label"].setText(f"No images found for {name}")

    def log_installed_plugin(self, plugin_name):
        try:
            plugin_dir = os.path.dirname(INSTALLED_PLUGINS_FILE)
            if not os.path.exists(plugin_dir):
                os.makedirs(plugin_dir)

            existing_plugins = set()
            if os.path.exists(INSTALLED_PLUGINS_FILE):
                with open(INSTALLED_PLUGINS_FILE, "r") as f:
                    existing_plugins = {line.strip() for line in f if line.strip()}

            if plugin_name not in existing_plugins:
                with open(INSTALLED_PLUGINS_FILE, "a") as f:
                    f.write(f"{plugin_name}\n")
        except Exception as e:
            logger.error(f"Error logging plugin {plugin_name}: {str(e)}")

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
        else:
            self["status_label"].setText("Update check failed.")

    def start_update(self, answer):
        if answer:
            try:
                self["status_label"].setText("Backing up installed plugins list...")
                if os.path.exists(INSTALLED_PLUGINS_FILE):
                    shutil.copy2(INSTALLED_PLUGINS_FILE, BACKUP_PLUGINS_FILE)

                self["status_label"].setText("Updating plugin...")
                self.container.execute(UPDATE_COMMAND)
            except Exception as e:
                self["status_label"].setText(f"Backup error: {str(e)}")

    def update_completed(self, retval):
        try:
            if os.path.exists(BACKUP_PLUGINS_FILE):
                plugin_dir = os.path.dirname(INSTALLED_PLUGINS_FILE)
                if not os.path.exists(plugin_dir):
                    os.makedirs(plugin_dir)

                shutil.move(BACKUP_PLUGINS_FILE, INSTALLED_PLUGINS_FILE)

            if retval == 0:
                self["status_label"].setText("Update successful. Restarting...")
                self.container.execute("init 4 && init 3")
            else:
                self["status_label"].setText("Update failed.")
        except Exception as e:
            self["status_label"].setText(f"Restore error: {str(e)}")

    def exit(self):
        self.close()

def main(session, **kwargs):
    session.open(CiefpPluginsPanel)

def Plugins(**kwargs):
    from Plugins.Plugin import PluginDescriptor
    return [PluginDescriptor(name="Ciefp Plugins", description=f"Panel for Ciefp plugins NO.47 (Version {PLUGIN_VERSION})", where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main, icon="plugin.png")]
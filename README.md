
# Ciefp Plugins Panel

![Ciefp Plugins Panel](https://github.com/ciefp/CiefpPlugins/blob/main/preview.jpg)

**Version:** `2.5`  
**Author:** [@ciefp](https://github.com/ciefp)  
**License:** Free for personal use  
**Supported Languages:** English, Srpski, Slovenčina, Русский, Deutsch, Ελληνικά

---

## 📖 Description

**Ciefp Plugins Panel** is a powerful and user-friendly Enigma2 plugin that serves as a central hub for installing and managing a collection of popular **Ciefp** utilities and tools. Designed for satellite receiver users (OpenPLi, OpenATV, VTI, etc.), this panel simplifies the installation of advanced features like EPG importers, IPTV bouquet managers, satellite editors, and more — all with a single click.

---

## ✨ Features

- **One-click installation** of 25+ Ciefp plugins
- **Multilingual interface** (6 languages)
- **Plugin descriptions** with localized text
- **Image viewer** for plugin screenshots
- **Auto-update system** with version checking
- **Installed plugins tracking**
- **Clean, modern GUI** with icons and scrollable descriptions
- **Safe backup & restore** of installed plugins list during updates

---

## 🛠️ Supported Plugins (Examples)

| Plugin Name | Function |
|------------|---------|
| Ciefpsettings Motor | Motorized dish configuration |
| Ciefp IPTV Bouquets | IPTV channel list management |
| Ciefp EPGshare | EPG sharing between devices |
| Ciefp OscamEditor | OSCam configuration editor |
| Ciefp Satellite Analyzer | Signal analysis & transponder scanning |
| Ciefp TvProgramSBB | TV guide for SBB (Serbia) |

> Full list available in the plugin interface.

---

## 🌍 Supported Languages

The plugin automatically detects and loads descriptions in the selected language. Available languages:

| Code | Language |
|------|----------|
| `en` | English |
| `sr` | Srpski |
| `sk` | Slovenčina |
| `ru` | Русский |
| `de` | Deutsch |
| `el` | Ελληνικά |

> Language files are located in:  
> `/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/descriptions/<lang>/`

---

## 📥 Installation

The plugin is installed via its own **installer script** from GitHub:

```bash
wget -q --no-check-certificate https://raw.githubusercontent.com/ciefp/CiefpPlugins/main/installer.sh -O - | /bin/sh
```

> After installation, restart Enigma2 GUI (`init 4 && init 3`) or reboot the receiver.

---

## 🖼️ Screenshots

Screenshots are loaded dynamically from `pictures.txt`. Example format:

```
CiefpIPTVBouquets:
https://example.com/images/iptv1.jpg
https://example.com/images/iptv2.jpg

CiefpOscamEditor:
https://example.com/images/oscam1.jpg
```

> Place `pictures.txt` in one of the supported paths:
> - `/usr/lib/enigma2/python/Plugins/Extensions/CiefpPlugins/pictures.txt`
> - `/tmp/pictures.txt`
> - `/usr/share/enigma2/pictures.txt`

---

## 🔄 Auto-Update

The plugin checks for updates on startup from:
```
https://raw.githubusercontent.com/ciefp/CiefpPlugins/main/version.txt
```

If a new version is available, you will be prompted to update.  
The update process:
1. Backs up `installed_plugins.txt`
2. Downloads and runs the latest installer
3. Restores the backup
4. Restarts Enigma2

---

## 📝 Logging

Logs are saved to:
- `/tmp/ciefp_plugin.log` (primary)
- `/tmp/ciefp_plugin_fallback.log` (if primary fails)

Use `cat /tmp/ciefp_plugin.log` via telnet/SSH for debugging.

---

## ⚙️ Configuration

- Language selection: **Yellow button**
- Install plugin: **Green button**
- View images: **Blue button**
- Exit: **Red button** or **EXIT**

---

## 🐛 Troubleshooting

| Issue | Solution |
|------|----------|
| No descriptions | Check `/descriptions/<lang>/` folder |
| Images not loading | Verify `pictures.txt` path/format |
| Update fails | Check internet & GitHub access |
| Icons missing | Reinstall plugin or clear cache |

---

## 🤝 Contributing

Want to add a new language or plugin?  
1. Fork the repo: [github.com/ciefp/CiefpPlugins](https://github.com/ciefp/CiefpPlugins)
2. Add description in `/descriptions/your_lang/`
3. Update `PLUGIN_LIST` if adding a new plugin
4. Submit a Pull Request

---

## ❤️ Support

⭐ **Star the repo** if you like it!  
🐛 Report issues on GitHub  
📧 Contact: [@ciefp on X](https://x.com/ciefp)

---

## 📄 License

This plugin is free for personal, non-commercial use.  
All included third-party tools retain their original licenses.

---

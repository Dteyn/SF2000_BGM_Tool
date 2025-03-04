# Kerokero - SF2000 + GB300 BGM Tool

**Kerokero** is a tool designed to streamline the process of creating background music for the SF2000 family of consoles, to replace the original main menu theme music. It allows users to import .MP3 or .WAV audio and easily set 'in' and 'out' points for a clip of up to 90 seconds. Users can preview the clip including the transition point, and can fine-tune the 'in' and 'out' points by the millisecond to create a seamless loop. The clip can then be saved in `pagefile.sys` format (specific to the SF2000 family of retro handhelds), or in .MP3 or .WAV format.

<img src="https://github.com/Dteyn/SF2000_BGM_Tool/raw/beta/screenshot-v020.png" alt="Screenshot of Kerokero running" width="425" height="550"/>

## Features

- **Load Audio Files:** Supports loading and playback of audio files in .WAV and .MP3 formats.
- **Set In and Out Points:** Allows users to define the start ('in') and end ('out') points of the audio clip with millisecond precision.
- **Preview Clips:** Users can preview the entire clip or just the section where the repeat occurs (at the start/end of the file).
- **Save in Various Formats:** The edited clip can be saved in a format specific to SF2000 family of consoles, as well as in .WAV or .MP3 formats.
- **Adjust Gain Level:** Users have the ability to adjust the gain level for both the preview and the processed audio, ensuring the output is just right.

## How to Use

- **Load an Audio File:** Start by loading an audio file in either .WAV or .MP3 format. It can be anything you wish.
- **Set In and Out Points:** Define the 'in' and 'out' points of your clip using the respective fields. The clip can be a maximum of 90 seconds.
- **Preview the Clip:** Use the preview feature to listen to the entire clip or just the section where the repeat occurs. This helps in making precise edits.
- **Refine In and Out Points:** Using the preview, refine your in and out points until the loop transition is seamless.
- **Adjust Gain Level:** If necessary, adjust the gain level to increase or decrease the volume of the audio.
- **Save the Clip:** Once satisfied with the edits, save the clip in the desired format - SF2000+GB300 format ('pagefile.sys'), .WAV, or .MP3.

## Video Tutorial

Refer to this video tutorial on how to use Kerokero:

### Howto video (includes subtitles for 24 languages):
https://dteyn.github.io/kerokero-howto/kerokero_howto.html

### YouTube video (English subtitles only)
[![Kerokero SF2000 & GB300 BGM Tool - Customize the background music on your SF2000 or GB300 handheld!
](https://img.youtube.com/vi/TooufbQlNdg/0.jpg)](https://www.youtube.com/watch?v=TooufbQlNdg)

## Installation

As of version 0.2.0, Kerokero is now distributed in two versions: a Python script, as well as a Windows executable (.EXE) created using [PyInstaller](https://pyinstaller.org/).

### Prerequisites

This script uses PyDub, which requires [ffmpeg](https://www.ffmpeg.org) to be installed. To avoid errors, make sure you have ffmpeg installed prior to running Kerokero.

### Instructions for Standalone .EXE version:
1. Download the latest `Kerokero-win-vx.x.x.zip` file from the [releases page](https://github.com/Dteyn/SF2000_BGM_Tool/releases)
2. Extract the .zip file to a new folder
3. Double click the .EXE file to start Kerokero

NOTE: Windows Defender or some Anti-Virus programs may identify the .EXE file as a trojan. This is a [common issue with PyInstaller](https://www.google.com/search?q=pyinstaller+virus+warning). Since Kerokero is open source, you can review the source code by looking at the Github reposistory and see that it is not doing anything malicious: https://github.com/Dteyn/SF2000_BGM_Tool. If this warning bothers you, you can also run the Python version and avoid the .EXE file altogether.

### Instructions for Python version:
1. Ensure you have Python 3.6+ and the required packages installed (see below)
2. Download the latest `Kerokero-python-vx.x.x.zip` file from the [releases page](https://github.com/Dteyn/SF2000_BGM_Tool/releases)
3. Run the script by double-clicking on `kerokero.py`

NOTE: If you are on Windows and want to disable the console window, rename the script to `kerokero.pyw`. By changing the extension to `pyw`, Python will not show the console window.

## Pre-Requisites

Before you can run the script, you need to install Python 3.6+ as well as several Python packages. Here's how you can install them:

### Python
Ensure that you have [Python 3.6+](https://www.python.org/downloads/) installed on your system. You can verify your Python installation by opening a command prompt and typing:

```shell
python --version
```

Your Python version must be at least 3.6 or higher for this script to function.

### Installing Packages

This script requires several packages, which are contained in `requirements.txt`. To install the necessary packages, run the following command in your terminal or command prompt:

```shell
pip install -r requirements.txt
```

Windows users can also double-click the `install-required-packages.bat` to easily install the required packages.

### Packages Required

[NumPy](https://numpy.org/): A powerful library for working with arrays and matrices of numeric data. In this script, it is used to manipulate audio data as arrays.

[sounddevice](https://python-sounddevice.readthedocs.io): A library that provides a simple way to play audio. It is used to play the audio previews in the script.

[Pydub](https://github.com/jiaaro/pydub): A high-level audio library that makes it easy to work with audio files. It is used to load and manipulate audio data in the script.

[PyQt5](https://pypi.org/project/PyQt5/): A set of Python bindings for The Qt Company’s Qt application framework. It is used to create the graphical user interface for the script.

**Version Numbers:**

Below are the versions which Kerokero was developed against:
- Python v3.12.5
- NumPy v1.26.4
- sounddevice v0.5.1
- Pydub v0.25.1
- PyQt5 v5.15.11

### Linux Users

When testing on Linux, I found that the `PortAudio` library is required. You can install this by using the following commands:

**Debian/Ubuntu and derivatives:**
```shell
sudo apt-get update
sudo apt-get install portaudio19-dev
```

**Fedora:**
```shell
sudo dnf install portaudio-devel
```

**Arch Linux:**
```shell
sudo pacman -S portaudio
```

Also, as noted above, PyDub requires ffmpeg to be installed, so make sure you have that installed as well.

## Known Issues

Some users encountered a 'WinError 2' error with the previous version of Kerokero (v0.1.0). I've tried to address this in v0.2.0, but if the issue still occurs - and you have [ffmpeg](https://www.ffmpeg.org) installed - it would be helpful to have some  context on the issue. I've added more logging to the `output.log` file to help diagnose this and any other issues.

If you encounter an issue, please create an issue on the [Issues](https://github.com/Dteyn/SF2000_BGM_Tool/issues) tab. Please provide the `output.log` file as well as a detailed description of the steps taken to encounter the error.

Reminder: you must have [ffmpeg](https://www.ffmpeg.org/) installed to avoid errors.

## About the Name "Kerokero"
The name "Kerokero" is inspired by the onomatopoeic representation of a frog's croak in Japanese. In the context of this project, it symbolizes the script's ability to seamlessly loop audio clips, akin to the repetitive croaking of a frog. It embodies the script's core functionality of creating continuous, looping audio, providing users with a tool that can create immersive and uninterrupted audio experiences, much like the echoing croaks of frogs in nature.

## Contributing

Feel free to fork the repository and submit pull requests for any improvements or bug fixes. 

## License

[CC0 1.0 Universal](LICENSE)

## Changelog

### v0.2.0:
- Added the ability to save 22050 Hz `pagefile.sys` files for use with BGM Samplerate Fix.
- Removed Windows-specific packages:
  - Replaced `SimpleAudio` with `sounddevice`.
  - Using `tkinter` for error message if packages are missing.
- Added more error checking:
  - Python version check.
  - Added default output filename of `pagefile.sys`.
  - Ensure user is not trying to save output file as input file.
- Improved logging to `output.log` with more detailed information and cleaner log format.
- Resolved all PyCharm warnings.
- Added `requirements.txt` with required packages as well as `install-required-packages.bat` for easy installation.
- Added `build.bat` and `versioninfo` for Windows .EXE build (thanks to tadpole author EricGoldsteinNz!).

### v0.1.0:
- Kerokero initial release.

## Acknowledgements

- Thanks to `notv37` and `bnister` for their initial research and technical insights into the SF2000's audio format.
- Thanks to `EricGoldsteinNz` for `build.bat` and `versioninfo` which were used to create a EXE version of Kerokero.
- Application icon 'kerokero.ico' is from @ptra on Pixabay: https://pixabay.com/vectors/frog-animal-comic-comic-drawing-3241108/

## More Information about the SF2000 & GB300 Consoles
 
- [SF2000 Information Repository](https://github.com/vonmillhausen/sf2000) by `VonMillhausen` contains comprehensive information about the SF2000 retro handheld
- [GB300 Information Repository](https://nummacway.github.io/gb300/) by `nummacway` is a great resource for learning more about the GB300 handheld and differences it has from the SF2000 console.
- [SF2000 Collection](https://zerter555.github.io/sf2000-collection/) by `Zerter` is a great place to customize your Froggy 
- [GB300+SF2000 Tool](https://github.com/nummacway/gb300-sf2000-tool) by `nummacway` is a great tool for managing your SF2000 and GB300 handhelds.
- [tadpole](https://github.com/EricGoldsteinNz/tadpole) by `EricGoldsteinNz` and `BeastGriever` is the best GUI app to manage your SF2000
- [frogtool](https://github.com/tzlion/frogtool) by `taizou` is a handy Python script for managing your SF2000 game library
- [Retro Handhelds Discord](https://discord.gg/retrohandhelds) is the best place to find up-to-date info and chat with other Froggy enthusiasts and developers

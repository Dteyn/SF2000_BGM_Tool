# Kerokero - SF2000 BGM Tool

**Kerokero** is a tool designed to streamline the process of creating seamless looping audio clips. With support for both .WAV and .MP3 formats, it allows users to easily set 'in' and 'out' points, preview clips, and save their work in various formats, including a custom format specific to the Data Frog SF2000 retro handheld.

[[https://github.com/Dteyn/SF2000_BGM_Tool/blob/beta/screenshot.png|alt=Screenshot of Kerokero running]]


## Features

- **Load Audio Files:** Supports loading and playback of audio files in .WAV and .MP3 formats.
- **Set In and Out Points:** Allows users to define the start ('in') and end ('out') points of the audio clip with millisecond precision.
- **Preview Clips:** Users can preview the entire clip or just the section where the repeat occurs (at the start/end of the file).
- **Save in Various Formats:** The edited clip can be saved in a format specific to Data Frog SF2000, as well as in .WAV or .MP3 formats.
- **Adjust Gain Level:** Users have the ability to adjust the gain level for both the preview and the processed audio, ensuring the output is just right.

## How to Use

- **Load an Audio File:** Start by loading an audio file in either .WAV or .MP3 format. It can be anything you wish.
- **Set In and Out Points:** Define the 'in' and 'out' points of your clip using the respective fields. The clip can be a maximum of 90 seconds.
- **Preview the Clip:** Use the preview feature to listen to the entire clip or just the section where the repeat occurs. This helps in making precise edits.
- **Refine In and Out Points:** Using the preview, refine your in and out points until the loop transition is seamless.
- **Adjust Gain Level:** If necessary, adjust the gain level to increase or decrease the volume of the audio.
- **Save the Clip:** Once satisfied with the edits, save the clip in the desired format - SF2000 format ('pagefile.sys'), .WAV, or .MP3.

## Installation & Usage

1. Ensure you have Python and the required packages installed (see below)
2. Download the latest release from the [releases page](https://github.com/Dteyn/SF2000_BGM_Tool/releases)
3. Run the script by double-clicking on `kerokero.pyw`

NOTE: If the script doesn't load, see 'Pre-Requisites' below.

## Pre-Requisites

Before you can run the script, you need to install Python as well as several Python packages. Here's how you can install them:

### Python
Ensure that you have [Python 3.x](https://www.python.org/downloads/) installed on your system. You can verify your Python installation by opening a command prompt and typing:

```shell
python --version
```

### Installing Packages

This script requires several packages. To install the necessary packages, run the following command in your terminal or command prompt:

```shell
pip install numpy simpleaudio pydub PyQt5
```
### Package Descriptions

[NumPy](https://numpy.org/): A powerful library for working with arrays and matrices of numeric data. In this script, it is used to manipulate audio data as arrays.

[SimpleAudio](https://pypi.org/project/simpleaudio/): A library that provides a simple way to play audio. It is used to play the audio previews in the script.

[Pydub](https://github.com/jiaaro/pydub): A high-level audio library that makes it easy to work with audio files. It is used to load and manipulate audio data in the script.

[PyQt5](https://pypi.org/project/PyQt5/): A set of Python bindings for The Qt Company’s Qt application framework. It is used to create the graphical user interface for the script.


The script also uses several built-in Python modules:

**logging**: A built-in Python module for logging messages. It is used to record events occurring while the script is running.

**os**: A built-in Python module that provides a way of using operating system dependent functionality, like reading or writing to the file system.

**sys**: Another built-in Python module that provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter.

**threading**: A built-in Python module to work with threads. It is used to create a smoother user interface experience by running some tasks in separate threads.

**time**: A built-in Python module that provides various time-related functions. It is used to control the timing of various operations in the script.


## About the Name "Kerokero"
The name "Kerokero" is inspired by the onomatopoeic representation of a frog's croak in Japanese. In the context of this project, it symbolizes the script's ability to seamlessly loop audio clips, akin to the repetitive croaking of a frog. It embodies the script's core functionality of creating continuous, looping audio, providing users with a tool that can create immersive and uninterrupted audio experiences, much like the echoing croaks of frogs in nature.


## Contributing

Feel free to fork the repository and submit pull requests for any improvements or bug fixes. 

## License

[CC0 1.0 Universal](LICENSE)


## Acknowledgements

- Thanks to `notv37` and `bnister` for their initial research and technical insights into the SF2000's audio format.
- Application icon 'kerokero.ico' is from @ptra on Pixabay: https://pixabay.com/vectors/frog-animal-comic-comic-drawing-3241108/

## More Information about the Data Frog SF2000
 
- [SF2000 Information Repository](https://github.com/vonmillhausen/sf2000) by `VonMillhausen` contains comprehensive information about the SF2000 retro handheld
- [SF2000 Collection](https://zerter555.github.io/sf2000-collection/) by `Zerter` is a great place to customize your Froggy 
- [tadpole](https://github.com/EricGoldsteinNz/tadpole) by `EricGoldsteinNz` and `BeastGriever` is the best GUI app to manage your SF2000
- [frogtool](https://github.com/tzlion/frogtool) by `taizou` is a handy Python script for managing your SF2000 game library
- [Retro Handhelds Discord](https://discord.gg/retrohandhelds) in the `#🐸data-frog-sf2000` (Other Devices category) is the best place to find up-to-date info and chat with other Froggy enthusiasts



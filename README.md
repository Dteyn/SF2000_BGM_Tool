# SF2000 Audio Converter

A Python tool to convert audio files to a compatible format for the Data Frog SF2000 handheld gaming console. Supports WAV input and outputs in 16-bit signed little-endian format, ready for use on the SF2000.

## Features

- File dialog for selecting input and output files.
- Automatically converts stereo audio to mono.
- Resamples audio to 21560 Hz, the optimal rate for the SF2000.
- Trims audio files longer than 1 minute and 30 seconds to fit within the SF2000's limitations.

## Installation & Usage

1. Download the 'main.py' file from this repository.
2. Navigate to the project directory in a terminal.
3. Install the required Python packages with the following command:
`pip install pydub`
4. Run the script with the following command:
  `python main.py`
5. Select the input WAV file and specify the output file name (usually `pagefile.sys`).
6. The script will process the audio and save it in the correct format for the SF2000.
7. Replace the existing `pagefile.sys` file in the Resources folder on your SF2000 microSD card with the newly generated file.

## Contributing

Feel free to fork the repository and submit pull requests for any improvements or bug fixes. 

## License

[CC0 1.0 Universal](LICENSE)

## Acknowledgements

- Thanks to notv37 and bnister for their initial research and technical insights into the SF2000's audio format.

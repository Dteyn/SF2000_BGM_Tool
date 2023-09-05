from tkinter import filedialog
from pydub import AudioSegment


def process_audio_for_sf2000(input_file, output_file):
    """
    Processes an audio file for the SF2000 handheld.

    Parameters:
    input_file (str): Path to the input WAV file.
    output_file (str): Path to the output file (pagefile.sys).

    Returns:
    None
    """
    # Load the audio file
    audio = AudioSegment.from_wav(input_file)

    # Check if the audio is longer than 1 minute 30 seconds
    if len(audio) > 90 * 1000:
        print("The audio is longer than 1 minute 30 seconds. Trimming...")
        audio = audio[:90 * 1000]

    # Down-mix to mono if stereo
    if audio.channels > 1:
        audio = audio.set_channels(1)

    # Resample the audio to 21560 Hz
    audio = audio.set_frame_rate(21560)

    # Export the audio in a 16-bit signed little-endian format
    audio.export(output_file, format="s16le")


if __name__ == "__main__":
    input_file_text = "Select the .WAV file to convert"
    output_file_text = "Select the output file"
    output_filename = "pagefile.sys"

    input_audio_file = filedialog.askopenfilename(filetypes=[('WAV Files', '*.wav')], title=input_file_text)
    output_audio_file = filedialog.asksaveasfilename(filetypes=[('SF2000 pagefile.sys file', '*.sys')],
                                                     title=output_file_text, confirmoverwrite=True)

    process_audio_for_sf2000(input_audio_file, output_audio_file)
    print(f"Processed audio saved as {output_audio_file}. Replace the existing pagefile.sys file in the "
          f"Resources folder on your SF2000 microSD card.")

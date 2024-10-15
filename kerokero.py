# Kerokero.py - SF2000+GB300 BGM Tool by Dteyn
# https://github.com/Dteyn/SF2000_BGM_Tool

import sys

script_version = "0.2.0"

# VERSION CHECK - Python >3.6 is required
if sys.version_info < (3, 6):
    print("This script requires Python 3.6 or later.")
    sys.exit(1)


# PACKAGE CHECK - Check if packages required are installed, if not, display an error message
packages_required = {
    "numpy": "numpy",
    "sounddevice": "sounddevice",
    "pydub": "pydub",
    "PyQt5": "PyQt5"
}


def check_packages():
    """Checks for missing packages that are required by this script"""
    packages_missing = []

    for lib_name, lib_import in packages_required.items():
        try:
            __import__(lib_import)
        except ImportError:
            packages_missing.append(lib_name)

    return packages_missing


def show_error_message(package_list):
    """Displays an error message if required packages are not found."""
    # Prepare the message
    error_message = f"The following packages are required, but not installed: \n\n{', '.join(package_list)}\n\n\n" \
                    f"Please install the packages using 'pip install -r requirements.txt', " \
                    f"or by running 'install-required-packages.bat'.\n\n" \
                    f"Then run the script again and it should function normally."

    try:
        import tkinter as tk
        from tkinter import messagebox

        # Create a root window and hide it
        root = tk.Tk()
        root.withdraw()

        # Show the error message
        print("ERROR: " + error_message)
        messagebox.showerror("Required Packages Missing", error_message)

        # Destroy the root window after displaying the message
        root.destroy()

    except ImportError:
        # Failsafe: if tkinter is not available, use console output only
        print("ERROR: " + error_message)


# Check for missing packages, if any are missing display an error. If not, proceed with imports
missing_packages = check_packages()

if missing_packages:
    show_error_message(missing_packages)
    sys.exit(1)  # Terminate with error code 1
else:
    import locale
    import logging
    import numpy as np
    import os
    import platform
    import sounddevice as sd
    import threading
    import time
    from datetime import datetime
    from PyQt5.QtCore import QTimer
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QApplication, QFrame, QWidget, QVBoxLayout, QPushButton, QLabel
    from PyQt5.QtWidgets import QFileDialog, QLineEdit, QMessageBox, QHBoxLayout, QTextEdit
    from pydub import AudioSegment


class AudioConverterApp(QWidget):
    def __init__(self):
        super().__init__()

        # Set the timer interval for updating current position in ms
        self.timer_interval = 10

        # Initialize instance attributes
        self.layout = None
        self.file_label = None
        self.select_button = None
        self.file_info_text_edit = None
        self.transport_layout = None
        self.mark_in_button = None
        self.play_button = None
        self.stop_button = None
        self.mark_out_button = None
        self.current_position_label = None
        self.clip_length_label = None
        self.start_pos_label = None
        self.start_pos = None
        self.end_position_label = None
        self.end_position = None
        self.gain_label = None
        self.gain_adjust = None
        self.preview_button = None
        self.preview_loop_button = None
        self.stop_preview_button = None
        self.process_button = None
        self.audio_file = None
        self.audio_filename_only = None
        self.audio = None
        self.timer = None
        self.current_position = None
        self.playing = None
        self.preview_segment = None
        self.preview_samples = None
        self.previewing = None
        self.preview_thread = None
        self.preview_segment_splice = None
        self.clip_segment = None
        self.play_segment = None
        self.play_samples = None

        # Set up the UI
        self.init_ui()

    def init_ui(self):
        """Sets up the User Interface elements"""
        logging.debug("Entering init_ui method")
        self.layout = QVBoxLayout()

        # Label for the currently selected file
        self.file_label = QLabel('No file selected')
        self.layout.addWidget(self.file_label)

        # Select File button
        self.select_button = QPushButton('Select File')
        # noinspection PyUnresolvedReferences
        self.select_button.clicked.connect(self.select_file)
        self.select_button.setFixedHeight(50)
        self.select_button.setToolTip("Select the audio file to process")
        self.layout.addWidget(self.select_button)

        # File information area
        self.file_info_text_edit = QTextEdit(self)
        self.file_info_text_edit.setReadOnly(True)
        self.file_info_text_edit.setFixedHeight(80)
        self.layout.addWidget(self.file_info_text_edit)

        # Create a horizontal layout for the transport controls
        self.transport_layout = QHBoxLayout()

        # 'Mark In' Button - marks the clip starting point when playing an audio track
        self.mark_in_button = QPushButton('Mark In')
        # noinspection PyUnresolvedReferences
        self.mark_in_button.clicked.connect(self.mark_in)
        self.mark_in_button.setFixedHeight(40)
        self.mark_in_button.setEnabled(False)
        self.mark_in_button.setToolTip("Set the start point of the audio clip")
        self.transport_layout.addWidget(self.mark_in_button)

        # 'Play' Button - plays the currently selected audio file
        self.play_button = QPushButton('Play')
        # noinspection PyUnresolvedReferences
        self.play_button.clicked.connect(self.play_audio)
        self.play_button.setFixedHeight(40)
        self.play_button.setEnabled(False)
        self.play_button.setToolTip("Play the selected audio file")
        self.transport_layout.addWidget(self.play_button)

        # 'Stop' button - stops playback of the currently playing file
        self.stop_button = QPushButton('Stop')
        # noinspection PyUnresolvedReferences
        self.stop_button.clicked.connect(self.stop_audio)
        self.stop_button.setFixedHeight(40)
        self.stop_button.setEnabled(False)
        self.stop_button.setToolTip("Stop playback")
        self.transport_layout.addWidget(self.stop_button)

        # 'Mark Out' Button - marks the clip ending point when playing an audio track
        self.mark_out_button = QPushButton('Mark Out')
        # noinspection PyUnresolvedReferences
        self.mark_out_button.clicked.connect(self.mark_out)
        self.mark_out_button.setFixedHeight(40)
        self.mark_out_button.setEnabled(False)
        self.mark_out_button.setToolTip("Set the end point of the audio clip")
        self.transport_layout.addWidget(self.mark_out_button)

        # Add the transport layout to the main layout
        self.layout.addLayout(self.transport_layout)

        # Current position label - initialize as blank and will be filled in later
        self.current_position_label = QLabel('')
        self.layout.addWidget(self.current_position_label)

        # Clip length label - initialize as blank and will be filled in later
        self.clip_length_label = QLabel('')
        self.layout.addWidget(self.clip_length_label)

        # 'Start Position' label and input box - the start point of the audio clip in ms
        self.start_pos_label = QLabel('Start Position (ms):')
        self.layout.addWidget(self.start_pos_label)
        self.start_pos = QLineEdit('')
        self.start_pos.setToolTip("The start point of the audio clip")
        # noinspection PyUnresolvedReferences
        self.start_pos.textChanged.connect(self.update_clip_length)
        self.layout.addWidget(self.start_pos)

        # 'End Position' label and input box
        self.end_position_label = QLabel('End Position (ms):')
        self.layout.addWidget(self.end_position_label)
        self.end_position = QLineEdit('')
        # noinspection PyUnresolvedReferences
        self.end_position.textChanged.connect(self.update_clip_length)
        self.end_position.setToolTip("The end point of the audio clip")
        self.layout.addWidget(self.end_position)

        # Gain adjustment label and input box - allows the user to raise or lower the volume of the clip
        self.gain_label = QLabel('Gain Adjustment (dB):')
        self.layout.addWidget(self.gain_label)
        self.gain_adjust = QLineEdit('0')
        self.gain_adjust.setToolTip("Make the audio louder or quieter by adjusting the gain in dB (ex. +3 or -3)")
        self.layout.addWidget(self.gain_adjust)

        # 'Preview Full Clip' button - preview the entire audio clip and loop. Clip is pre-looped 3x to prevent delay
        self.preview_button = QPushButton('Preview Full Audio Clip')
        # noinspection PyUnresolvedReferences
        self.preview_button.clicked.connect(self.preview_audio)
        self.preview_button.setFixedHeight(50)
        self.preview_button.setEnabled(False)
        self.preview_button.setToolTip("Preview the entire audio clip from start to finish, looped 3x")
        self.layout.addWidget(self.preview_button)

        # 'Preview Loop Transition' button - previews the loop point in the audio clip
        self.preview_loop_button = QPushButton('Preview Loop Transition')
        # noinspection PyUnresolvedReferences
        self.preview_loop_button.clicked.connect(self.preview_loop_repeat)
        self.preview_loop_button.setFixedHeight(50)
        self.preview_loop_button.setEnabled(False)
        self.preview_loop_button.setToolTip("Preview the repeat point in the looped audio clip.\n"
                                            "Plays the last 5 seconds and first 5 seconds of the clip"
                                            "so that you can preview how well the repeat joins up."
                                            "NOTE: Requires a minimum 10 second audio clip")
        self.layout.addWidget(self.preview_loop_button)

        # 'Stop Preview' button - stops the currently playing preview
        self.stop_preview_button = QPushButton('Stop Preview')
        # noinspection PyUnresolvedReferences
        self.stop_preview_button.clicked.connect(self.stop_preview)
        self.stop_preview_button.setFixedHeight(50)
        self.stop_preview_button.setEnabled(False)
        self.stop_preview_button.setToolTip("Stop playback of the preview")
        self.layout.addWidget(self.stop_preview_button)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(divider)

        # 'Save Audio Clip' Button - save the audio clip in SF2000 or .WAV/.MP3 format
        self.process_button = QPushButton('Save Audio Clip')
        # noinspection PyUnresolvedReferences
        self.process_button.clicked.connect(self.process_audio)
        self.process_button.setFixedHeight(80)
        self.process_button.setEnabled(False)
        self.process_button.setToolTip("Process the audio and save the audio clip to file")
        self.layout.addWidget(self.process_button)

        # Set the layout and display the window
        self.setLayout(self.layout)
        self.setWindowTitle(f'Kerokero v{script_version} by Dteyn')
        self.show()

        # Lock the window size
        self.setFixedSize(self.size())

        logging.debug("Exiting init_ui method\n")

    def select_file(self):
        """Prompts the user to select a .WAV or .MP3 file for input, loads the file and displays information"""
        logging.debug("Entering select_file method")
        try:
            self.audio_file, _ = QFileDialog.getOpenFileName(self, "Select the .WAV or .MP3, or .SYS file to convert",
                                                             "",
                                                             "Audio Files (*.wav *.mp3 *.sys)")
            self.audio_filename_only = os.path.basename(self.audio_file)

            if self.audio_file:
                self.file_label.setText(self.audio_filename_only)
                logging.info(f"Selected file: {self.audio_file}")
                logging.debug(f"Filename only: {self.audio_filename_only}")

                # Check the file extension to determine the action
                file_extension = os.path.splitext(self.audio_file)[1].lower()

                if file_extension in ['.wav', '.mp3']:
                    # Load audio file and display information
                    self.audio = AudioSegment.from_file(self.audio_file)

                    # Get the duration in mm:ss format
                    minutes, seconds = divmod(len(self.audio) // 1000, 60)
                    duration_formatted = f"{minutes}:{seconds:02d}"

                    # Get the number of channels, display Stereo or Mono accordingly
                    if self.audio.channels > 1:
                        channels_text = "Stereo"
                    else:
                        channels_text = "Mono"

                    # Display the file information
                    file_info_text = (
                        f"Format: {self.audio_file.split('.')[-1].upper()}, "
                        f"Length: {len(self.audio)} ms ({duration_formatted}), "
                        f"Sample Rate: {self.audio.frame_rate}Hz, "
                        f"Channels: {channels_text}, "
                        f"Bit Depth: {self.audio.sample_width * 8}-bit"
                    )
                    self.file_info_text_edit.setText(file_info_text)
                    logging.info(f"Input File Information:\n {file_info_text}")

                    # Set up a timer to display the current position
                    self.timer = QTimer()
                    # noinspection PyUnresolvedReferences
                    self.timer.timeout.connect(self.update_current_position)
                    self.timer.setInterval(self.timer_interval)
                    self.current_position = 0
                    self.playing = False

                    # Enable buttons in the UI
                    self.play_button.setEnabled(True)
                    self.preview_button.setEnabled(True)
                    self.preview_loop_button.setEnabled(True)
                    self.process_button.setEnabled(True)

                elif file_extension == '.sys':
                    # Ask the user if they would like to convert an existing .sys file
                    reply = QMessageBox.question(self, 'Convert .SYS File to 22050 Hz',
                                                 "You have selected an existing pagefile.sys file.\n"
                                                 "This tool can resample an existing pagefile.sys\n"
                                                 "file to 22050 Hz, to fix the playback speed if\n"
                                                 "you have applied the BGM Sample Rate fix.\n\n"
                                                 "Would you like to resample the file?\n",
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                    if reply == QMessageBox.Yes:
                        # Proceed to convert the .sys file
                        self.convert_sys_file()
                    else:
                        # User chose not to convert the .sys file or closed the dialog, cancel the operation
                        return
            else:
                logging.info("File selection was cancelled")

        except Exception as e:
            logging.error(f"Error selecting file: {e}")
            QMessageBox.critical(self, "Error Selecting File", str(e))
        logging.debug("Exiting select_file method\n")

    def convert_sys_file(self):
        """
        Converts an audio file from 21560 Hz to 22050 Hz and allows the user to select the output file path.
        """
        logging.debug("Entering convert_sys_file method")
        try:
            # Specify the parameters for the RAW audio file
            sample_rate = 21560  # Original sample rate
            channels = 1  # Mono
            sample_width = 2  # 16-bit

            # Load the RAW audio file
            audio = AudioSegment.from_raw(self.audio_file,
                                          sample_width=sample_width,
                                          frame_rate=sample_rate,
                                          channels=channels)

            # Convert the sample rate to 22050 Hz
            converted_audio = audio.set_frame_rate(22050)

            # Prompt the user to select the output file path
            while True:
                output_file_path, _ = QFileDialog.getSaveFileName(None, "Save Converted File", "",
                                                                  "SYS Files (*.sys)")

                if not output_file_path:
                    # User cancelled the save dialog
                    return

                if output_file_path == self.audio_file:
                    # Warn the user if they attempt to save over the original file
                    QMessageBox.warning(self, "Cannot Overwrite Original File",
                                        "Cannot save over the original file. Please type a new filename,"
                                        "or save in a different folder.")
                    continue  # Prompt the save dialog again

                break  # Exit the loop if a valid new filename is provided

            # Save the converted audio
            converted_audio.export(output_file_path, format="s16le")  # Save as 16-bit little-endian

            QMessageBox.information(self, "Success", f"File converted successfully and saved to {output_file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during the conversion: {e}")
        logging.debug("Exiting convert_sys_file method\n")

    def preview_audio(self):
        """Previews the audio clip based on the start point and end point. Gain adjustment is applied if specified
        Uses: pydub for processing audio, NumPy for samples array and sounddevice for playing the preview
        """
        logging.debug("Entering preview_audio method")
        try:
            # Get the start position, end position, and calculate the clip length
            start_pos = float(self.start_pos.text())
            end_pos = float(self.end_position.text())
            clip_length = end_pos - start_pos

            # Make sure the clip length is over 100 milliseconds
            if clip_length > 90000 or clip_length <= 99:
                raise ValueError("Clip length must be between 100 and 90,000 milliseconds.")

            # Create the preview segment
            self.preview_segment = self.audio[start_pos:end_pos]

            # Pre-loop the preview segment 3 times to create a seamless loop
            self.preview_segment = self.preview_segment * 3

            # Apply the gain adjustment if specified
            gain_value = float(self.gain_adjust.text())

            if gain_value != 0:
                self.preview_segment = self.preview_segment.apply_gain(gain_value)
                logging.info(f"Gain adjustment applied: {gain_value} dB")

            # Convert the pydub AudioSegment to numpy array
            self.preview_samples = np.array(self.preview_segment.get_array_of_samples())
            self.preview_samples = self.preview_samples.reshape((-1, self.preview_segment.channels))

            logging.info(f"Preview segment created: "
                         f"Start point: {start_pos} ms, "
                         f"End point: {end_pos} ms, "
                         f"# samples: {len(self.preview_samples)}")

            # Disable the 'Preview Audio' and 'Play' buttons while the audio is playing
            self.preview_button.setEnabled(False)
            self.preview_loop_button.setEnabled(False)
            self.play_button.setEnabled(False)

            # Enable the 'Stop Preview' button
            self.stop_preview_button.setEnabled(True)

            # Indicate the preview is playing
            self.previewing = True

            # Create a thread so the preview will play repeatedly until stopped
            self.preview_thread = threading.Thread(target=self.loop_preview)
            self.preview_thread.start()

        except ValueError as e:
            QMessageBox.critical(self, "Invalid input", str(e))
            logging.error(f"Invalid input: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            logging.error(f"An error occurred in preview_audio method: {e}")
        logging.debug("Exiting preview_audio method\n")

    def preview_loop_repeat(self):
        """Creates a section of audio of the last 5 seconds and first 5 seconds of the track to preview the transition
        Uses: pydub for processing audio, NumPy for samples array and sounddevice for playing the preview
        Creates a thread for previewing the loop repeatedly
        """
        logging.debug("Entering preview_loop_repeat method")
        try:
            # Get the start position, end position, and calculate the clip length
            start_pos = float(self.start_pos.text())
            end_pos = float(self.end_position.text())
            clip_length = end_pos - start_pos
            logging.info("Creating a looped preview at transition point...")
            logging.info(f"Start position: {start_pos} ms, End position: {end_pos} ms, Clip Length: {clip_length} ms")

            # Make sure the clip length is over 10 seconds
            if clip_length > 90000 or clip_length <= 9999:
                raise ValueError("For this preview, clip length must be between 10,000 and 90,000 milliseconds.")

            # Create the preview segment
            self.preview_segment = self.audio[start_pos:end_pos]

            # Apply the gain adjustment if specified
            gain_value = float(self.gain_adjust.text())

            if gain_value != 0:
                self.preview_segment = self.preview_segment.apply_gain(gain_value)
                logging.info(f"Gain adjustment applied: {gain_value} dB")

            # Pre-loop the preview segment twice to create a seamless loop
            self.preview_segment = self.preview_segment * 2

            # Create a segment that consists of the last 5 seconds of the loop and the first 5 seconds of the loop
            loop_point = len(self.preview_segment) // 2  # Find the loop point (end of the first segment)
            preview_start = max(0, loop_point - 5000)  # Start 5 seconds before the loop point
            preview_end = min(len(self.preview_segment), loop_point + 5000)  # End 5 seconds after the loop point

            # Create the spliced transition segment
            self.preview_segment_splice = self.preview_segment[preview_start:preview_end]

            # Convert the pydub AudioSegment to numpy array
            self.preview_samples = np.array(self.preview_segment_splice.get_array_of_samples())
            self.preview_samples = self.preview_samples.reshape((-1, self.preview_segment.channels))

            logging.info(f"Loop point: {loop_point} ms, Preview Start: {preview_start} ms, "
                         f"Preview End: {preview_end} ms")

            # Disable the 'Preview Audio' and 'Play' buttons while the audio is playing
            self.preview_button.setEnabled(False)
            self.preview_loop_button.setEnabled(False)
            self.play_button.setEnabled(False)

            # Enable the 'Stop Preview' button
            self.stop_preview_button.setEnabled(True)

            # Indicate the preview is playing
            self.previewing = True

            # Create a thread so the preview will play repeatedly until stopped
            self.preview_thread = threading.Thread(target=self.loop_preview)
            self.preview_thread.start()

        except ValueError as e:
            QMessageBox.critical(self, "Invalid input", str(e))
            logging.error(f"Invalid input: {e}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            logging.error(f"An error occurred in preview_loop_repeat method: {e}")
        logging.debug("Exiting preview_loop_repeat method\n")

    def loop_preview(self):
        """Plays the loop on repeat until Stop Preview is pressed"""
        # Play the preview loop on repeat until the 'Stop Preview' button is pressed
        while self.previewing:
            # Play the preview segment
            sd.play(self.preview_samples, self.preview_segment.frame_rate)

            # Wait a bit before checking if we should continue playing
            time.sleep(0.2)  # Sleep to prevent busy-waiting

            # Enter a loop until stop preview button is pressed
            while sd.get_stream().active:
                time.sleep(0.2)  # Continue to sleep to prevent busy-waiting
                if not self.previewing:
                    # If preview stop button was clicked, break from the loop
                    break

            # Stop playback
            sd.stop()

            # Small delay to prevent immediate playback
            time.sleep(0.2)

    def stop_preview(self):
        """Stops the currently playing preview that is playing"""
        logging.debug("Entering stop_preview method")
        # Stop the preview playback
        self.previewing = False
        if sd.get_stream().active:
            sd.stop()

        # Disable the 'Stop Preview' button
        self.stop_preview_button.setEnabled(False)

        # Re-enable the 'Preview Audio' and 'Play' buttons when the audio stops
        self.preview_button.setEnabled(True)
        self.preview_loop_button.setEnabled(True)
        self.play_button.setEnabled(True)
        logging.debug("Exiting stop_preview method\n")

    def process_audio(self):
        """Processes the audio clip based on the start and end point and applies gain if specified
        - SF2000+GB300 format: 16-bit signed little-endian, mono, 21560 Hz (to correct for playback speed issue)
        - WAV or MP3 format: Standard options, basic output
        Uses: pydub to process the audio and export the audio segment
        """
        logging.debug("Entering process_audio method")
        try:
            # Get the start position and length from the input fields
            start_pos = float(self.start_pos.text())
            end_pos = float(self.end_position.text())
            clip_length = end_pos - start_pos

            logging.info(f"Start Position: {start_pos} ms, End Position: {end_pos}, Clip Length: {clip_length} ms")

            # Validate the start and end positions
            if end_pos <= start_pos:
                raise ValueError("End position must be greater than start position.")

            # Make sure the clip length is over 100 milliseconds
            if clip_length > 90000 or clip_length <= 99:
                raise ValueError("Clip length must be between 100 and 90,000 milliseconds.")

            # Get the selected segment of the audio
            self.clip_segment = self.audio[start_pos:end_pos]

            # Apply the gain adjustment if specified
            gain_value = float(self.gain_adjust.text())

            if gain_value != 0:
                self.clip_segment = self.clip_segment.apply_gain(gain_value)
                logging.info(f"Gain adjustment applied: {gain_value} dB")

            # Create save dialog, allowing user to choose SF2000+GB300 pagefile.sys or standard .WAV file output
            file_filter = "Default pagefile.sys file (*.sys);;22050hz pagefile.sys file (*.sys);" \
                          "WAV file (*.wav);;MP3 file (*.mp3)"
            default_filename = "pagefile"  # Default filename without extension
            output_file, selected_filter = QFileDialog.getSaveFileName(self, "Save File", default_filename,
                                                                       file_filter)
            logging.info(f"File type selected: {selected_filter}, Output filename: {output_file}")

            # Make sure the user isn't trying to save over the input file
            if output_file == self.audio_file:
                raise ValueError("Input and Output files cannot be the same.\n"
                                 "Please save the output as a new filename.")

            # If the user specified a file to save,
            if output_file:
                # Save as default SF2000 'pagefile.sys' format - 21560hz for stock, unmodified firmware
                if selected_filter == "Default pagefile.sys file (*.sys)":
                    if not output_file.endswith('.sys'):
                        output_file += '.sys'
                    # Down-mix to mono
                    if self.clip_segment.channels > 1:
                        self.clip_segment = self.clip_segment.set_channels(1)
                    # Resample the audio to 21560 Hz for proper playback speed on the SF2000 stock firmware
                    self.clip_segment = self.clip_segment.set_frame_rate(21560)
                    # Export the audio in 16-bit signed little-endian format
                    self.clip_segment.export(output_file, format="s16le")

                # Save as fixed SF2000 'pagefile.sys' format - 22050hz for patched firmware with audio fix
                elif selected_filter == "22050hz pagefile.sys file (*.sys)":
                    if not output_file.endswith('.sys'):
                        output_file += '.sys'
                    # Down-mix to mono
                    if self.clip_segment.channels > 1:
                        self.clip_segment = self.clip_segment.set_channels(1)
                    # Resample the audio to 22050 Hz for proper playback speed on the SF2000 patched firmware
                    self.clip_segment = self.clip_segment.set_frame_rate(22050)
                    # Export the audio in 16-bit signed little-endian format
                    self.clip_segment.export(output_file, format="s16le")

                # Save as .WAV format if specified
                elif selected_filter == "WAV file (*.wav)":
                    if not output_file.endswith('.wav'):
                        output_file += '.wav'
                    # Export the audio in WAV format
                    self.clip_segment.export(output_file, format="wav")

                # Save as .MP3 format if specified
                elif selected_filter == "MP3 file (*.mp3)":
                    if not output_file.endswith('.mp3'):
                        output_file += '.mp3'
                    # Export the audio in MP3 format
                    self.clip_segment.export(output_file, format="mp3")

                QMessageBox.information(self, "Success", f"File successfully saved as {output_file}")
                logging.info(f"File successfully saved as {output_file}")
            else:
                logging.info("File save operation was cancelled")

        except OSError as e:
            if e.errno == 2:  # Error 2 is FileNotFoundError on Windows
                QMessageBox.critical(self, "Error Opening File",
                                     "File could not be found. Please check the file path and try again.\n\n"
                                     "Developer Note: please report the exact steps you took to produce this error")
                logging.error("The specified file could not be found: {}".format(e))
            else:
                # Handle other OSError exceptions that are not WinError 2
                QMessageBox.critical(self, "Error", "An error occurred: {}".format(str(e)))
                logging.error("An error occurred: {}".format(e))
        except Exception as e:
            # Handle other exceptions that are not OSErrors
            QMessageBox.critical(self, "Error", "An unexpected error occurred: {}".format(str(e)))
            logging.error("An unexpected error occurred: {}".format(e))
        logging.debug("Exiting process_audio method\n")

    def update_clip_length(self):
        """Updates the Clip Length label on the UI"""
        try:
            start_pos_text = self.start_pos.text()
            end_pos_text = self.end_position.text()

            # Only update when there are values in both start position and end position
            if not start_pos_text or not end_pos_text:
                return

            # Convert values to float and calculate the clip length
            start_pos = float(start_pos_text)
            end_pos = float(end_pos_text)
            clip_length = end_pos - start_pos

            # Format the clip length in mm:ss format, convert to integer for display
            minutes, seconds = divmod(clip_length / 1000, 60)
            clip_length_formatted = f"{int(minutes)}:{int(seconds):02d}"
            clip_length_display = int(clip_length)

            # Update the clip length on the UI
            self.clip_length_label.setText(f'Clip Length: {clip_length_display} ms ({clip_length_formatted})')

        except ValueError as e:
            QMessageBox.critical(self, "Invalid input", str(e))
            logging.error(f"Invalid input: {e}")

    def mark_in(self):
        """Marks the 'Start Position' when the audio is being previewed"""
        try:
            if self.current_position:
                self.start_pos.setText(str(self.current_position))
                logging.info(f"In point marked: {(str(self.current_position))} ms")
        except Exception as e:
            QMessageBox.critical(self, "Error Marking In Point", str(e))
            logging.error(f"An error occurred in the mark_in method: {e}")

    def mark_out(self):
        """Marks the 'End Position' when the audio is being previewed"""
        try:
            self.end_position.setText(str(self.current_position))
            logging.info(f"Out point marked: {(str(self.current_position))} ms")
        except Exception as e:
            QMessageBox.critical(self, "Error Marking Out Point", str(e))
            logging.error(f"An error occurred in the mark_out method: {e}")

    def play_audio(self):
        """Plays the loaded audio file to preview the audio and set the Start and End points
        Uses: pydub for processing audio and applying gain, NumPy for array, and sounddevice for playback
        """
        logging.debug("Entering play_audio method")
        if not self.playing:
            try:
                # Create a play segment from the loaded pydub audio segment
                self.play_segment = self.audio

                # Apply the gain adjustment if specified
                gain_value = float(self.gain_adjust.text())

                if gain_value != 0:
                    self.play_segment = self.play_segment.apply_gain(gain_value)
                    logging.info(f"Gain adjustment applied: {gain_value} dB")

                # Convert the pydub AudioSegment to numpy array
                self.play_samples = np.array(self.play_segment.get_array_of_samples())
                self.play_samples = self.play_samples.reshape((-1, self.play_segment.channels))

                # Reset position and start playing audio
                self.current_position = 0
                self.playing = True
                self.timer.start()

                logging.info(f"Playing audio: {len(self.play_samples)} samples @ "
                             f"{str(self.play_segment.frame_rate)} Hz")

                # Play the preview segment using sounddevice
                sd.play(self.play_samples, self.play_segment.frame_rate)

                # Disable the 'Preview Audio' and 'Play' buttons while the audio is playing
                self.preview_button.setEnabled(False)
                self.preview_loop_button.setEnabled(False)
                self.play_button.setEnabled(False)

                # Enable the 'Mark In', 'Mark Out', and 'Stop' buttons
                self.mark_in_button.setEnabled(True)
                self.mark_out_button.setEnabled(True)
                self.stop_button.setEnabled(True)

            except ValueError as e:
                QMessageBox.critical(self, "Invalid input", str(e))
                logging.error(f"Invalid input: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Error Playing Audio", str(e))
                logging.error(f"An error occurred in the play_audio method: {e}")
            logging.debug("Exiting play_audio method\n")

    def stop_audio(self):
        logging.debug("Entering stop_audio method")

        try:
            # Re-enable the 'Preview Audio' and 'Play' buttons when the audio stops
            self.preview_button.setEnabled(True)
            self.preview_loop_button.setEnabled(True)
            self.play_button.setEnabled(True)

            # Disable the 'Mark In', 'Mark Out', and 'Stop' buttons
            self.mark_in_button.setEnabled(False)
            self.mark_out_button.setEnabled(False)
            self.stop_button.setEnabled(False)

            # Stop the audio playback and timer
            self.playing = False
            sd.stop()
            self.timer.stop()

            logging.info("Audio and timer stopped.")

        except Exception as e:
            QMessageBox.critical(self, "Error Stopping Audio", str(e))
            logging.error(f"An error occurred in the stop_audio method: {e}")
        logging.debug("Exiting stop_audio method\n")

    def update_current_position(self):
        """Updates the current position label based on the timer started when playback was started
        Will also stop the audio playback once the end of the file is reached
        """
        # Update label to display the current position
        try:
            if self.playing:
                # Increment the current position in sync with timer
                self.current_position += self.timer_interval

                minutes, seconds = divmod(self.current_position / 1000, 60)
                position_formatted = f"{int(minutes)}:{int(seconds):02d}"

                self.current_position_label.setText(
                    f'Current Position: {self.current_position} ms ({position_formatted})')

                # Stop playback once the end of the audio is reached
                if self.current_position >= len(self.audio):
                    logging.info("End of audio reached, stopping playback")

                    # Stop the audio playback and timer
                    self.playing = False
                    self.play_obj.stop()
                    self.timer.stop()

                    # Re-enable the 'Preview Audio' and 'Play' buttons when the audio stops
                    self.preview_button.setEnabled(True)
                    self.preview_loop_button.setEnabled(True)
                    self.play_button.setEnabled(True)

                    # Disable the 'Mark In', 'Mark Out', and 'Stop' buttons
                    self.mark_in_button.setEnabled(False)
                    self.mark_out_button.setEnabled(False)
                    self.stop_button.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Error Updating Position", str(e))
            logging.error(f"An error occurred in the update_current_position method: {e}")


# MAIN ENTRY POINT

# Define a function to gather system information
def get_system_info():
    info = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "operating_system": platform.system() + " " + platform.release(),
        "python_version": sys.version,
        "processor": platform.processor(),
        "default_language": locale.getlocale()[0],
        "time_zone": time.tzname,
        "encoding": locale.getpreferredencoding(),
    }
    return info


# CONFIGURE LOGGING LEVEL

# Logging level can be set to INFO, DEBUG, ERROR, or NONE to disable logging
# Logging destinations can be ['console'], ['file'], or ['console', 'file'].
log_level = 'DEBUG'
log_destinations = ['console', 'file']  # If log_level is NONE, this setting is ignored

# Create a logger
logger = logging.getLogger()

# If log_level is NONE, disable logging
if log_level == "NONE":
    logger.setLevel(100)  # Setting to a level higher than CRITICAL (50) to disable logging
else:
    logger.setLevel(getattr(logging, log_level))

# Create a console handler and set the log level
if 'console' in log_destinations and log_level != "NONE":
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

# Create a file handler and set the log level
if 'file' in log_destinations and log_level != "NONE":
    file_handler = logging.FileHandler('output.log', mode='a')
    file_handler.setLevel(getattr(logging, log_level))
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

system_info = get_system_info()
startup_message = "\n==============================================================================================\n" \
                  f"KEROKERO v{script_version} STARTED\n" \
                  f"Time: {system_info['time']}\n" \
                  f"OS: {system_info['operating_system']}\n" \
                  f"Python Version: {system_info['python_version']}\n" \
                  f"Processor: {system_info['processor']}\n" \
                  f"Default Language: {system_info['default_language']}\n" \
                  f"Time Zone: {system_info['time_zone']}\n" \
                  f"Encoding: {system_info['encoding']}\n"
logger.info(startup_message)

logging.debug("Script initialized - setting up application")

# Set up application
app = QApplication(sys.argv)

# Define the path for both icon files
ico_icon_path = os.path.join(os.path.dirname(__file__), 'kerokero.ico')
svg_icon_path = os.path.join(os.path.dirname(__file__), 'kerokero.svg')

# Check if the .ico file exists
if os.path.exists(ico_icon_path):
    app.setWindowIcon(QIcon(ico_icon_path))
elif os.path.exists(svg_icon_path):
    # If the .ico file doesn't exist, check for the .svg file and use that instead
    app.setWindowIcon(QIcon(svg_icon_path))

# Run the AudioConvertApp class to start the application
ex = AudioConverterApp()

# Exit the application
sys.exit(app.exec_())

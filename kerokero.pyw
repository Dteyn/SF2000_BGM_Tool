import logging
import numpy as np
import os
import sys
import simpleaudio as sa
import threading
import time
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFrame, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtWidgets import QFileDialog, QLineEdit, QMessageBox, QHBoxLayout, QTextEdit
from pydub import AudioSegment

# Configure logging - set INFO, DEBUG, or ERROR level debugging
logging.basicConfig(level=logging.INFO)


class AudioConverterApp(QWidget):
    def __init__(self):
        super().__init__()

        # Set the timer interval for updating current position in ms
        self.timer_interval = 10

        # Set up the UI
        self.init_ui()

    def init_ui(self):
        logging.debug("Entering init_ui method")
        self.layout = QVBoxLayout()

        # Label for the currently selected file
        self.file_label = QLabel('No file selected')
        self.layout.addWidget(self.file_label)

        # Select File button
        self.select_button = QPushButton('Select File')
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
        self.mark_in_button.clicked.connect(self.mark_in)
        self.mark_in_button.setFixedHeight(40)
        self.mark_in_button.setEnabled(False)
        self.mark_in_button.setToolTip("Set the start point of the audio clip")
        self.transport_layout.addWidget(self.mark_in_button)

        # 'Play' Button - plays the currently selected audio file
        self.play_button = QPushButton('Play')
        self.play_button.clicked.connect(self.play_audio)
        self.play_button.setFixedHeight(40)
        self.play_button.setEnabled(False)
        self.play_button.setToolTip("Play the selected audio file")
        self.transport_layout.addWidget(self.play_button)

        # 'Stop' button - stops playback of the currently playing file
        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_audio)
        self.stop_button.setFixedHeight(40)
        self.stop_button.setEnabled(False)
        self.stop_button.setToolTip("Stop playback")
        self.transport_layout.addWidget(self.stop_button)

        # 'Mark Out' Button - marks the clip ending point when playing an audio track
        self.mark_out_button = QPushButton('Mark Out')
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
        self.start_pos = QLineEdit('0')
        self.start_pos.setToolTip("The start point of the audio clip")
        self.start_pos.textChanged.connect(self.update_clip_length)
        self.layout.addWidget(self.start_pos)

        # 'End Position' label and input box
        self.end_position_label = QLabel('End Position (ms):')
        self.layout.addWidget(self.end_position_label)
        self.end_position = QLineEdit('90000')
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
        self.preview_button.clicked.connect(self.preview_audio)
        self.preview_button.setFixedHeight(50)
        self.preview_button.setEnabled(False)
        self.preview_button.setToolTip("Preview the entire audio clip from start to finish, looped 3x")
        self.layout.addWidget(self.preview_button)

        # 'Preview Loop Transition' button - previews the loop point in the audio clip
        self.preview_loop_button = QPushButton('Preview Loop Transition')
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
        self.process_button.clicked.connect(self.process_audio)
        self.process_button.setFixedHeight(80)
        self.process_button.setEnabled(False)
        self.process_button.setToolTip("Process the audio and save the audio clip to file")
        self.layout.addWidget(self.process_button)

        # Set the layout and display the window
        self.setLayout(self.layout)
        self.setWindowTitle('Kerokero - SF2000 BGM Tool')
        self.show()

        # Lock the window size
        self.setFixedSize(self.size())

        logging.debug("Exiting init_ui method")

    def select_file(self):
        """Prompts the user to select a .WAV or .MP3 file for input, loads the file and displays information"""
        logging.debug("Entering select_file method")
        try:
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly
            self.audio_file, _ = QFileDialog.getOpenFileName(self, "Select the .WAV or .MP3 file to convert", "",
                                                             "Audio Files (*.wav; *.mp3)", options=options)
            self.audio_filename_only = os.path.basename(self.audio_file)

            if self.audio_file:
                self.file_label.setText(self.audio_filename_only)
                logging.debug(f"Selected file: {self.audio_file}")

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

                # Set up a timer to display the current position
                self.timer = QTimer()
                self.timer.timeout.connect(self.update_current_position)
                self.timer.setInterval(self.timer_interval)
                self.current_position = 0
                self.playing = False

                # Enable buttons in the UI
                self.play_button.setEnabled(True)
                self.preview_button.setEnabled(True)
                self.preview_loop_button.setEnabled(True)
                self.process_button.setEnabled(True)

            else:
                logging.debug("File selection was cancelled")

        except Exception as e:
            logging.error(f"An error occurred in select_file method: {e}")
            QMessageBox.critical(self, "Error", str(e))
        logging.debug("Exiting select_file method")

    def preview_audio(self):
        """Previews the audio clip based on the start point and end point. Gain adjustment is applied if specified
        Uses: pydub for processing audio and SimpleAudio for playing the preview
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
            if self.gain_adjust:
                self.preview_segment = self.preview_segment.apply_gain(self.gain_adjust.text())

            # Convert the pydub AudioSegment to numpy array
            self.preview_samples = np.array(self.preview_segment.get_array_of_samples())
            self.preview_samples = self.preview_samples.reshape((-1, self.preview_segment.channels))

            # Disable the 'Preview Audio' and 'Play' buttons while the audio is playing
            self.preview_button.setEnabled(False)
            self.preview_loop_button.setEnabled(False)
            self.play_button.setEnabled(False)

            # Enable the 'Stop Preview' button
            self.stop_preview_button.setEnabled(True)

            # Play the preview segment
            self.preview_obj = sa.play_buffer(self.preview_samples, self.preview_segment.channels,
                                              self.preview_segment.sample_width, self.preview_segment.frame_rate)

        except ValueError as e:
            QMessageBox.critical(self, "Invalid input", str(e))
            logging.error(f"Invalid input: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            logging.error(f"An error occurred: {e}")
        logging.debug("Exiting preview_audio method")

    def preview_loop_repeat(self):
        """Creates a section of audio of the last 5 seconds and first 5 seconds of the track to preview the transition
        Uses: pydub for processing audio and SimpleAudio for playing the preview
        Creates a thread for previewing the loop repeatedly
        """
        logging.debug("Entering preview_loop_repeat method")
        try:
            # Get the start position, end position, and calculate the clip length
            start_pos = float(self.start_pos.text())
            end_pos = float(self.end_position.text())
            clip_length = end_pos - start_pos

            # Make sure the clip length is over 10 seconds
            if clip_length > 90000 or clip_length <= 9999:
                raise ValueError("For this preview, clip length must be between 10,000 and 90,000 milliseconds.")

            # Create the preview segment
            self.preview_segment = self.audio[start_pos:end_pos]

            # Apply the gain adjustment if specified
            if self.gain_adjust:
                self.preview_segment = self.preview_segment.apply_gain(self.gain_adjust.text())

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
            logging.error(f"An error occurred: {e}")
        logging.debug("Exiting preview_loop_repeat method")

    def loop_preview(self):
        """Plays the loop on repeat until Stop Preview is pressed"""
        # Play the preview loop on repeat until the 'Stop Preview' button is pressed
        while self.previewing:
            # Play the preview segment
            self.preview_obj = sa.play_buffer(self.preview_samples, self.preview_segment.channels,
                                              self.preview_segment.sample_width, self.preview_segment.frame_rate)
            while self.preview_obj.is_playing():
                time.sleep(0.1)  # Sleep to prevent busy-waiting

    def stop_preview(self):
        """Stops the currently playing preview that is playing using SimpleAudio"""
        logging.debug("Entering stop_preview method")
        # Stop the preview playback
        self.previewing = False
        if self.preview_obj:
            self.preview_obj.stop()

        # Disable the 'Stop Preview' button
        self.stop_preview_button.setEnabled(False)

        # Re-enable the 'Preview Audio' and 'Play' buttons when the audio stops
        self.preview_button.setEnabled(True)
        self.preview_loop_button.setEnabled(True)
        self.play_button.setEnabled(True)
        logging.debug("Exiting stop_preview method")

    def process_audio(self):
        """Processes the audio clip based on the start and end point and applies gain if specified
        - SF2000 format: 16-bit signed little-endian, mono, 21560 Hz (to correct for playback speed issue)
        - WAV or MP3 format: Standard options, basic output
        Uses: pydub to process the audio and export the audio segment
        """
        logging.debug("Entering process_audio method")
        try:
            # Get the start position and length from the input fields
            start_pos = float(self.start_pos.text())
            end_pos = float(self.end_position.text())
            clip_length = end_pos - start_pos

            # Validate the start and end positions
            if end_pos <= start_pos:
                raise ValueError("End position must be greater than start position.")

            # Make sure the clip length is over 100 milliseconds
            if clip_length > 90000 or clip_length <= 99:
                raise ValueError("Clip length must be between 100 and 90,000 milliseconds.")

            # Get the selected segment of the audio
            self.clip_segment = self.audio[start_pos:end_pos]

            # Apply the gain adjustment if specified
            if self.gain_adjust:
                self.clip_segment = self.clip_segment.apply_gain(self.gain_adjust.text())

            # Create save dialog, allowing user to choose SF2000 pagefile.sys or standard .WAV file output
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_filter = "SF2000 pagefile.sys file (*.sys);;WAV file (*.wav);;MP3 file (*.mp3)"
            output_file, selected_filter = QFileDialog.getSaveFileName(self, "Save File", "",
                                                                       file_filter, options=options)

            # If the user specified a file to save,
            if output_file:
                # Save as SF2000 'pagefile.sys' format if specified
                if selected_filter == "SF2000 pagefile.sys file (*.sys)":
                    if not output_file.endswith('.sys'):
                        output_file += '.sys'
                    # Down-mix to mono
                    if self.clip_segment.channels > 1:
                        self.clip_segment = self.clip_segment.set_channels(1)
                    # Resample the audio to 21560 Hz for proper playback speed on the SF2000
                    self.clip_segment = self.clip_segment.set_frame_rate(21560)
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

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            logging.error(f"An error occurred: {e}")
        logging.debug("Exiting process_audio method")

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
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            logging.error(f"An error occurred: {e}")

    def mark_out(self):
        """Marks the 'End Position' when the audio is being previewed"""
        try:
            self.end_position.setText(str(self.current_position))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            logging.error(f"An error occurred: {e}")

    def play_audio(self):
        """Plays the loaded audio file to preview the audio and set the Start and End points
        Uses: pydub for processing audio and applying gain and SimpleAudio for playback
        """
        logging.debug("Entering play_audio method")
        if not self.playing:
            try:
                # Create a play segment from the loaded pydub audio segment
                self.play_segment = self.audio

                # Apply the gain adjustment if specified
                if self.gain_adjust:
                    self.play_segment = self.play_segment.apply_gain(self.gain_adjust.text())

                # Convert the pydub AudioSegment to numpy array
                self.play_samples = np.array(self.play_segment.get_array_of_samples())
                self.play_samples = self.play_samples.reshape((-1, self.play_segment.channels))

                # Reset position and start playing audio
                self.current_position = 0
                self.playing = True
                self.timer.start()

                # Play the preview segment using SimpleAudio
                self.play_obj = sa.play_buffer(self.play_samples, self.play_segment.channels,
                                               self.play_segment.sample_width, self.play_segment.frame_rate)

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
                QMessageBox.critical(self, "Error", str(e))
                logging.error(f"An error occurred: {e}")
            logging.debug("Exiting play_audio method")

    def stop_audio(self):
        logging.debug("Entering stop_audio method")
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
        self.play_obj.stop()
        self.timer.stop()
        logging.debug("Exiting stop_audio method")

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
            QMessageBox.critical(self, "Error", str(e))
            logging.error(f"An error occurred: {e}")

# Main entry point
app = QApplication(sys.argv)

# Check if the .ico file exists
icon_path = os.path.join(os.path.dirname(__file__), 'kerokero.ico')
if os.path.exists(icon_path):
    app.setWindowIcon(QIcon(icon_path))

# Run the AudioConvertApp class
ex = AudioConverterApp()

# Exit the application
sys.exit(app.exec_())

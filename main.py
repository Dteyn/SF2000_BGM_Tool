import logging
import numpy as np
import os
import pygame
import sys
import simpleaudio as sa
import threading
import time
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFrame, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtWidgets import QFileDialog, QLineEdit, QMessageBox, QHBoxLayout, QTextEdit
from pydub import AudioSegment

# Configure logging
logging.basicConfig(level=logging.DEBUG)


class AudioConverterApp(QWidget):
    def __init__(self):
        super().__init__()

        # Set the timer interval
        self.timer_interval = 10

        # Set up the UI
        self.init_ui()

    def init_ui(self):
        logging.debug("Entering init_ui method")
        self.layout = QVBoxLayout()

        # Label for the currently selected file
        self.file_label = QLabel('No file selected')
        self.layout.addWidget(self.file_label)

        self.select_button = QPushButton('Select File')
        self.select_button.clicked.connect(self.select_file)
        self.select_button.setFixedHeight(50)
        self.select_button.setToolTip("Select the audio file to process")
        self.layout.addWidget(self.select_button)

        # Create a read-only, fixed height QTextEdit to display the file information
        self.file_info_text_edit = QTextEdit(self)
        self.file_info_text_edit.setReadOnly(True)
        self.file_info_text_edit.setFixedHeight(80)
        self.layout.addWidget(self.file_info_text_edit)

        # Create a horizontal layout for the transport controls
        self.transport_layout = QHBoxLayout()

        # Create and add the 'Mark In' button to the transport layout
        self.mark_in_button = QPushButton('Mark In')
        self.mark_in_button.clicked.connect(self.mark_in)
        self.mark_in_button.setFixedHeight(40)
        self.mark_in_button.setEnabled(False)
        self.mark_in_button.setToolTip("Set the 'In' point of the audio clip")
        self.transport_layout.addWidget(self.mark_in_button)

        # Create and add the 'Play' button to the transport layout
        self.play_button = QPushButton('Play')
        self.play_button.clicked.connect(self.play_audio)
        self.play_button.setFixedHeight(40)
        self.play_button.setEnabled(False)
        self.play_button.setToolTip("Play the selected audio file")
        self.transport_layout.addWidget(self.play_button)

        # Create and add the 'Stop' button to the transport layout
        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_audio)
        self.stop_button.setFixedHeight(40)
        self.stop_button.setEnabled(False)
        self.stop_button.setToolTip("Stop playback")
        self.transport_layout.addWidget(self.stop_button)

        # Create and add the 'Mark Out' button to the transport layout
        self.mark_out_button = QPushButton('Mark Out')
        self.mark_out_button.clicked.connect(self.mark_out)
        self.mark_out_button.setFixedHeight(40)
        self.mark_out_button.setEnabled(False)
        self.mark_out_button.setToolTip("Set the 'Out' point of the audio clip")
        self.transport_layout.addWidget(self.mark_out_button)

        # Add the transport layout to the main layout
        self.layout.addLayout(self.transport_layout)

        self.current_position_label = QLabel('')
        self.layout.addWidget(self.current_position_label)

        self.clip_length_label = QLabel('')
        self.layout.addWidget(self.clip_length_label)

        self.start_pos_label = QLabel('Start Position (ms):')
        self.layout.addWidget(self.start_pos_label)

        self.start_pos = QLineEdit('0')
        self.start_pos.setToolTip("The start point of the audio clip")
        self.start_pos.textChanged.connect(self.update_clip_length)
        self.layout.addWidget(self.start_pos)

        self.end_position_label = QLabel('End Position (ms):')
        self.layout.addWidget(self.end_position_label)

        self.end_position = QLineEdit('90')
        self.end_position.textChanged.connect(self.update_clip_length)
        self.end_position.setToolTip("The end point of the audio clip")
        self.layout.addWidget(self.end_position)

        self.gain_label = QLabel('Gain Adjustment (dB):')
        self.layout.addWidget(self.gain_label)

        self.gain_adjust = QLineEdit('0')
        self.gain_adjust.setToolTip("Make the audio louder or quieter by adjusting the gain in dB (ex. +3 or -3)\n"
                                    "NOTE: The gain level does not affect the Playback (at top). It only applies to\n"
                                    "the Preview and Save buttons below")
        self.layout.addWidget(self.gain_adjust)

        self.preview_button = QPushButton('Preview Full Audio Clip')
        self.preview_button.clicked.connect(self.preview_audio)
        self.preview_button.setFixedHeight(50)
        self.preview_button.setEnabled(False)
        self.preview_button.setToolTip("Preview the entire audio clip from start to finish, then loop")
        self.layout.addWidget(self.preview_button)

        self.preview_loop_button = QPushButton('Preview Loop Transition')
        self.preview_loop_button.clicked.connect(self.preview_loop_repeat)
        self.preview_loop_button.setFixedHeight(50)
        self.preview_loop_button.setEnabled(False)
        self.preview_loop_button.setToolTip("Preview the repeat point in the looped audio clip")
        self.layout.addWidget(self.preview_loop_button)

        self.stop_preview_button = QPushButton('Stop Preview')
        self.stop_preview_button.clicked.connect(self.stop_preview)
        self.stop_preview_button.setFixedHeight(50)
        self.stop_preview_button.setEnabled(False)
        self.stop_preview_button.setToolTip("Stop playback of the preview")
        self.layout.addWidget(self.stop_preview_button)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(divider)

        self.process_button = QPushButton('Save Audio Clip')
        self.process_button.clicked.connect(self.process_audio)
        self.process_button.setFixedHeight(80)
        self.process_button.setEnabled(False)
        self.process_button.setToolTip("Process the audio and save the audio clip to file")
        self.layout.addWidget(self.process_button)

        self.setLayout(self.layout)
        self.setWindowTitle('SF2000 BGM Tool')
        self.show()

        self.setFixedSize(self.size())  # Lock the window size

        logging.debug("Exiting init_ui method")

    def select_file(self):
        logging.debug("Entering select_File method")
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

                # Initialize pygame mixer and load content
                pygame.mixer.init()
                pygame.mixer.music.load(self.audio_file)

                # Set up a timer to display the current position
                self.timer = QTimer()
                self.timer.timeout.connect(self.update_current_position)
                self.timer.setInterval(self.timer_interval)
                self.current_position = 0
                self.playing = False

                # Enable buttons
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

            # Pre-loop the preview segment twice to create a seamless loop
            self.preview_segment = self.preview_segment * 2

            # Apply the gain adjustment if specified
            if self.gain_adjust:
                self.preview_segment = self.preview_segment.apply_gain(self.gain_adjust.text())

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

            # Create a thread to handle the looping of the preview segment
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
        # Play the preview loop on repeat until the 'Stop Preview' button is pressed
        while self.previewing:
            # Play the preview segment
            self.preview_obj = sa.play_buffer(self.preview_samples, self.preview_segment.channels,
                                              self.preview_segment.sample_width, self.preview_segment.frame_rate)
            while self.preview_obj.is_playing():
                time.sleep(0.1)  # Sleep to prevent busy-waiting

    def stop_preview(self):
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

            if output_file:
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

                elif selected_filter == "WAV file (*.wav)":
                    if not output_file.endswith('.wav'):
                        output_file += '.wav'
                    # Export the audio in WAV format
                    self.clip_segment.export(output_file, format="wav")

                elif selected_filter == "MP3 file (*.mp3)":
                    if not output_file.endswith('.mp3'):
                        output_file += '.mp3'
                    # Export the audio in WAV format
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
        try:
            start_pos_text = self.start_pos.text()
            end_pos_text = self.end_position.text()

            if not start_pos_text or not end_pos_text:
                return

            start_pos = float(start_pos_text)
            end_pos = float(end_pos_text)
            clip_length = end_pos - start_pos

            minutes, seconds = divmod(clip_length / 1000, 60)
            clip_length_formatted = f"{int(minutes)}:{int(seconds):02d}"
            clip_length_display = int(clip_length)  # Convert to integer for display

            self.clip_length_label.setText(f'Clip Length: {clip_length_display} ms ({clip_length_formatted})')

        except ValueError as e:
            QMessageBox.critical(self, "Invalid input", str(e))
            logging.error(f"Invalid input: {e}")

    def mark_in(self):
        try:
            if self.current_position:
                self.start_pos.setText(str(self.current_position))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            logging.error(f"An error occurred: {e}")

    def mark_out(self):
        try:
            self.end_position.setText(str(self.current_position))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            logging.error(f"An error occurred: {e}")

    def play_audio(self):
        logging.debug("Entering play_audio method")
        if not self.playing:
            try:
                # Disable the 'Preview Audio' and 'Play' buttons while the audio is playing
                self.preview_button.setEnabled(False)
                self.preview_loop_button.setEnabled(False)
                self.play_button.setEnabled(False)

                # Enable the 'Mark In', 'Mark Out', and 'Stop' buttons
                self.mark_in_button.setEnabled(True)
                self.mark_out_button.setEnabled(True)
                self.stop_button.setEnabled(True)

                # Reset position and start playing audio
                self.current_position = 0
                self.playing = True
                pygame.mixer.music.play(start=0)
                self.timer.start()

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
        pygame.mixer.music.stop()
        self.timer.stop()
        logging.debug("Exiting stop_audio method")

    def update_current_position(self):
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
                    self.timer.stop()
                    self.playing = False
                    logging.info("End of audio reached, stopping playback")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            logging.error(f"An error occurred: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Check if the .ico file exists
    icon_path = os.path.join(os.path.dirname(__file__), 'kerokero.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    ex = AudioConverterApp()
    sys.exit(app.exec_())

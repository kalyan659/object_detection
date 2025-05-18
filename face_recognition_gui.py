

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import face_recognition
from datetime import datetime, date, timedelta
import csv
from collections import defaultdict
import time
import threading


# Define the path to the directory containing the training images.
path = 'Training_images'
# Initialize an empty list to store the training images.
images = []
# Initialize an empty list to store the names of the people in the training images.
classNames = []
# Get a list of all files and directories in the specified path.
myList = os.listdir(path)
# Print the list of files and directories found in the training images path.
print(myList)
# Iterate through each item (file or directory) in the myList.
for cl in myList:
    # Construct the full path to the current image file.
    curImg = cv2.imread(f'{path}/{cl}')
    # Append the current image to the images list.
    images.append(curImg)
    # Extract the name of the person from the filename (removing the extension) and append it to the classNames list.
    classNames.append(os.path.splitext(cl)[0])
# Print the list of extracted class names.
print(classNames)

# Define a function to find the face encodings for all the images in the provided list.
def findEncodings(images):
    # Initialize an empty list to store the face encodings.
    encodeList = []
    # Iterate through each image in the input list of images.
    for img in images:
        # Convert the image from BGR (OpenCV's default) to RGB.
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Find all face encodings in the current image.
        encode = face_recognition.face_encodings(img)
        # Check if any face encodings were found in the image.
        if encode:
            # Append the first face encoding found in the image to the encodeList.
            encodeList.append(encode[0])
        # If no face encoding was found in the image, print a warning.
        else:
            print(f"Warning: No face detected in {os.path.join(path, cl)}")
    # Return the list of face encodings.
    return encodeList

# Call the findEncodings function to get the encodings of the known faces from the training images.
encodeListKnown = findEncodings(images)
# Print a message indicating that the encoding process is complete.
print('Encoding Complete')
# --- End of Your Existing Face Recognition Code ---

# Initialize a defaultdict to store the daily attendance records. The keys are names, and the values are dictionaries of dates and entry/exit times.
daily_attendance = defaultdict(dict)
# Initialize a set to keep track of the faces currently recognized in the frame to avoid multiple attendance markings.
recognized_faces_in_frame = set()

# Define a function to mark the attendance of a recognized person.
def markAttendance(name):
    # Get the current date and time.
    now = datetime.now()
    # Extract the current date.
    current_date = now.date()
    # Format the current time as HH:MM:SS.
    current_time = now.strftime('%H:%M:%S')

    # Check if the name is already a key in the daily_attendance dictionary.
    if name not in daily_attendance:
        # If the name is not present, create a new entry for that person.
        daily_attendance[name] = {}

    # Check if the current date is already a key within the inner dictionary for the given name.
    if current_date not in daily_attendance[name]:
        # If the date is not present, it's the first entry for this person on this day, so record the entry time.
        daily_attendance[name][current_date] = {'entry': current_time, 'exit': None}
    # If the date is already present, it's a subsequent entry on the same day, so update the exit time.
    else:
        daily_attendance[name][current_date]['exit'] = current_time

# Define a function to calculate the working hours between an entry and an exit time.
def calculate_working_hours(entry_time_str, exit_time_str):
    # Check if both entry and exit time strings are provided.
    if entry_time_str and exit_time_str:
        try:
            # Convert the entry time string to a datetime object.
            entry_time = datetime.strptime(entry_time_str, '%H:%M:%S')
            # Convert the exit time string to a datetime object.
            exit_time = datetime.strptime(exit_time_str, '%H:%M:%S')
            # Calculate the difference between exit and entry time to get the working duration.
            working_duration = exit_time - entry_time
            # Return the calculated working duration.
            return working_duration
        # Handle potential ValueError if the time strings are not in the correct format.
        except ValueError:
            return None
    # If either entry or exit time is missing, return None.
    return None

# Define a function to determine the attendance status (Present, Half Day, Absent) based on the working duration.
def get_status(working_duration):
    # Check if a working duration was calculated.
    if working_duration:
        # Define timedelta objects for 8 hours and 4 hours for comparison.
        eight_hours = timedelta(hours=8)
        four_hours = timedelta(hours=4)
        # If the working duration is greater than 8 hours, the status is Present ('P').
        if working_duration > eight_hours:
            return 'P'
        # If the working duration is greater than 4 hours and less than or equal to 8 hours, the status is Half Day ('HD').
        elif four_hours < working_duration <= eight_hours:
            return 'HD'
        # If the working duration is less than or equal to 4 hours, the status is Absent ('A').
        else:
            return 'A'
    # If no working duration was calculated (e.g., only entry time), the status is Absent ('A').
    return 'A'

# # Define a function to generate the daily attendance report in a CSV file.
# def generateDailyAttendanceReport(filename='DailyAttendanceReport.csv'):
#     # Open the specified CSV file in write mode ('w') with newline='' to prevent extra blank rows.
#     with open(filename, 'w+', newline='') as csvfile:
#         # Create a CSV writer object.
#         csv_writer = csv.writer(csvfile)
#         # Write the header row to the CSV file if it is empty
#         #if os.path.getsize(filename) == 0:
#         csv_writer.writerow(['Name', 'Date', 'Entry Time', 'Exit Time', 'Working Hours', 'Status'])
#         # Iterate through each person and their daily attendance records.
#         for name, daily_records in daily_attendance.items():
#             # Iterate through each date record for the current person.
#             for date_record, times in daily_records.items():
#                 # Get the entry time for the current date.
#                 entry_time = times.get('entry')
#                 # Get the exit time for the current date.
#                 exit_time = times.get('exit')
#                 # Calculate the working hours for the current date.
#                 working_duration = calculate_working_hours(entry_time, exit_time)
#                 # Convert the working duration to a string if it's not None.
#                 working_hours_str = str(working_duration) if working_duration else None
#                 # Get the attendance status based on the working duration.
#                 status = get_status(working_duration)
#                 # Write a row to the CSV file with the person's name, date, entry time, exit time, working hours, and status.
#                 csv_writer.writerow([name, date_record.isoformat(), entry_time, exit_time, working_hours_str, status])
#     # Print a message indicating that the report has been generated successfully.
#     print(f"Daily attendance report with working hours and status generated successfully in '{filename}'")
#     # Return the filename of the generated report.
#     return filename

def generateDailyAttendanceReport(filename='DailyAttendanceReport.csv'):
    records = []  # To store all non-empty rows
    file_exists = os.path.exists(filename)

    # Step 1: Load existing valid records
    if file_exists:
        with open(filename, 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            headers = next(csv_reader, None)
            if headers:
                records.append(headers)
                for row in csv_reader:
                    # Only keep rows that are not empty
                    if any(cell.strip() for cell in row):  # Check for at least one non-empty cell
                        records.append(row)
    else:
        headers = ['Name', 'Date', 'Entry Time', 'Exit Time', 'Working Hours', 'Status']
        records.append(headers)

    # Step 2: Update or insert today's records
    for name, daily_records in daily_attendance.items():
        for date_record, times in daily_records.items():
            date_str = date_record.strftime('%d-%m-%Y')  # Adjusted to match your output format
            entry_time = times.get('entry')
            exit_time = times.get('exit')
            working_duration = calculate_working_hours(entry_time, exit_time)
            working_hours_str = str(working_duration) if working_duration else ''
            status = get_status(working_duration)

            found = False
            for i in range(1, len(records)):
                if len(records[i]) < 6:
                    continue
                if records[i][0] == name and records[i][1] == date_str:
                    # Update existing row
                    records[i][3] = exit_time
                    records[i][4] = working_hours_str
                    records[i][5] = status
                    found = True
                    break

            if not found:
                records.append([name, date_str, entry_time, exit_time, working_hours_str, status])

    # Step 3: Write clean records back to the CSV
    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(records)

    print(f"Daily attendance report updated successfully in '{filename}' with clean rows.")
    return filename


# Define the main application class for the face recognition attendance system.
class FaceAttendanceApp:
    # Initialize the application.
    def __init__(self, window, window_title):
        # Set the main window.
        self.window = window
        # Set the title of the main window.
        self.window.title(window_title)

        # Set the window to fullscreen mode.
        self.window.attributes('-fullscreen', True)

        # Open the default webcam (camera index 0).
        self.cap = cv2.VideoCapture(0)
        # Check if the webcam was opened successfully.
        if not self.cap.isOpened():
            # If the webcam could not be opened, raise a ValueError.
            raise ValueError("Unable to open webcam")

        # Get the width of the screen.
        self.screen_width = self.window.winfo_screenwidth()
        # Get the height of the screen.
        self.screen_height = self.window.winfo_screenheight()

        # Calculate the desired width for the camera feed canvas (60% of screen width).
        self.camera_width = int(self.screen_width * 0.4)
        # Calculate the desired height for the camera feed canvas (80% of screen height).
        self.camera_height = int(self.screen_height * 0.5)
        # Create a Tkinter Canvas widget to display the camera feed.
        self.canvas = tk.Canvas(window, width=self.camera_width, height=self.camera_height)
        # Pack the canvas to the left side of the window with padding.
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # Create a frame to hold the controls (attendance label, report frame, close button).
        self.controls_frame = ttk.Frame(window)
        # Pack the controls frame to the right side of the window, filling vertically.
        self.controls_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        # Create a label to display the name of the recognized person.
        self.attendance_label = tk.Label(self.controls_frame, text="Recognized Person: None", font=("Arial", 16))
        # Pack the attendance label with vertical padding.
        self.attendance_label.pack(pady=10)

        # Create a labeled frame to contain the attendance report.
        self.report_frame = ttk.LabelFrame(self.controls_frame, text="Attendance Report")
        # Pack the report frame, filling both horizontally and vertically, and expanding to take available space.
        self.report_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Create a Treeview widget to display the report in a tabular format.
        self.report_tree = ttk.Treeview(self.report_frame, columns=('Name', 'Date', 'Entry Time', 'Exit Time', 'Working Hours', 'Status'), show='headings')
        # Set the heading text for the 'Name' column.
        self.report_tree.heading('Name', text='Name')
        # Set the heading text for the 'Date' column.
        self.report_tree.heading('Date', text='Date')
        # Set the heading text for the 'Entry Time' column.
        self.report_tree.heading('Entry Time', text='Entry Time')
        # Set the heading text for the 'Exit Time' column.
        self.report_tree.heading('Exit Time', text='Exit Time')
        # Set the heading text for the 'Working Hours' column.
        self.report_tree.heading('Working Hours', text='Working Hours')
        # Set the heading text for the 'Status' column.
        self.report_tree.heading('Status', text='Status')
        # Configure column widths and alignment (adjust these values as needed).
        self.report_tree.column('Name', anchor=tk.W, width=120)
        self.report_tree.column('Date', anchor=tk.W, width=100)
        self.report_tree.column('Entry Time', anchor=tk.CENTER, width=100)
        self.report_tree.column('Exit Time', anchor=tk.CENTER, width=100)
        self.report_tree.column('Working Hours', anchor=tk.CENTER, width=120)
        self.report_tree.column('Status', anchor=tk.CENTER, width=80)
        # Pack the treeview, filling both horizontally and vertically, and expanding to take available space.
        self.report_tree.pack(fill=tk.BOTH, expand=True)

        # Create a button to manually generate the attendance report.
        self.generate_report_button = ttk.Button(self.report_frame, text="Generate Report", command=self.generate_and_display_report)
        # Pack the generate report button with vertical padding.
        self.generate_report_button.pack(pady=5)

        # Create a button to close the application.
        self.close_button = ttk.Button(self.controls_frame, text="Close", command=self.on_closing)
        # Pack the close button with vertical padding.
        self.close_button.pack(pady=10)

        # Flag to control whether to process frames from the webcam.
        self.process_frame_flag = True
        # Store the last time a report was generated.
        self.last_report_time = time.time()
        # Set the interval for automatic report generation (1 hour in seconds).
        self.report_interval = 3600

        # Start the webcam update loop.
        self.update()
        # Create a thread for automatically generating the report in the background.
        self.auto_report_thread = threading.Thread(target=self.auto_generate_report)
        # Set the thread as a daemon so it will exit when the main program exits.
        self.auto_report_thread.daemon = True
        # Start the automatic report generation thread.
        self.auto_report_thread.start()

        # Set the protocol for handling the window closing event (when the user clicks the close button).
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Start the Tkinter event loop to display the GUI and handle events.
        self.window.mainloop()

    # Define a function to continuously update the webcam feed and perform face recognition.
    def update(self):
        # Check if the frame processing flag is set to True.
        if not self.process_frame_flag:
            # If the flag is False, wait for 15 milliseconds and then call update again.
            self.window.after(15, self.update)
            return

        # Read a frame from the webcam.
        success, frame = self.cap.read()
        # If a frame was successfully read.
        if success:
            # Resize the frame to the desired camera feed display size.
            frame_resized = cv2.resize(frame, (self.camera_width, self.camera_height))
            # Resize the frame to 1/4 of its original size for faster face recognition processing.
            imgS = cv2.resize(frame_resized, (0, 0), None, 0.25, 0.25)
            # Convert the small frame from BGR to RGB.
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            
            # Find all face locations in the small frame.
            facesCurFrame = face_recognition.face_locations(imgS)
            # Find the face encodings for the faces detected in the small frame.
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            # Initialize an empty set to store the names of the faces recognized in the current frame.
            current_recognized_faces = set()

            # Iterate through each face encoding and its corresponding location in the current frame.
            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                # Scale coordinates back to full frame
                y1, x2, y2, x1 = faceLoc
                scale_y = self.camera_height / imgS.shape[0]
                scale_x = self.camera_width / imgS.shape[1]
                y1, x2, y2, x1 = int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y), int(x1 * scale_x)
                # # Add padding and find face only
                # PADDING = 100
                # x1_pad = max(x1 - PADDING, 0)
                # y1_pad = max(y1 - PADDING, 0)
                # x2_pad = min(x2 + PADDING, self.camera_width)
                # y2_pad = min(y2 + PADDING, self.camera_height)

                # # Crop the frame to show only the face with padding
                # face_crop = frame_resized[y1_pad:y2_pad, x1_pad:x2_pad]

                # # Convert to RGB for Tkinter display
                # face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
                # img_face_only = Image.fromarray(face_rgb)
                # Compare the current face encoding with the encodings of the known faces.
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                # Calculate the distance between the current face encoding and the known face encodings.
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                # Find the index of the known face with the smallest distance (best match).
                matchIndex = np.argmin(faceDis)

                # If there is a match (the face distance is below the tolerance threshold - default is usually 0.6).
                if matches[matchIndex]:
                    # Get the name of the recognized person from the classNames list.
                    name = classNames[matchIndex]
                    # Add the recognized name to the set of currently recognized faces.
                    current_recognized_faces.add(name)
                    # Get the coordinates of the face location in the small frame.
                    y1, x2, y2, x1 = faceLoc
                    # Scale the face location coordinates back to the size of the resized camera feed frame.
                    y1, x2, y2, x1 = int(y1 * (self.camera_height / imgS.shape[0])), \
                                        int(x2 * (self.camera_width / imgS.shape[1])), \
                                        int(y2 * (self.camera_height / imgS.shape[0])), \
                                        int(x1 * (self.camera_width / imgS.shape[1]))
                    # Draw a green rectangle around the detected face in the resized frame.
                    cv2.rectangle(frame_resized, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    # Draw a filled green rectangle at the bottom of the detected face for the name background.
                    cv2.rectangle(frame_resized, (x1, y2 - 35), (x2, y2), (0, 255, 110), cv2.FILLED)
                    # Put the name of the recognized person on the frame.
                    cv2.putText(frame_resized, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 2)
                    # Call the markAttendance function to record the attendance of the recognized person.
                    markAttendance(name)

            # If any faces were recognized in the current frame.
            if current_recognized_faces:
                # Join the set of recognized names into a comma-separated string.
                recognized_name_str = ", ".join(current_recognized_faces)
                # Update the attendance label to display the recognized person(s).
                self.attendance_label.config(text=f"Recognized Person(s): {recognized_name_str}")
            # If no faces were recognized in the current frame.
            else:
                # Update the attendance label to indicate that no person was recognized.
                self.attendance_label.config(text="Recognized Person: None")
            
            
            # Convert the resized frame from BGR to RGB for PIL Image.    
            img = Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB))
            # Create a PhotoImage object from the PIL Image to display in Tkinter.
            if 'img_face_only' in locals():
                self.photo = ImageTk.PhotoImage(image=img_face_only)
            else:
                self.photo = ImageTk.PhotoImage(image=img)
            # Update the image displayed on the canvas.
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        # Schedule the update function to be called again after 15 milliseconds to create a continuous video feed.
        self.window.after(15, self.update)
    # def update(self):
    #     # Check if the frame processing flag is set to True.
    #     if not self.process_frame_flag:
    #         # If the flag is False, wait for 15 milliseconds and then call update again.
    #         self.window.after(15, self.update)
    #         return

    #     # Read a frame from the webcam.
    #     success, frame = self.cap.read()
    #     # If a frame was successfully read.
    #     if success:
    #         # Resize the frame to the desired camera feed display size.
    #         frame_resized = cv2.resize(frame, (self.camera_width, self.camera_height))
    #         # Resize the frame to 1/4 of its original size for faster face recognition processing.
    #         imgS = cv2.resize(frame_resized, (0, 0), None, 0.25, 0.25)
    #         # Convert the small frame from BGR to RGB.
    #         imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    #         # Find all face locations in the small frame.
    #         facesCurFrame = face_recognition.face_locations(imgS)
    #         # Find the face encodings for the faces detected in the small frame.
    #         encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    #         # If faces are detected
    #         if facesCurFrame:
    #             # Only process the first face found
    #             encodeFace = encodesCurFrame[0]
    #             faceLoc = facesCurFrame[0]

    #             # Compare the current face encoding with the encodings of the known faces.
    #             matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
    #             faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
    #             matchIndex = np.argmin(faceDis) if faceDis.size > 0 else -1

    #             # If match found
    #             if matchIndex != -1 and matches[matchIndex]:
    #                 name = classNames[matchIndex]
    #                 markAttendance(name)
    #             else:
    #                 name = "Unknown"

    #             # Scale coordinates back to full frame
    #             y1, x2, y2, x1 = faceLoc
    #             scale_y = self.camera_height / imgS.shape[0]
    #             scale_x = self.camera_width / imgS.shape[1]
    #             y1, x2, y2, x1 = int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y), int(x1 * scale_x)

    #             # Add padding
    #             PADDING = 100
    #             x1_pad = max(x1 - PADDING, 0)
    #             y1_pad = max(y1 - PADDING, 0)
    #             x2_pad = min(x2 + PADDING, self.camera_width)
    #             y2_pad = min(y2 + PADDING, self.camera_height)

    #             # Crop the frame to show only the face with padding
    #             face_crop = frame_resized[y1_pad:y2_pad, x1_pad:x2_pad]

    #             # Convert to RGB for Tkinter display
    #             face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
    #             img = Image.fromarray(face_rgb)
    #         else:
    #             # No face found – show a black image with message
    #             blank_img = np.zeros((300, 300, 3), dtype=np.uint8)
    #             cv2.putText(blank_img, "No face detected", (30, 150),
    #                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    #             img = Image.fromarray(cv2.cvtColor(blank_img, cv2.COLOR_BGR2RGB))

    #         # Display the cropped or blank image
    #         imgtk = ImageTk.PhotoImage(image=img)
    #         self.camera_label.imgtk = imgtk
    #         self.camera_label.configure(image=imgtk)

    #     # Schedule next update
    #     self.window.after(15, self.update)

    # Define a function that runs in a separate thread to automatically generate the attendance report at a set interval.
    def auto_generate_report(self):
        # Continue the loop as long as the frame processing flag is True (i.e., the application is running).
        while self.process_frame_flag:
            # Check if the time elapsed since the last report generation is greater than or equal to the report interval.
            if time.time() - self.last_report_time >= self.report_interval:
                # If the interval has passed, call the function to generate the report and display it.
                self.generate_and_display_report()
                # Update the last report time to the current time.
                self.last_report_time = time.time()
            # Pause the loop for 60 seconds (1 minute) before checking again.
            time.sleep(60)

    # Define a function to generate the daily attendance report and display it in the table.
    def generate_and_display_report(self):
        # Call the function to generate the daily attendance report CSV file and get the filename.
        filename = generateDailyAttendanceReport()
        # Call the function to display the data from the generated CSV file in the Treeview table.
        self.display_report_table(filename) # Call the new display function

    # Define a function to display the attendance report data from a CSV file in the Treeview table.
    def display_report_table(self, filename):
        try:
            # Open the specified CSV file in read mode ('r') with newline='' to handle different line endings.
            with open(filename, 'r', newline='') as csvfile:
                # Create a CSV DictReader object to read the CSV file as dictionaries (with headers as keys).
                reader = csv.DictReader(csvfile)
                # Clear any existing data in the Treeview table.
                for item in self.report_tree.get_children():
                    self.report_tree.delete(item)
                # Configure the width and alignment of each column in the Treeview.
                self.report_tree.column('Name', anchor=tk.W, width=120) # 'W' for West (left) alignment
                self.report_tree.column('Date', anchor=tk.W, width=100) # 'W' for West (left) alignment
                self.report_tree.column('Entry Time', anchor=tk.CENTER, width=100) # 'CENTER' for center alignment
                self.report_tree.column('Exit Time', anchor=tk.CENTER, width=100) # 'CENTER' for center alignment
                self.report_tree.column('Working Hours', anchor=tk.CENTER, width=120) # 'CENTER' for center alignment
                self.report_tree.column('Status', anchor=tk.CENTER, width=80) # 'CENTER' for center alignment
                # Iterate through each row in the CSV file (as a dictionary).
                for row in reader:
                    # Insert a new row into the Treeview with the values from the current CSV row, ordered according to the column headings.
                    self.report_tree.insert('', tk.END, values=(row['Name'], row['Date'], row['Entry Time'], row['Exit Time'], row['Working Hours'], row['Status']))
        # Handle the case where the report file is not found.
        except FileNotFoundError:
            # Display an error message box to the user indicating that the report file was not found.
            messagebox.showerror("Error", f"Report file '{filename}' not found.")

    # Define a function to handle the closing of the application window.
    def on_closing(self):
        # Set the frame processing flag to False to stop the webcam feed and face recognition.
        self.process_frame_flag = False
        # Release the webcam.
        self.cap.release()
        # Destroy the main Tkinter window, closing the application.
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceAttendanceApp(root, "Face Recognition Attendance System")

# 👤 Face Recognition Attendance System (GUI Based)

A Python-based GUI application that uses real-time face recognition to automate employee attendance logging. It detects faces via webcam, ensures liveness with blink detection, and updates an ongoing daily attendance report.

---

## 📌 Features

- 🧠 Real-time face detection and recognition using `face_recognition` and `OpenCV`
- 👁️ Blink detection to verify a live person (anti-photo spoofing)
- 📂 Persistent logging of attendance (entry & exit) to `DailyAttendanceReport.csv`
- 🗃 Read employee details from `employee_details.csv`
- 🧮 Calculates working hours and attendance status
- 🖼️ GUI interface built with Tkinter

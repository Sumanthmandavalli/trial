# detect.py
from ultralytics import YOLO
import cv2
import smtplib
from email.message import EmailMessage
import vonage
import threading

# Load the YOLO model
model = YOLO("best.pt")

# Function to send an email alert
def email_alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject

    user = "sumanth.m@infyzterminals.com"
    msg['from'] = user
    password = "hkqr nsaz gqdh fjcj"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()
    print("Email sent successfully!")

# Function to send an SMS alert
def send_sms_alert(body, phone_number):
    client = vonage.Client(key="ae47b9f2", secret="Bt4D94EDjxgX2mso")
    sms = vonage.Sms(client)

    responseData = sms.send_message(
        {
            "from": "yard",
            "to": phone_number,
            "text": body
        }
    )

    if responseData["messages"][0]["status"] == "0":
        print("SMS sent successfully.")
    else:
        print(f"SMS failed with error: {responseData['messages'][0]['error-text']}")

# Function to perform detection and send alerts
def detect_and_alert():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.track(frame, save=False, show=False, classes=[0, 1, 2, 3, 4, 5, 7], conf=0.7)

        # Initialize detection counters
        person_count = 0
        mask_count = 0
        hardhat_count = 0
        safety_vest_count = 0

        # Accessing the boxes attribute to get detected objects
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    label = result.names[int(box.cls)]
                    if label == "Person":
                        person_count += 1
                    elif label == "Mask":
                        mask_count += 1
                    elif label == "Hardhat":
                        hardhat_count += 1
                    elif label == "Safety Vest":
                        safety_vest_count += 1

        # Calculate the number of unsafe persons
        unsafe_person_count = person_count - min(mask_count, hardhat_count, safety_vest_count)

        # Display counts on the frame
        annotated_frame = results[0].plot()
        cv2.putText(annotated_frame, f'Persons: {person_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(annotated_frame, f'Unsafe Persons: {unsafe_person_count}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.putText(annotated_frame, f'Mask: {mask_count}', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 255), 2)
        cv2.putText(annotated_frame, f'Hardhat: {hardhat_count}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 255), 2)
        cv2.putText(annotated_frame, f'Safety Vest: {safety_vest_count}', (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 255), 2)

        if unsafe_person_count > 0:
            threading.Thread(target=email_alert, args=("PPE Alert", "A person without PPE has been detected.", "sumanth.m@infyzterminals.com")).start()
            phone_number = "918367531279"
            threading.Thread(target=send_sms_alert, args=("PPE Alert: A person without PPE has been detected.", phone_number)).start()

        # Convert frame to JPEG format
        ret, jpeg = cv2.imencode('.jpg', annotated_frame)
        frame = jpeg.tobytes()
        
        # Yield the frame for streaming
        yield frame

    cap.release()
    cv2.destroyAllWindows()

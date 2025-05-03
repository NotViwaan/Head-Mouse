import cv2
import mediapipe as mp
import pyautogui
import pyttsx3
import numpy as np
import time

class HeadControlledMouse:
    def __init__(self):
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Camera setup
        self.cam = cv2.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        
        # Control parameters
        self.movement_scale = 1.5  # Sensitivity adjustment
        self.smoothing_factor = 0.3  # Higher value = smoother but slower response
        self.dead_zone_threshold = 0.01  # Ignore small movements
        self.calibration_frames = 30  # Frames to average for neutral position
        
        # State variables
        self.neutral_position = None
        self.calibration_samples = []
        self.prev_x, self.prev_y = pyautogui.position()
        self.calibrated = False
        self.last_click_time = 0
        self.click_cooldown = 0.5  # Seconds between clicks
        
    def calibrate(self, frame_count=30):
        """Calibrate neutral head position by averaging first few frames"""
        self.say("Calibrating. Please hold your head in neutral position.")
        samples = []
        
        for _ in range(frame_count):
            _, frame = self.cam.read()
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            output = self.face_mesh.process(rgb_frame)
            
            if output.multi_face_landmarks:
                landmarks = output.multi_face_landmarks[0].landmark
                nose = landmarks[4]  # Nose tip
                samples.append((nose.x, nose.y))
            
            # Show countdown
            cv2.putText(frame, f"Calibrating: {frame_count - len(samples)} frames left", 
                       (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Calibration', frame)
            cv2.waitKey(1)
        
        if samples:
            self.neutral_position = np.mean(samples, axis=0)
            self.calibrated = True
            self.say("Calibration complete. You may now move your head.")
        else:
            self.say("Calibration failed. Please ensure face is visible.")
        
        cv2.destroyWindow('Calibration')
    
    def say(self, text):
        """Text-to-speech output"""
        self.engine.say(text)
        self.engine.runAndWait()
    
    def process_frame(self, frame):
        """Process each camera frame for head tracking"""
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = self.face_mesh.process(rgb_frame)
        landmark_points = output.multi_face_landmarks
        frame_h, frame_w, _ = frame.shape
        
        if landmark_points:
            landmarks = landmark_points[0].landmark
            nose = landmarks[4]  # Nose tip
            
            if not self.calibrated:
                return frame
            
            # Calculate head movement from neutral position
            head_x = nose.x - self.neutral_position[0]
            head_y = nose.y - self.neutral_position[1]
            
            # Apply dead zone
            if abs(head_x) < self.dead_zone_threshold: head_x = 0
            if abs(head_y) < self.dead_zone_threshold: head_y = 0
            
            # Calculate new cursor position with scaling
            new_x = self.prev_x + (head_x * self.screen_w * self.movement_scale)
            new_y = self.prev_y + (head_y * self.screen_h * self.movement_scale)
            
            # Apply smoothing and boundary checking
            smooth_x = max(0, min(self.screen_w, 
                          self.prev_x * (1 - self.smoothing_factor) + new_x * self.smoothing_factor))
            smooth_y = max(0, min(self.screen_h, 
                          self.prev_y * (1 - self.smoothing_factor) + new_y * self.smoothing_factor))
            
            # Move cursor
            pyautogui.moveTo(smooth_x, smooth_y)
            self.prev_x, self.prev_y = smooth_x, smooth_y
            
            # Visual feedback
            cv2.putText(frame, f"X: {head_x:.3f}", (20, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Y: {head_y:.3f}", (20, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Click detection (eye blink)
            left_eye = [landmarks[145], landmarks[159]]
            for landmark in left_eye:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 2, (0, 255, 255), -1)
            
            if (left_eye[0].y - left_eye[1].y) < 0.008:
                current_time = time.time()
                if current_time - self.last_click_time > self.click_cooldown:
                    pyautogui.click()
                    cv2.putText(frame, "CLICK", (frame_w//2-50, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    self.last_click_time = current_time
        
        return frame
    
    def run(self):
        """Main program loop"""
        self.say("Head movement mouse starting")
        self.calibrate(self.calibration_frames)
        
        while True:
            ret, frame = self.cam.read()
            if not ret:
                break
            
            processed_frame = self.process_frame(frame)
            cv2.imshow('Head Movement Mouse', processed_frame)
            
            if cv2.waitKey(1) & 0xFF == 27:  # ESC key
                break
        
        self.cam.release()
        cv2.destroyAllWindows()
        self.say("Head mouse control ended")

if __name__ == "__main__":
    mouse = HeadControlledMouse()
    mouse.run()
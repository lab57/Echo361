import cv2
import os
import csv
import time
from skimage.metrics import structural_similarity as ssim
import numpy as np

def video_into_slides(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)


    target_fps = 5
    frame_skip = int(fps / target_fps)

    slide_change_threshold = 1000000  
    slides = []

    ret, prev_frame = cap.read()  
    if not ret:
        print("Error: Could not read the first frame.")
        cap.release()
        exit()

    timestamp = 0 
    slides.append((0.000,prev_frame))

    prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    frame_index  = 0 

    while cap.isOpened():
        for _ in range(frame_skip - 1): 
            ret = cap.grab() 
            if not ret:
                break
        
        ret, curr_frame = cap.read()
        if not ret:
            break

        curr_frame_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        frame_diff = cv2.absdiff(curr_frame_gray, prev_frame)
        
        diff_sum = frame_diff.sum()

        if diff_sum > slide_change_threshold:
            timestamp = (frame_index * frame_skip) / fps
            slides.append((round(timestamp, 3),curr_frame))    

            
        prev_frame = curr_frame_gray
        frame_index += 1

    cap.release()
    cv2.destroyAllWindows()
    return slides


def are_images_similar(img1, img2, threshold=0.95):
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    score, _ = ssim(img1_gray, img2_gray, full=True)
    return score > threshold

def filter_similar_slides(slides, threshold=0.95, time_threshold=1.0):
    grouped_slides = [] 
    current_group = []   
    prev_slide = None

    # Step 1: Group similar slides together.
    for timestamp, slide in slides:
        if prev_slide is None:
            current_group.append((timestamp, slide))
        else:
            if are_images_similar(prev_slide, slide, threshold):
                current_group.append((timestamp, slide))
            else:
                grouped_slides.append(current_group)
                current_group = [(timestamp, slide)]
        
        prev_slide = slide

    if current_group:
        grouped_slides.append(current_group)

    # Step 2: Take the last slide from each group.
    filtered_slides = [group[-1] for group in grouped_slides]

    # Step 3: Remove slides that are displayed for less than time_threshold.
    final_slides = []
    for i in range(len(filtered_slides) - 1):
        current_timestamp, current_slide = filtered_slides[i]
        next_timestamp, _ = filtered_slides[i + 1]

        time_displayed = next_timestamp - current_timestamp

        if time_displayed >= time_threshold:
            final_slides.append((current_timestamp, current_slide))

    # Always add the last slide since there's no next slide to compare its time duration.
    final_slides.append(filtered_slides[-1])

    return final_slides


def save_slides(slides, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamps = []
    
    csv_filename = "slide_timestamps.csv"
    csv_file_path = os.path.join(output_dir, csv_filename)
        
    for timestamp, slide in slides:
        timestamps.append(timestamp)
        slide_filename = f"{output_dir}/slide_{timestamp:.3f}s.png"
        cv2.imwrite(slide_filename, slide)
        
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        writer.writerow(["Timestamp (seconds)"])
        
        for timestamp in timestamps:
            writer.writerow([timestamp])
 
if __name__ == "__main__":
    start = time.time()
    # video_path = "Hackathon Test Recording.mp4"
    # output_path = "SimpleTestOutput"
    video_path = "HackathonAnimationTest.mp4"
    output_path = "AnimationOutput"
    inital_slides = video_into_slides(video_path)
    save_slides(inital_slides, output_path)
    
    filtered_output_path = "FilteredAnimationOutput"
    filtered_slides = filter_similar_slides(inital_slides)
    save_slides(filtered_slides,filtered_output_path)
    
    end = time.time()
    print(end-start)
    
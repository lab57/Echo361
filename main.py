import process_video
import create_pdf
import os


def recording_to_docs(video_path):

    # Step 1: Split recording into audio and video
    
    # Step 2: Get slides and timestamps from video
    slides = process_video.video_into_filtered_sides(video_path)
    timestamps = [s[0] for s in slides]
    
    # Step 3: Save the images to a file path
    output_dir = "output"
    process_video.save_slides(slides, output_dir)
    
    # Step 4: Get transcript of each timestamp from timestamps and audio, generate a transcript of the whole meeting
    
    # Step 5: Get summary of each transcript part
    
    # Step 6: Organize data for pdf generation
    data = []
    for timestamp, slide in slides:
        slide_filename = f"{output_dir}/slide-{timestamp:.3f}s.png"
        summary = f"This is the summary for slide-{timestamp:.3f}s."
        data.append((timestamp, slide_filename, summary))
        
    # Step 7: Generate pdf from slides and summaries
    title = "Insert Title"
    author = "Insert Author"
    document_setup_data = (title, author)

    typst_path = "report.typ"
    output_path = "report.pdf"
       
    create_pdf.generate_typst_document(data, typst_path, document_setup_data)
    create_pdf.compile_to_pdf(typst_path,output_path)
    
    # Step 8: Export pdf and .txt files
    
    # Step 9: Clean up any created files

if __name__ == "__main__":
    video_path = "Hackathon Test Recording.mp4"
    recording_to_docs(video_path)

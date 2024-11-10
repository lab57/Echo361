import os
import subprocess

def generate_typst_document(data, typst_path, document_setup_data):
    title, author = document_setup_data

    typst_content = f"""
#import "template.typ": *

#show: project.with(
  title: "{title}",
  authors: ((name: "{author}"),),
  date: [#datetime.today().display()],
)
    """
    
    for timestamp, image_path, summary in data:
        typst_content += f"""
Timestamp: {timestamp}s 
#figure(image("{image_path}", width: 100%),)
{summary}


#pagebreak()
"""

    with open(typst_path, 'w') as file:
        file.write(typst_content)

    print(f"Typst document saved to {typst_path}")

# def compile_typst_to_pdf(typst_file_path, pdf_output_path):
#     os.system(f"typst compile {typst_file_path} {pdf_output_path}")


def compile_to_pdf(typst_path="report.typ", output_file="report.pdf"):
    """
    Compile the Typst file to PDF using the Typst compiler.
    """
    try:
        subprocess.run(["./typst.exe", "compile", typst_path, output_file], check=True)
        print(f"PDF '{output_file}' has been generated.")
    except subprocess.CalledProcessError:
        print(
            "Error: Failed to compile Typst file. Make sure Typst is installed and accessible in your PATH."
        )
    except FileNotFoundError:
        print(
            "Error: Typst compiler not found. Please install Typst and make sure it's in your PATH."
        )
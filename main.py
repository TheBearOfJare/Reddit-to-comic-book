import praw
import requests
import os
from datetime import datetime
from fpdf import FPDF

bcolors = {
    'Error': '\033[91m',
    'Warning': '\033[93m',
    'Success': '\033[92m',
    'Ok blue': '\033[94m',
    'info purple': '\033[95m',
    'Reset': '\033[0m'
}

# --- Reddit API Credentials ---
CLIENT_ID = "-gjL-rH_3ZfRn8iitPMYTQ"
CLIENT_SECRET = "PtX3yVP9oRgJtoj4eSNom2U-faFIBg"
USER_AGENT = "comic_downloader by u/Darkphoton31"

# --- Configuration ---
REDDIT_USERNAME = "FieldExplores"
DOWNLOAD_DIR = "downloaded_images"

# Initialize PRAW
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

def image_downloader(redditor):
    # Counter for downloaded files
    post_counter = 0

    # Iterate through the user's submissions, sorted by 'new'
    # limit=None retrieves as many posts as possible (up to 1000 by default)
    
    try:
        for submission in redditor.submissions.new(limit=None):
            print(submission.title)
            # Check if the post is an image
            # A submission.url will often end in an image file extension (.jpg, .png, etc.)
            # or point to an imgur link that is an image.
            if submission.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                post_counter += 1
                
                # Get the creation timestamp
                creation_time = datetime.utcfromtimestamp(submission.created_utc)
                
                # Create a chronological filename
                # This format ensures that files are sorted correctly by name
                filename = f"{creation_time.strftime('%Y-%m-%d_%H-%M-%S')}_{post_counter:04d}_{submission.id}.{submission.url.split('.')[-1]}"
                filepath = os.path.join(DOWNLOAD_DIR, filename)

                # Check if the file has already been downloaded to prevent duplicates
                if os.path.exists(filepath):
                    print(f"{bcolors['ok blue']}File already exists, skipping: {filename}{bcolors['Reset']}")
                    continue

                try:
                    # Download the image
                    response = requests.get(submission.url)
                    response.raise_for_status()  # Raise an exception for bad status codes
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"Downloaded: {filename}")

                except requests.exceptions.RequestException as e:
                    print(f"{bcolors['Warning']}Could not download {submission.url}: {e}{bcolors['Reset']}")
                    continue
    except Exception as e:
        print(f"{bcolors['Error']}An error occurred while processing submissions: {e}{bcolors['Reset']}")
        return 
                   
    print(f"{bcolors['Success']}\nFinished! Downloaded {post_counter} posts to the '{DOWNLOAD_DIR}' directory.{bcolors['Reset']}")

def bookmaker():
    # initialize the PDF object
    pdf = FPDF()

    # iterate through the downloaded images, adding two per page using pdf.eph to scale to the size of the page
    for image in os.listdir(DOWNLOAD_DIR):
        pdf.add_page()
        pdf.image(os.path.join(DOWNLOAD_DIR, image), align="C", y = None, w = pdf.h / 2, h = pdf.h / 2, type='PNG')
        pdf.image(os.path.join(DOWNLOAD_DIR, image), align="C", y = None, w = pdf.h / 2, h = pdf.h / 2, type='PNG')

    # save the PDF
    pdf.output("Gator Days.pdf")
        
        
        

# Get the Redditor instance for the specified username
try:
    redditor = reddit.redditor(REDDIT_USERNAME)
except Exception as e:
    print(f"{bcolors['Error']}Error getting Redditor: {e}{bcolors['Reset']}")
    exit()

# Create the download directory if it doesn't exist
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)
    print(f"{bcolors['Ok blue']}Created directory: {DOWNLOAD_DIR}{bcolors['Reset']}")

print(f"{bcolors['info purple']}Starting to download posts from {REDDIT_USERNAME}...{bcolors['Reset']}")

# Start the image downloading process
image_downloader(redditor=redditor)

# Compile the images with fpdf2
bookmaker()

import praw
import requests
import os
from datetime import datetime

# --- Your Reddit API credentials ---
# Replace these with your own values from the Reddit app you created.
# You can also store these in a praw.ini file for better security.
# See https://praw.readthedocs.io/en/stable/getting_started/authentication.html
CLIENT_ID = "gjL-rH_3ZfRn8iitPMYTQ"
CLIENT_SECRET = "PtX3yVP9oRgJtoj4eSNom2U-faFIBg"
USER_AGENT = "comic_downloader by u/Darkphoton31"

# --- Configuration ---
REDDIT_USERNAME = "u/FieldExplores"
DOWNLOAD_DIR = "downloaded_comics"

# Initialize PRAW
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

# Get the Redditor instance for the specified username
try:
    redditor = reddit.redditor(REDDIT_USERNAME)
except Exception as e:
    print(f"Error getting Redditor: {e}")
    exit()

# Create the download directory if it doesn't exist
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)
    print(f"Created directory: {DOWNLOAD_DIR}")

print(f"Starting to download posts from u/{REDDIT_USERNAME}...")

# Counter for downloaded files
post_counter = 0

# Iterate through the user's submissions, sorted by 'new'
# limit=None retrieves as many posts as possible (up to 1000 by default)
# You can increase this by changing the limit if needed, though PRAW handles pagination for you
for submission in redditor.submissions.new(limit=None):
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
            print(f"File already exists, skipping: {filename}")
            continue

        try:
            # Download the image
            response = requests.get(submission.url)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded: {filename}")

        except requests.exceptions.RequestException as e:
            print(f"Could not download {submission.url}: {e}")
            continue

print(f"\nFinished! Downloaded {post_counter} posts to the '{DOWNLOAD_DIR}' directory.")

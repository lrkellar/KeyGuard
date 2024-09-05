import streamlit as st
import uuid
import csv
import os
from g_drive_service import GoogleDriveService
from googleapiclient.http import MediaIoBaseDownload
import io

# Directory to save uploaded images
IMAGE_DIR = "uploaded_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# Function to create a dictionary entry
def create_entry(root_id, property_address, gps_coord, property_name, key_type, pin_count, pin_depths, image_path, user_access_class, user_access_level):
    return {
        "Root_id": root_id,
        "Property_Address": property_address,
        "GPS_Coord": gps_coord,
        "Property_Name": property_name,
        "Key_Type": key_type,
        "Pin_Count": pin_count,
        "Pin_Depths": pin_depths,
        "Image_Path": image_path,
        "User_Access_Class": user_access_class,
        "User_Access_Level": user_access_level
    }

# Function to save entry to CSV
def save_to_csv(entry, filename='KeyIndex.csv'):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=entry.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)

# Function to load entries from CSV
def load_entries(filename='KeyIndex.csv'):
    entries = []
    if os.path.isfile(filename):
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                entries.append(row)
    return entries

# Function to download file from Google Drive
def download_file(file_id, file_name):
    service = GoogleDriveService().build()
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    return file_name

# Initialize the main dictionary
main_dict = {}

# Streamlit app
st.title("Property Data Entry")

# Sidebar for data entry
st.sidebar.header("Enter Property Data")
with st.sidebar.form(key='property_form'):
    property_address = st.text_input("Property Address")
    door_name = st.text_input("Door Name (optional)", placeholder="Front Door, Riser Room, etc")
    property_name = st.text_input("Property Name")
    key_type = st.selectbox("Key Type", ["Kwikset", "Schlage", "Mailbox"])
    pin_count = st.number_input("Pin Count", min_value=0, step=1)
    pin_depths = st.text_input("Pin Depths (comma-separated values)").split(',')
    image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    user_access_class = st.selectbox("User Access Class", ["Manager", "Owner", "Employee", "Resident"])
    user_access_level = st.number_input("User Access Level", min_value=0, step=1)
    
    submit_button = st.form_submit_button(label='Submit')

# Handle form submission
if submit_button:
    root_id = str(uuid.uuid4())  # Generate a random UUID for Root ID
    image_path = None
    if image is not None:
        image_path = os.path.join(IMAGE_DIR, f"{root_id}_{image.name}")
        with open(image_path, "wb") as f:
            f.write(image.getbuffer())
    
    entry = create_entry(root_id, property_address, door_name, property_name, key_type, pin_count, pin_depths, image_path, user_access_class, user_access_level)
    main_dict[root_id] = entry
    
    # Save entry to CSV
    save_to_csv(entry)
    
    # Upload CSV to Google Drive
    g_drive_service = GoogleDriveService()
    g_drive_service.upload_file('KeyIndex.csv', 'KeyIndex.csv')
    
    st.sidebar.success(f"Entry for Root ID {root_id} added successfully!")

# Display the contents of KeyIndex.csv from Google Drive
st.title("Key Index Contents")

# Assuming you have the file ID of KeyIndex.csv
file_id = 'KeyIndex.csv'  # Replace with the actual file ID
download_file(file_id, 'KeyIndex.csv')

entries = load_entries('KeyIndex.csv')
if entries:
    for entry in entries:
        st.write(entry)
else:
    st.write("No entries found.")


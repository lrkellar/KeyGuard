import streamlit as st
import uuid
import csv
import os

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
def save_to_csv(entry, filename='property_entries.csv'):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=entry.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)

# Function to load entries from CSV
def load_entries(filename='property_entries.csv'):
    entries = []
    if os.path.isfile(filename):
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                entries.append(row)
    return entries

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
    
    st.sidebar.success(f"Entry for Root ID {root_id} added successfully!")

# Display the list of Property_Name elements

from g_drive_service import GoogleDriveService

def get_file_list():
    selected_fields = "nextPageToken, files(id, name, webViewLink)"
    g_drive_service = GoogleDriveService().build()
    list_file = g_drive_service.files().list(fields=selected_fields).execute()
    return list_file.get("files")

st.title("Key List")

files = get_file_list()
if files:
    for file in files:
        st.write(f"Name: {file['name']}, Link: {file['webViewLink']}")
else:
    st.write("No files found.")

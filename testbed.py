import streamlit as st
from g_drive_service import GoogleDriveService

def get_file_list():
    selected_fields = "nextPageToken, files(id, name, webViewLink)"
    g_drive_service = GoogleDriveService().build()
    list_file = g_drive_service.files().list(fields=selected_fields).execute()
    return list_file.get("files")

st.title("Google Drive File Viewer")

files = get_file_list()
if files:
    for file in files:
        st.write(f"Name: {file['name']}, Link: {file['webViewLink']}")
else:
    st.write("No files found.")

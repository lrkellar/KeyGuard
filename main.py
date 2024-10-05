import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import uuid
from PIL import Image
from rembg import remove
import io
from pindisplay import create_kwikset_plot
import time
from gspread.exceptions import APIError

st.set_page_config(layout="wide")

# Streamlit app
st.title("KeyGuard")
st.markdown("A digital library of your keys")
code = st.secrets['passcode']
# Create a placeholder for the passcode input
passcode_placeholder = st.empty()
# Check if the user is authenticated
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
# Display the passcode input if not authenticated
if not st.session_state.authenticated:
    passcode = passcode_placeholder.text_input(label="Please enter your passcode", value="Speak friend and enter", type="password")
    if passcode == st.secrets['passcode']:
        st.session_state.authenticated = True
        passcode_placeholder.empty()  # Clear the passcode input
if st.session_state.authenticated:
    conn = st.connection("gsheets", type=GSheetsConnection)

    if conn:
        # Create a horizontal layout for the input and button
        col1, col2 = st.columns([3, 1])

        with col1:
            integer_input = st.text_input("Enter a key pin values here to view:", value="15243", max_chars=6)

        with col2:
            generate_button = st.button("Generate Plot")

        # Validate input and generate plot only when button is clicked
        if generate_button:
            if integer_input.isdigit() and 5 <= len(integer_input) <= 6:
                integer_input = int(integer_input)
                pin_count = len(str(integer_input))
                st.image(create_kwikset_plot(pin_count=pin_count, pins=integer_input))
            else:
                st.warning("Please enter a valid 5 or 6 digit integer.")


        existing_data = conn.read(worksheet="KeyIndex", ttl=5)
        existing_data = existing_data.dropna(how="all")

        presentation_data = existing_data.iloc[:, :7]
        # Add a search box
        search_query = st.text_input("Search keys", "")
        
        if search_query:
            filtered_data = presentation_data[existing_data.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
        else:
            filtered_data = presentation_data
        
        st.dataframe(filtered_data)
    else:
        st.error("Failed to connect to Google Sheets. Please check your connection settings.")

    KEY_TYPES = ["Kwikset", "Schlage"]
    PIN_COUNTS = [5, 6]

    User_access_class = "Admin"
    User_access_level = "test_id"
    Door_name = "front door"

    
    with st.sidebar:
        with st.form(key="vendor_form"):
            Property_Address = st.text_input(label="*Property Address", placeholder="30 Rockefeller")
            Door_name = st.text_input(label="*Door name or description", placeholder="Front door, riser room, or Apartment A")
            Property_name = st.text_input(label="Property Name", placeholder="30 Rock")
            Key_type = st.selectbox(label="Key Brand", options=KEY_TYPES)
            Pin_count = st.selectbox(label="Pin Count", options=PIN_COUNTS)
            Pin_depths = st.text_input(label="Pin Depths", placeholder="examples 5 Pin: 14241 or 6 pin: 334422")
            Picture = st.file_uploader(label="Upload an image", type=["png", "jpg", "jpeg"])

            st.markdown("**Required*")

            submit_button = st.form_submit_button(label="Add key")

            if submit_button:
                st.write("You pressed submit")

                # Check if all mandatory fields are filled
                if not Property_Address or not Key_type or not Pin_count:
                    st.warning("Ensure all fields are filled out")
                    st.stop()
                if not Property_name:
                    Property_name = Property_Address
                else:
                    key_entry = pd.DataFrame(
                        [{
                            "Root_id": uuid.uuid1(),
                            "Property_Address": Property_Address,
                            "Door_name": Door_name,
                            "Property_name": Property_name,
                            "Key_type": Key_type,
                            "Pin_count": Pin_count,
                            "Pin_depths": Pin_depths,
                            "User_access_class": User_access_class,
                            "User_access_level": User_access_level,
                        }]
                    )

                    if Picture:
                        Picture = Image.open(Picture)
                        Picture = remove(Picture)
                        # Convert the processed image to bytes
                        buffered = io.BytesIO()
                        Picture.save(buffered, format="PNG")
                        img_str = buffered.getvalue()
                        st.image(img_str, caption="Processed Image", use_column_width=True)
                        key_entry.at[0, "Image"] = img_str  # Store the image bytes

                    try:
                        existing_data = conn.read(worksheet="KeyIndex", ttl=5)
                        updated_df = pd.concat([existing_data, key_entry], ignore_index=True)
                        print(existing_data)
                        print(updated_df)
                        conn.update(worksheet="KeyIndex", data=updated_df)
                    except APIError as e:
                        print(f"Error encountered: {e}. Retrying in 10 seconds...")
                        time.sleep(10)
                        try:
                            existing_data = conn.read(worksheet="KeyIndex", ttl=5)
                            updated_df = pd.concat([existing_data, key_entry], ignore_index=True)
                            print(existing_data)
                            print(updated_df)
                            conn.update(worksheet="KeyIndex", data=updated_df)
                        except APIError as e:
                            print(f"Retry failed: {e}. Please check the server status and try again later.")

                    st.success("Key successfully added!")
                    st.image(create_kwikset_plot(pin_count=Pin_count, pins=Pin_depths))

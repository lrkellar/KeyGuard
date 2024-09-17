import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import uuid
from PIL import Image
from rembg import remove
import io

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
        existing_data = conn.read(worksheet="KeyIndex", usecols=list(range(1, 10)), ttl=5)
        existing_data = existing_data.dropna(how="all")
        
        # Add a search box
        search_query = st.text_input("Search keys", "")
        
        if search_query:
            filtered_data = existing_data[existing_data.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
        else:
            filtered_data = existing_data
        
        st.dataframe(filtered_data)
    else:
        st.error("Failed to connect to Google Sheets. Please check your connection settings.")

    KEY_TYPES = ["Kwikset", "Schlage"]
    PIN_COUNTS = [5, 6]

    User_access_class = "Admin"
    User_access_level = "test_id"

    with st.sidebar:
        with st.form(key="vendor_form"):
            Property_Address = st.text_input(label="Property Address", placeholder="30 Rockefeller")
            Door_name = st.text_input(label="Door name or description*", placeholder="Front door, riser room, or Apartment A")
            Property_name = st.text_input(label="Property Name*", placeholder="30 Rock")
            Key_type = st.selectbox(label="Key Brand", options=KEY_TYPES)
            Pin_count = st.selectbox(label="Pin Count", options=PIN_COUNTS)
            Pin_depths = st.text_input(label="Pin Depths", placeholder="examples 5 Pin: 14241 or 6 pin: 334422")
            Picture = st.file_uploader(label="Upload an image", type=["png", "jpg", "jpeg"])

            st.markdown("**Optional**")

            submit_button = st.form_submit_button(label="Add key")

            if submit_button:
                st.write("You pressed submit")

                # Check if all mandatory fields are filled
                if not Property_Address or not Key_type or not Pin_count:
                    st.warning("Ensure all fields are filled out")
                    st.stop()
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
                            "Image": None,  # Placeholder for the image
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

                    updated_df = pd.concat([existing_data, key_entry], ignore_index=True)
                    conn.update(worksheet="KeyIndex", data=updated_df)

                    st.success("Key successfully added!")

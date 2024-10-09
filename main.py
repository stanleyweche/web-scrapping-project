from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
import base64
from selenium.common.exceptions import StaleElementReferenceException

# Set up the Chrome WebDriver
service = Service('')  # Update this path to your chromedriver
driver = webdriver.Chrome(service=service)


# Function to scrape images from the currently opened page
def scrape_images():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    download_folder = os.path.join(desktop_path, 'downloaded_images')

    # Create download folder if it doesn't exist
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Wait for the page to load completely
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'img')))
    except Exception as e:
        print(f"Error waiting for images to load: {e}")
        driver.quit()
        return

    # Find all image elements
    images = driver.find_elements(By.TAG_NAME, 'img')

    # Download each image
    for index in range(len(images)):
        try:
            img = images[index]  # Get the image element
            src = img.get_attribute('src')
            alt = img.get_attribute('alt') or f'image_{index + 1}'  # Use alt text or fallback to a default name

            if src:
                # Check if the src is a data URL
                if src.startswith('data:image/'):
                    # Split the data URL into its components
                    header, base64_data = src.split(',', 1)
                    # Decode the base64 string
                    img_data = base64.b64decode(base64_data)

                    # Extract the image format from the header
                    image_format = header.split(';')[0].split('/')[1]  # e.g., png, jpeg
                    filename = f"{alt.replace(' ', '_').replace('/', '_')}.{image_format}"  # Use the correct extension

                    # Save the image
                    with open(os.path.join(download_folder, filename), 'wb') as handler:
                        handler.write(img_data)
                    print(f'Downloaded: {filename}')
                else:
                    # Get the image data from the URL
                    img_data = requests.get(src, timeout=10).content

                    # Create a valid filename
                    filename = alt.replace(' ', '_').replace('/', '_')  # Replace spaces and slashes
                    if not filename.endswith('.jpg'):
                        filename += '.jpg'  # Ensure it has a .jpg extension

                    # Save the image
                    with open(os.path.join(download_folder, filename), 'wb') as handler:
                        handler.write(img_data)
                    print(f'Downloaded: {filename}')
        except StaleElementReferenceException:
            print(f"StaleElementReferenceException encountered for image index {index}. Retrying...")
            # Re-fetch the images and retry
            images = driver.find_elements(By.TAG_NAME, 'img')
            continue  # Retry the current index
        except Exception as e:
            print(f'Could not download image at index {index}. Reason: {e}')


# Prompt the user for the URL and open it
url = input("Please enter the URL of the webpage to open: ")
driver.get(url)

# Call the function to scrape images from the opened page
scrape_images()

# Close the driver
driver.quit()

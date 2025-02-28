from selenium import webdriver

# Start the Chrome WebDriver
driver = webdriver.Chrome()

# Open a webpage
driver.get("https://www.google.com")

# Print the page title
print(driver.title)

# Close the browser window
driver.quit()
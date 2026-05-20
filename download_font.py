import urllib.request
try:
    urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf", "Roboto.ttf")
    print("Font downloaded successfully.")
except Exception as e:
    print("Error:", e)

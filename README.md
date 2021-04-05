# Crawler-immobilienscout24.de

This crawler goes through all results of multiple previously defined searches for real estate on the website www.immobilienscout24.de.

By this you can get data (about 90 features) for all current real estate offers at once.

## How to use:
Specify one or multiple searches on www.immobilienscout24.de manually. Paste the url of the first result page and a name in the dataframe df_search.

Specify the path where to store the crawled data.

Download driver for your webbrowser (e.g. https://chromedriver.chromium.org/ if using Chrome) and adjust its path.

Run the file.

## Captchas:
Captchas will always occur for the first url opened and then every ~600 offers. If so, the script will pause and ask you to solve the captcha and then press any button to continue.

If you have any idea how to prevent the captchas from occuring feel free to contribute to the code.

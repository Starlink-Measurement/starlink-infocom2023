First download/install the Chrome webdriver either using `apt` or place
the .exe in the same folder.

```
sudo apt install chromium-chromedriver
```

Use pipenv to install packages and setup environment:
```
pipenv install
pipenv shell
```

Create the file `config.py` and populate with the following:

```python
local_stores = {
    'disclaimerShown': 'true',
    'observerLat': '41.49923',
    'dishyAngle': '18',
    'dishyTilt': '18',
    'observerLng': '1.8950696'
    'fltVersion': 'all',
    }
```

`observerLat` and `observerLng` is your Starlink dishy's latitude and longitudes.
These values can be found in the local storage with the "Application" tab from chrome's devtools.

Add in the variable 'htleFile' to set the starting datetime. The format is `YYYYMMDDHHMMSS`.
For example,
```
    ...
    'htleFile': '20220519120000'
    ...
```
to set the datetime to May 19th, 2022 at 12:00:00.

Then, just run the scraper:
```
python scraper.py
```

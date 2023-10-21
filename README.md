# Installation
**This hasn't been tested on Mac so if you have a problem on Mac that really sounds like a you problem**
Clone this git by donwloading or using the `git clone` command
Open the folder on terminal and run the following commands
```
:: Create a virtual environment which is handy
py -m venv env
:: Activate it
<path to file>\env\Scripts\activate.bat
:: Download all relevant libraries
py -m pip install PyMuPDF Pillow urllib3
```

# Running
Then just run `main.py` and everything should work. Of course if you want you can edit some settings (like subjects)
To set the subject just go into `main.py` 
```
...

if __name__ == "__main__":
    set_subject("CODE")  # this should be the only code added, DON'T TOUCH ANYTHING ELSE
    # Code must be the full code, with 4 digits, don't write 606 write 0606

...
```
**!! When you're rerunning for a new subject remember that all the downloaded papers will be deleted.**
# Potential Scary Waries
- If you are downloading and this message shows up in the console:
`Failed to download paper ...`
Don't worry, that paper probably never existed. My program just iterates through every paper and if it doesn't exist it counts as a failed download
- If you are running the screenshot phase and it said `Question .. failed` don't worry because that question probably doesn't exist.
- If you are running the screenshot phase and it says `Failed??? Setting the cropbox for question...` then it's an actual bug to worry about please inform me.

Other unfound error may occur, please tell me if there are.

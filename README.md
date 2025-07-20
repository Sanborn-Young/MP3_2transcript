# MP3 to Transcript

## Overview of this package

Speaker diarization is a technique used in transcript creation to identify and label different speakers in an audio recording. It answers the question "who spoke when?" by breaking down the audio into segments and assigning labels to each speaker. One popular package to do this can be found at replicate.com/thomasmol/whisper-diarization. By using this package on Replicate, they'll keep everything up to date and synced, and they'll give you access to a GPU to be able to quickly create a transcript with voices identified. You do need to sign up with a credit card, but generally to translate an hour's worth of speech is cheap at somewhere around 10 or 20 cents for the translation using this service.

While using the package is easy and cheap, it only outputs a JSON file. From that JSON file, you generally want something that is more text-based. So this Python script automates much of the work that you would otherwise need to do manually to quickly be able to turn an MP3, feed it to replicate, have it create a JSON, and then turn this into a text file which is suitable for bringing up a final transcript.

## Requirements before using

Sign up for an account at Replicate.com. Replicate.com uses your GitHub sign-on to register you.

Put in a credit card at replicate.com so you have access to the GPU and processing.

## Python environments

This has only been tested under a virtual Python environment of 3.12.
You may not need to set up a virtual environment, although I strongly suggest it. It may also run underneath different versions of Python. However, I advise not moving to 3.13 as of this date because many packages have not synced with it.

## How to Get and Use Your Replicate API Key

### 1. Find Your API Key

1. Go to the Replicate API tokens page in your browser:
   https://replicate.com/account/api-tokens
2. Give your new token a descriptive name (e.g., "my-first-app").
3. Click the "Create token" button.
4. Your API token will be displayed. **Copy it immediately. It should be about thirty-nine characters or so.**

> **IMPORTANT:** Replicate will only show you the full token once.
> Store it in a secure location like a password manager.

## How to use this GitHub

### MP3 to Transcript

A GUI tool to transcribe audio from MP3 files.

### Installation

To install this tool, open your terminal and follow these steps.

1. **Clone the Repository**

```
git clone https://github.com/Sanborn-Young/MP3_2transcript.git
```

2. **Navigate into the Project Directory**

```
cd MP3_2transcript
```

3. **Install the Project and its Dependencies**
   This command uses the `setup.py` file to install the application and everything it needs to run.

```
pip install .
```

4. Open up the dotenv file with any text editor such as Notepad. You will see that it has the term replicate equals with a bunch of X's. Delete all the Xs and place your Replicate key which you got earlier in this space. Make sure that you include the entire key. Do not add any quotation marks around the key. Do not put a space before or after the key. Save the file. Make a copy of this file and change the name of the file to ".env" without the quotation marks. When the script runs, it needs to have the key from Replicate put into it so it can pass this during the API. It does this by looking for this file .env, which should be in the same directory as the main script. As always, if you expose this key or give it to somebody else, this basically gives anybody the ability to use your account to be able to use the Replicate API. So make sure that it is not public, but only in the same subdirectory as the main program.

## Invoking or starting up the program

Running these things can always be a little bit fickle. Make sure that you have the .env file sitting right next to the Python script. A very easy way of running this without normally any issues is to simply type in the following:

```
python GUIMP3_2transcript.py
```

However, the reason that we included a setup file and you did the pip install . was to simply be able to invoke it anywhere with the following command at the CLI:

```
mp3-2transcript
```

As of my upload in version 1.0, this seems to be working. For if any reason it doesn't, you will need to type in the other at the command line and issue a bug report.  Also, this is dependent upon Replicate not changing the Identification of the model in their API. If something blows up, this may be the source of it, and you would need to file a bug report so I can check.

## Actual usage once program is invoked

When running, the program will bring up a Tkinter dialog box which will allow you to select an MP3.

Once you have selected the MP3, it will ask you for the number of speakers that were present on the MP3. I have noticed this works very well with two speakers, but as you go to more speakers it struggles to be able to figure out the distinct voice type.

Once you have given it the right number of speakers, it will then attempt to upload it to the model on Replicate. You will see a dialog box that will tell you that it's processing. After it is done processing, it will ask you if you want to turn it into a Markdown file. This is where you may need to do a bit of intervention. If you have another window open, you will need to look in the same subdirectory as your MP3. What you will see is that the program has already created a JSON file. You may want to open up the JSON file, which is human-readable, and you will see that it identifies different speakers. If you can find a speaker and a piece of text that you know was spoken by somebody during the MP3, this will help you give labels to the speakers. If you can't figure it out immediately, then it will simply give it generic labels. You can always do a search and replace later, but the ability to put some labels on speakers may save you time later.

If you say yes, I want to do a markdown file, it will then query you on if you want to replace the generic titles with real names, and you will need to give a real name to each speaker until you are done with the number of speakers that you identified up front.

You will find now in the subdirectory another file with the extension MD, which stands for Markdown. Also, the names which you gave during the query phase, if you chose to give them, have been slightly formatted so that they should appear in bold. Again, putting labels on the speakers is optional, and will probably require you to open up the JSON file to do some guessing about which speaker is what.

After you have processed one file, it will ask you if you want to continue. Of course, if you don't, hit no, and the program will abort, and allow you to go back to whatever you were doing before in your command-line window.

## Other next steps you can do with this repository: hints and tips

On my own machine, I have gone farther and turned this into an executable file. The only challenge is it turns out to be relatively a more inconvenient thing to work through. Generally, the file has been tested to be able to be compiled via the following method. Compiling Python programs is never as easy as what it should be, mainly because you don't always pick up all the libraries or it makes assumptions about where various files should be that aren't immediately obvious unless you're doing a lot of compiling and are really familiar with the characteristics of the Python libraries and PyInstaller. But with that being written, let me go ahead and give you some tips in terms of what I did to get the program compiled.

Set up a virtual environment for 3.12. I use venv for everything on my machine.

Invoke the virtual environment.

Use this to clone the GitHub as above.

Transfer into your cloned subdirectory.

Install PyInstaller:

```
pip install pyinstaller
```

Hopefully you've installed this in your virtual environment. You may want to double check that pyinstaller is actually in your virtual environment by running the following:

```
where pyinstaller
```

It should give you back data saying that it's in your virtual environment folder. If not, it just won't run correctly.

PyInstaller doesn't always pick up all the dependencies and there's a couple dependencies in this file that you will want to pick up. So to force it to pick up something, you can run the following command:

```
pyinstaller --collect-all replicate --collect-all dotenv MP3toMD.py
```

During compile, the replicate and the .env were two problematic things which were not picked up by PyInstaller. By throwing the collect all after it, it will actually update your spec file, and then it will try to run the spec file. This was successful in my run and install. This will install it into your build subdirectory where you can run it. It will also create another subdirectory by it. You will need to copy your .env file into it. You could try to compile it all into one, but that slows things down and is a possible future task for me to try.

Unfortunately, after I made an executable, I then pushed everything to git, and my git install forced me to also make some changes to the main Python script. I cannot guarantee you that this won't give you some difficulty trying to compile it with PyInstaller. So, it's a development activity to be done. Somebody can volunteer to help patch here, or clone and maybe put an issue down that you fixed it in your own GitHub.

Finally, there is an icon file in the resource subdirectory if you want to put an icon on your exe. I had some difficulty in getting this to go with PyInstaller, so on my own personal machine I simply used ResourceHacker, an excellent utility that allows you to update various things such as icons on programs. ResourceHacker can be found at: https://www.angusj.com/resourcehacker/

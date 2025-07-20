#### Overview of this package



Speaker diarization is a technique used in transcript creation to identify and label different speakers in an audio recording. It answers the question "who spoke when?" by breaking down the audio into segments and assigning labels to each speaker. One popular package to do this can be found at replicate.com/thomasmol/whisper-diarization.  By using this package on Replicate, they'll keep everything up to date and synced, and they'll give you access to a GPU to be able to quickly create a transcript with voices identified.. You do need to sign up with a credit card, but generally to translate an hour's worth of speech is cheap at somewhere around 10 or 20 cents for the translation using this service.

While using the package is easy and cheap, it only outputs a JSON file. From that JSON file, you generally want something that is more text-based. So this Python script automates much of the work that you would otherwise need to do manually to quickly be able to turn an MP3, feed it to replicate, have it create a JSON, and then turn this into a text file which is suitable for bringing up a final transcript.



#### Requirements before using

Sign up for an account at Replicate.com. Replicate.com uses your GitHub sign-on to register you.

Put in a credit card at replicate.com so you have access to the GPU and processing.

#### Python environments

This has only been tested under a virtual Python environment of 3.12.
You may not need to set up a virtual environment, although I strongly suggest it. It may also run underneath different versions of Python. However, I advise not moving to 3.13 as of this date because many packages have not synced with it.

##### How to Get and Use Your Replicate API Key

##### 1. Find Your API Key

1.  Go to the Replicate API tokens page in your browser:
    https://replicate.com/account/api-tokens

2.  Give your new token a descriptive name (e.g., "my-first-app").

3.  Click the "Create token" button.

4.  Your API token will be displayed. **Copy it immediately.**

> **IMPORTANT:** Replicate will only show you the full token once.
> Store it in a secure location like a password manager.

#### How to use this GitHub


# MP3 to Transcript

A GUI tool to transcribe audio from MP3 files.

## Installation

To install this tool, open your terminal and follow these steps.

1.  **Clone the Repository**
    ```
    git clone https://github.com/Sanborn-Young/MP3_2transcript.git
    ```

2.  **Navigate into the Project Directory**
    ```
    cd MP3_2transcript
    ```

3.  **Install the Project and its Dependencies**
    This command uses the `setup.py` file to install the application and everything it needs to run.
    ```
    pip install .
    ```
4. Open up the dotenv file with any text editor such as Notepad. You will see that it has the term replicate equals with a bunch of X's. Delete all the Xs and place your Replicate key which you got earlier in this space. Make sure that you include the entire key. Do not add any quotation marks around the key. Do not put a space before or after the key. Save the file. Make a copy of this file and change the name of the file to ".env" without the quotation marks.  When the script runs, it needs to have the key from Replicate put into it so it can pass this during the API. It does this by looking for this file .env, which should be in the same directory as the main script. As always, if you expose this key or give it to somebody else, this basically gives anybody the ability to use your account to be able to use the Replicate API. So make sure that it is not public, but only in the same subdirectory as the main program.


## Usage

After the installation is complete, you can run the application from any location in your terminal by simply typing the following command:

mp3-2transcript








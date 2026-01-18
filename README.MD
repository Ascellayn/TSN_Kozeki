# Kozeki
A [TSNA](https://github.com/Ascellayn/TSN_Abstracter)-based tool to extract Blue Archive's `.molru` (and "MXMC" `.bytes`) PC files, a cursed file type given to us who like to poke around a bit too much.  
If you are unaware, since a few updates ago, Blue Archive on Steam recently started obfuscating the game files, which is quite the annoyance if you want to grab an image for a meme or a thumbnail or something.  
This tool's purpose is to be able to extract those files, and maybe some more in the future.  
Kozeki will in the future be able to recreate from scratch `.molru` files, although its utility might be questionable due to the Anti-Cheat.  

<br>

> [!CAUTION]
> Kozeki is currently early in development.  
> It currently supports extracting **JPEG**, **OGG**, and **PNG** files ***__while keeping their original file names__***.  
> However the Repack/Editing feature of `.molru` files remains to be fully reverse engineered in order to be able to effectively mod the game. (Assuming you can bypass the "Abnormal Game Client" message which is possible at your own risk.)

<br>

## Setup
> [!NOTE]
> Kozeki is primarily developed (including its dependency TSNA) on Linux.
> While tests have shown that *compatibility on Windows seems perfect*, on average everything is slower **especially generating the "MXMC" Definitions Cache**.
> You may wish to download `MXMC_Cache.cjson` too if you have the miss fortune of running Kozeki on Windows, if that cache on the repository is up to date.

<br>

1. Download [TSN_Kozeki.py](https://raw.githubusercontent.com/Ascellayn/TSN_Kozeki/refs/heads/main/TSN_Kozeki.py)  
And place the file at the root of your Blue Archive Folder (the one containing the Blue Archive Executable).
2. You may download [MXMC_Definitions.cjson](https://raw.githubusercontent.com/Ascellayn/TSN_Kozeki/refs/heads/main/MXMC_Definitions.cjson)  
If generating the File Name Definitions is taking too long. (If you're on Windows, DO THIS!)
3. Install [TSN Abstracter](https://github.com/Ascellayn/TSN_Abstracter)  
You can simply just drag and drop the `TSN_Abstracter` folder where `TSN_Kozeki.py` is located.  
Or if you're more advanced, clone the TSNA repository and add the cloned folder to your `PYTHONPATH`.

<br>

##### You should end up with a similar looking file structure:
```
 BlueArchive/ (→ Your game folder)
	|-  BlueArchive_Data/
	|-  TSN_Abstracter/
		|- __init__.py
		|- ...
	|-  BlueArchive.exe
	|-  TSN_Kozeki.py
	\-> MXMC_Definitions.cjson (→ If you've downloaded this file)
```

<br>

4. Run `python3 TSN_Kozeki.py` in your favorite terminal and watch it go!  
You may run `python3 TSN_Kozeki.py -h` to get a list of the following arguments:  
```
Options
	-h			= Print usage information and exit.
	-d			= Enable Debug Mode.
	--limit-logs		= Disable showing which files are extracted, improves performance significantly.

	--extractor <extractor>	= Enforce an extraction method. Available ones are: 'regex'. (default: 'regex').
	--repack <folder>	= The folder containing the data we wish to repack as a Molru file.
	--skip-mxmc 		= Do not use the MXMC Definitions System, recommended on Windows where generating it is stupid slow.
	--only-mxmc 		= Only execute Kozeki to generate a MXMC Definitions Cache, used for Data Research. Also saves an uncompressed version.
```

<br>


You should end up with a `Extracted` folder, processing certain `molru` files may take a while depending on their size. The stronger your computer is at single-threaded tasks the faster it should run.  
**Enabling debug mode SEVERELY slows down Kozeki's Extraction.**
A future update will introduce partial multi-threading as a desperate attempt to make it more bearable to extract everything at once.

<br>

## Repacking (Editing / Creating Molru Files)
**The Kozeki Repacker currently does not create Molru files that can be loaded by Blue Archive.**  
We currently do not know how the Molru headers from Hex 0x04 to 0x34 work, which in turn, as likely a checksum is present, makes the game refuse to load properly the Molru file even if you bypass the "Abnormal Client Detected" message.  
This feature is thus currently merely here **for research purposes** and can be accessed by running `python3 TSN_Kozeki --repack <folder name>`.  

<br>

## The MX Media Catalogue (MXMC) Definitions
What I call "MXMC" is a file format that is quite odd, it's located under `BlueArchive_Data/StreamingAssets/PUB/Resource/Catalog` and seemingly holds every file name and their internally referenced names in the game.  
It's under a `.bytes` format and doesn't contain a readable file header, however I've decided to name it "MXMC" as it's likely obviously made by MX Studios and since it's a Catalog of... Media. It's right in the directory name really.  
It might be a temporary solution to Molru files not having a file name when extracting Molru files as **the iOS build of the game has a completely different one** (while having the same data) ***and transplanting it into the PC version seemed to cause absolutely zero issues***. With the way Kozeki handles this file and how the file is structured, it's not unlikely that if Nexon decides to combat Kozeki that we'll loose this feature forever. Fingers crossed we'll be fine.  
Kozeki by default generates a `MXMC_Definitions.cjson` file which is **a 7z compressed JSON file**. You can decompress it using TSN Abstracter's `File.JSON_Read("MXMC_Definitions.cjson", True)` or you can just not bother and check the published decompressed file on this repository at [Research/MXMC_Definitions.json](https://raw.githubusercontent.com/Ascellayn/TSN_Kozeki/refs/heads/main/Research/MXMC_Definitions.json).

<br>

#### Why Kozeki?
Thought it'd made sense to name this script by Ui from a certain epic anime rpg video game since she's capable of restoring something that is nye unreadable to mere mortals such as every single one of us.  
It is also tradition to name any new project that I'm working on by something Blue Archive related. Kozeki is technically a codename, if you find a better name for this script, feel free to give me suggestions.  
Also technically a tool already exists [here](https://github.com/TanyanArchitect/Blue-Archive-Steam-version-MOLRU-files-extractor), however I do not trust AI Slop and trust my garbage code significantly more. Yes I seriously rewrote this tool because I didn't want to touch AI Generated scripts (and also because I think in my opinion this is going to be much more readable and maintainable). Cancel me on my Twitter dot com if you don't agree with my childish move instead of pulling a nuclear pull request. [It's right there](https://twitter.com/siriusbyt).  

##### v0.7 Update:
After bloodshed and tears, I'm happy to announce now that, that previous tool is now likely not worth using as Kozeki now is capable of restoring file names, which the other tool is not capable of. Hopefully Repacking is up next on the list!

<br>

###### [TSN_Kozeki © (2025-2026) - Ascellayn | TSN License 2.1 - Universal](https://sirio-network.com/license/2.1)

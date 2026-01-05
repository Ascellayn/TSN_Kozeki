# Kozeki
A TSNA based tool to extract Blue Archive's `.molru` PC files, a cursed file type given to us who like to poke around a bit too much.  
If you are unaware, since a few updates ago, Blue Archive on Steam recently started obfuscating the game files, which is quite the annoyance if you want to grab an image for a meme or a thumbnail or something.  
This tool's purpose is to be able to extract those files, and maybe some more in the future.  
Kozeki will in the future be able to recreate from scratch `.molru` files, although its utility might be questionable due to the Anti-Cheat.  

<br>

> [!CAUTION]
> This tool is VERY MUCH unfinished and is in a **proof of concept** stage.  
> As of right now it only supports **JPEG**, **PNG** and **OGG** files, although implementing more file types should be easy.

<br>

## Setup
**Notice:** Kozeki is primarily tested on **Linux**, while a few tests showed that it seems fine on Windows, I cannot do extended tests so it's possible that some things may be weird!  
- Download [TSN_Kozeki.py](https://raw.githubusercontent.com/Ascellayn/TSN_Kozeki/refs/heads/main/TSN_Kozeki.py) and place the file at the root of your Blue Archive Folder (the one containing the Blue Archive Executable).
- Install [TSN Abstracter](https://github.com/Ascellayn/TSN_Abstracter), you can simply just drag and drop the `TSN_Abstracter` folder where `TSN_Kozeki.py` is located or if you're more advanced, clone the TSNA repository and add the cloned folder to your `PYTHONPATH`.
- Run `python3 TSN_Kozeki.py` in your favorite terminal and watch it go!

You should end up with a `Extracted` folder, processing certain `molru` files may take a while depending on their size. The stronger your computer is at single-threaded tasks the faster it should run.  
A future update will introduce partial multi-threading as a desperate attempt to make it more bearable to extract everything at once.

<br>

## Repacking (Editing / Creating Molru Files)
The Kozeki Repacker currently does not create Molru files that can be loaded by Blue Archive.  
We currently do not know how the Molru headers from Hex 0x04 to 0x34 work, which in turn, as likely a checksum is present, makes the game refuse to load properly the Molru file even if you bypass the "Abnormal Client Detected" message.  
This feature is thus currently merely here for research purposes and can be accessed by running `python3 TSN_Kozeki --repack <folder name>`.  


<br>

#### Why Kozeki?
Thought it'd made sense to name this script by Ui from a certain epic anime rpg video game since she's capable of restoring something that is nye unreadable to mere mortals such as every single one of us.  
It is also tradition to name any new project that I'm working on by something Blue Archive related. Kozeki is technically a codename, if you find a better name for this script, feel free to give me suggestions.  
Also technically a tool already exists [here](https://github.com/TanyanArchitect/Blue-Archive-Steam-version-MOLRU-files-extractor), however I do not trust AI Slop and trust my garbage code significantly more. Yes I seriously rewrote this tool because I didn't want to touch AI Generated scripts (and also because I think in my opinion this is going to be much more readable and maintainable). Cancel me on my Twitter dot com if you don't agree with my childish move instead of pulling a nuclear pull request. [It's right there](https://twitter.com/siriusbyt).  

<br>

###### TSN_Kozeki © (2025-2026) - Ascellayn | TSN License 2.1 - Universal
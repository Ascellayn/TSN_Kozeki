# Kozeki
A TSNA based tool to extract Blue Archive's `.molru` PC files, a cursed file type given to us who like to poke around a bit too much.  
If you are unaware, since a few updates ago, Blue Archive on Steam recently started obfuscating the game files, which is quite the annoyance if you want to grab an image for a meme or a thumbnail or something.  
This tool's purpose is to be able to extract those files, and maybe some more in the future.

<br>

> [!CAUTION]
> This tool is VERY MUCH unfinished and is in a **proof of concept** stage. Certain information in the README may entirely be false for now as... My lazy ass is in the process of writing it.  
> As of right now it only supports **JPEG** files, although implementing more file types should be easy.

<br>

## Setup
**Notice:** Kozeki is primarily tested on **Linux**, while a few tests showed that it seems fine on Windows, I cannot guarantee that it will work correctly.  
- Install [TSN Abstracter](https://github.com/Ascellayn/TSN_Abstracter), you can simply just drag and drop the `TSN_Abstracter` folder where `TSN_Kozeki.py` is located, which should be at **the root folder of Blue Archive** or if you're more advanced, do some fancy `PYTHONPATH` thingy.
- Run `python3 TSN_Kozeki.py` in your favorite terminal and watch it go!

You should end up with a `Extracted` and `Unknown` folder, the Extracted Folder contains the goods, the Unknown folder contains Schizophrenia fuel (stuff that needs to be implemented and handled by Kozeki later on).

<br>

#### Why Kozeki?
Thought it'd made sense since Ui is capable of restoring something that is nye unreadable to mere mortals such as every single one of us.  
Also technically a tool already exists [here](https://github.com/TanyanArchitect/Blue-Archive-Steam-version-MOLRU-files-extractor), however I do not trust AI Slop and trust my garbage code significantly more. Yes I seriously rewrote this tool because I didn't want to touch AI Generated scripts (and also because I think in my opinion this is going to be much more readable and maintainable). Cancel me on my Twitter dot com if you don't agree with my childish move instead of pulling a nuclear pull request. [It's right there](https://twitter.com/siriusbyt).  

<br>

###### TSN_Kozeki © (2025) - Ascellayn | `TSN License 2.1 - Universal`
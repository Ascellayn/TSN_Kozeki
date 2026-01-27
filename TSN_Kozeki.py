from TSN_Abstracter import *;
import re, sys, typing;

Log.Clear();
Kozeki_Version: str = "v0.8.2";
Kozeki_Branch: str = "Azure";

Limit_Logs: bool = False;

MXMC_Only: bool = False;
MXMC_Disabled: bool = False;
MXMC_Dictionary: dict[str, list[tuple[str, str, str, str]]] = {};

def MX_MediaCatalog() -> None:
	""" The MX Media Catalogue (MXMC) is a .bytes file containing the internal name of a file and its path.
	We use the MXMC to rename our extracted files to their actual names. This function is currently slow and will be rewritten to maybe use Regex in the future for blazing fast processing."""
	if (MXMC_Disabled): return;

	# Hardcoded path for now because quite frankly the only file we need to deal with at the moment.
	global MXMC_Dictionary;

	MXMC_Init: int = Time.Get_Unix(True); MXMC_Progress: int = MXMC_Init;
	Buffer_Internal: bytes = b""; Buffer_External: bytes = b""; Key: str;
	Internal: bool = True;

	with open("BlueArchive_Data/StreamingAssets/PUB/Resource/Catalog/MediaResources/MediaCatalog.bytes", "r+b") as NCB: MXMC_Data: bytes = NCB.read();

	MXMC_Dictionary["__Version"] = MXMC_Data[1] + MXMC_Data[2]; # pyright: ignore[reportArgumentType] // stfu
	MXMC_Data = MXMC_Data[13:]; # We don't care about the header nor the "Internal/Unknown" 64 bits value.
	MXMC_Total: int = len(MXMC_Data);

	Log.Info(f"Need to process a total of {len(MXMC_Data)} Bytes; MXMC Version \"{MXMC_Dictionary["__Version"]}\" ");

	if (File.Exists("MXMC_Definitions.cjson")):
		MXMC_Cached: dict[str, Any] = File.JSON_Read("MXMC_Definitions.cjson", True);
		if (MXMC_Cached["__Version"] == MXMC_Dictionary["__Version"]):
			Log.Info(f"Cached MXMC Definitions Cache found and versions match, avoiding re-discovering everything.");
			MXMC_Dictionary = MXMC_Cached;
			return;
		else: Log.Warning(f"An MXMC Definitions Cache was found but is outdated! Will need to rediscover... (Expected {MXMC_Dictionary["__Version"]}, got {MXMC_Cached["__Version"]})");
	else: Log.Warning(f"No MXMC Definitions Cache was found, discovering file names...");
	Log.Stateless("Kozeki will now attempt to parse every single Filename that Blue Archive uses inside the BlueArchive_Data/StreamingAssets/ folder.\nThis is used so that exported data from Molru files have proper file names instead of their raw hex positions. This will take unfortunately a while, please be patient.");

	while (True):
		Byte: bytes = MXMC_Data[0:1];
		if (Byte in [b"\x03", b"\x02", b"\x01"]): # 0x03 = GameData // 0x02 = Preload // 0x01 = Root
			MXMC_Data = MXMC_Data[9:];
			if (Internal): Internal = False; continue;

			match Byte:
				case b"\x03": Key_Pre: str = "BlueArchive_Data/StreamingAssets/PUB/Resource/GameData/MediaResources/";
				case b"\x02": Key_Pre: str = "BlueArchive_Data/StreamingAssets/PUB/Resource/Preload/MediaResources/";
				case b"\x01": Key_Pre: str = "BlueArchive_Data/StreamingAssets/";
				case _:
					Log.Critical(f"John Nexon added a new Folder ID to the MXMC File Format, please notify Ascellayn to go coin himself in THE FINALS.\nKozeki will now close to prevent bad extractions. And by close we mean crashin-");
					raise Exception(Byte);

			Key = Key_Pre + "/".join(str(Buffer_External, "ASCII").split("/")[:-1]);
			if (Key not in MXMC_Dictionary.keys()): MXMC_Dictionary[Key] = [];
			MXMC_Dictionary[Key].append((str(Buffer_Internal, "ASCII"), str(Buffer_External, "ASCII"), str(Buffer_Internal, "ASCII").split("/")[-1], str(Buffer_External, "ASCII").split("/")[-1]));
			Buffer_External = b""; Buffer_Internal = b""; Internal = True;

			Log.Debug(f"Discovered {MXMC_Dictionary[Key][-1][3]} in {Key} // {len(MXMC_Data)} Bytes left to process");
			if (len(MXMC_Data) < 4): break;
			MXMC_Data = MXMC_Data[7:];

			if ((Time.Get_Unix() - MXMC_Progress) > 1):
				Log.Carriage(f"MX Catalog Parsing → {MXMC_Total - len(MXMC_Data)}/{MXMC_Total} ({round(((MXMC_Total - len(MXMC_Data))/MXMC_Total)*100, 2)}%) Bytes Processed");
				MXMC_Progress = Time.Get_Unix();


		else:
			if (Internal): Buffer_Internal += Byte;
			else: Buffer_External += Byte;
			MXMC_Data = MXMC_Data[1:];
	Log.Awaited().Status_Update(f"[OK: {len(MXMC_Dictionary.keys())} File Definitions Found]")

	Log.Info(f"Writing Cached MXMC cJSON...");
	File.JSON_Write("MXMC_Definitions.cjson", MXMC_Dictionary, True);
	Log.Awaited().OK();






def Extract_Regex(F: str) -> None:
	""" Regex extraction, requires a hefty amount of memory and can be slow for larger files."""
	Molru_Init: int = Time.Get_Unix(True);
	
	Molru_Name: str = F.split("/")[-1];
	File.Path_Require(f"Extracted/{F.replace(".molru", "")}/");

	with open(F, "r+b") as Molru: Bytes: bytes = Molru.read();
	Log.Debug(f"{Molru_Name}: Analyzing...");


	# Mental Illness
	Extract: typing.Iterator[re.Match[bytes]] | None = re.finditer(b"""
		(\xFF\xD8....									# JPEG (Group 1)
			(?:												# Signatures
				\x4A\x46\x49\x46|							# JFIF
				\x45\x78\x69\x66|							# EXIF
				\x49\x43\x43\x5F|							# XICC
				\x00\x01\x01\x01							# RAW
			)
			.+?\xFF\xD9 									# JPEG End of Data
			(?:\xFF\xED.+?\xFF\xD9)? 							# Photoshop Meta
			(?:\xFF\xE1.+?\xFF\xD9)? 							# Adobe XMP
			(?:\x38\x42\x49\x4D.+?\xFF\xD9)?					# 8BIM Meta
			(?:\x00\x38\x42\x49\x4D.+?\xFF\xD9)?				# 8BIM Meta (with an extra Byte 00 byte before because FUCK YOU I GUESS)
			(?:\xFF\xDB\x00\x43\x00\x03\x02\x02.+?\xFF\xD9)?	# There is a singular file that is beyond fucked and requires this extra check to correctly form the data. It'd require rewriting the whole way I deal with JPEGs so have this janky shit instead
		)|
		(\x4F\x67\x67\x53)|								# OGG (Group 2)
		(\x89\x50\x4E\x47.+?(?:\x49\x45\x4E\x44)....)	# PNG (Group 3)
	""", Bytes, re.DOTALL + re.VERBOSE);
	# If the JFIF/EXIF Regex looks so retarded, blame Adobe. No seriously. Well it's just metadata bullshit in general.


	Log.Awaited().OK();
	#Log.Debug(f"Found {len(list(Extract)) if (Extract) else 0} Chunks of data");
	# ↑ Uncommenting this causes Tchernobyl and breaks the extractor, so please don't do it.




	Trailing_Zeros: int = len(str(len(Bytes))); 
	def Write_Unknown(Start: int) -> None:
		if (Start - Offset == 0): return;
		Log.Warning(f"{Molru_Name}: Unknown Hex of {Start - Offset} Bytes @ 0x{String.Trailing_Zero(Offset, Trailing_Zeros)}-0x{String.Trailing_Zero(Start, Trailing_Zeros)}...");
		with open(f"Extracted/{F.replace(".molru", "")}/0x{String.Trailing_Zero(Offset, Trailing_Zeros)}-0x{String.Trailing_Zero(Start, Trailing_Zeros)}.hex", "w+b") as Img: Img.write(Bytes[Offset:Start]);
		Log.Awaited().OK();


	def Write_Data(Type: str, Extension: str, Start: int, End: int) -> None:
		Molru_Path: str = F.replace(".molru", "");

		MXMC_Definitions: tuple[str, str, str, str] | None = None;
		File_Name: str | None = None;
		if (Molru_Path in MXMC_Dictionary.keys()):
			if (len(MXMC_Dictionary[Molru_Path]) != 0):
				MXMC_Definitions = MXMC_Dictionary[Molru_Path].pop(0);
				File_Name = MXMC_Definitions[3];

		if (not File_Name):
			File_Name = f"0x{String.Trailing_Zero(Start, Trailing_Zeros)}-0x{String.Trailing_Zero(End, Trailing_Zeros)}.{Extension}";

		if (not Limit_Logs): Log.Stateless(f"{Molru_Name}: {Type} of {End - Start} Bytes @ 0x{String.Trailing_Zero(Start, Trailing_Zeros)}-0x{String.Trailing_Zero(End, Trailing_Zeros)} // \"{File_Name}\"");
		with open(f"Extracted/{F.replace(".molru", "")}/{File_Name}", "w+b") as Data: Data.write(Bytes[Start:End]);





	Offset: int = 0; Buffer_Start: int = 0; # Generic Dynamic Values
	Serial: bytes = b""; # OGG Specific Variable, read OGG Section



	def Found(Indexes: tuple[int, int]) -> bool: return False if (Indexes == (-1, -1)) else True;
	for Match in Extract:
		if (Found(Match.span(1))): # JFIF / EXIF
			Start: int = Match.span(1)[0]; End: int = Match.span(1)[1];
			match (Bytes[Start+3:Start+4]):
				case b"\xE0": Write_Data("JFIF", "JFIF.jpg", Start, End);
				case b"\xE1": Write_Data("EXIF", "EXIF.jpg", Start, End);
				case b"\xE2": Write_Data("XICC JPEG", "XICC.jpg", Start, End);
				case b"\xDB": Write_Data("RAW JPEG", "RAW.jpg", Start, End);
				case _: Write_Data("UNKNOWN JPEG", "UNKNOWN.JPEG", Start, End); # Assume it's JPEG RAW if we get here... Though we'll never get here since the regex will fail if it is JPEG Raw.
			Write_Unknown(Start);
			Offset = End; continue;



		if (Found(Match.span(2))): # OGG
			Start: int = Match.span(2)[0];
			Segments: int = int.from_bytes(Bytes[Start+27:Start+28:]);
			End: int = Start + 28 + Segments;
			Log.Debug(f"{Molru_Name}: OGG Header | Segments: {Segments} - Start: 0x{String.Trailing_Zero(Start, Trailing_Zeros)} - End: 0x{String.Trailing_Zero(End, Trailing_Zeros)} - Bytes: {End - Start}");


			# The only way for us to reliably parse OGG files is by checking the bitstream serial.
			if (Serial == Bytes[Start+14:Start+18]): continue;
			Serial = Bytes[Start+14:Start+18];


			if (Buffer_Start != 0): # Band-aid fix... Otherwise shit keeps creating a bad OGG file
				Write_Data("OGG", "ogg", Buffer_Start, Start);
				Offset = Start;


			Buffer_Start = Start;
			Write_Unknown(Buffer_Start); # Write Unknown is broken here for post-molru headers, I can't be arsed figuring out a solution right now though.
			continue;





		if (Found(Match.span(3))): # PNG
			Start: int = Match.span(3)[0]; End: int = Match.span(3)[1];
			Write_Data("PNG", "png", Start, End);
			Write_Unknown(Start);
			Offset = End; continue;





	# Catch unknown data at the end of files
	if (Offset != len(Bytes)): Write_Unknown(Offset);
	Log.Stateless(f"{F}: Finished Processing in {Time.Elapsed_String(Time.Get_Unix(True) - Molru_Init, " ", Show_Until=-3)}");
	#exit();










def Kozeki_Extractor(Extractor: str) -> None:
	if (not File.Exists("BlueArchive_Data")): Log.Critical("The \"BlueArchive_Data\" folder was not found! Quitting."); exit();

	Tree: File.Folder_Tree = File.Tree("BlueArchive_Data");
	def Molru_Recursion(Folder_Matrix: File.Folder_Matrix, Path: str = "BlueArchive_Data/") -> None:
		def Molru_Files(Files: list[str], Path: str) -> None:
			for File in Files:
				if (File.endswith(".molru")):
					Log.Info(f"Processing Molru \"{Path}{File}\"...");
					match Extractor.lower():
						case "regex": Extract_Regex(f"{Path}{File}");
						case _: raise Exception(f"Unknown Extractor: {Extractor}");
					Log.Awaited().OK();

		Path += f"{Folder_Matrix[0]}/"; Log.Debug(Path);
		Molru_Files(list(Folder_Matrix[1][1]), Path); # this looks cursed to make strict typing happy

		for Folder in Folder_Matrix[1][0]:
			Molru_Recursion(Folder, Path);

	for Folder in Tree[0]: Molru_Recursion(Folder);



def Kozeki_Repacker(Repacked_Folder: str) -> None:
	Log.Critical(f"The Kozeki Repacker currently does not create Molru files that can be loaded by Blue Archive.\nWe currently do not know how the Molru headers from Hex 0x04 to 0x34 work, which in turn, as likely a checksum is present, makes the game refuse to load properly the Molru file even if you bypass the \"Abnormal Client Detected\" message.\nThis feature is thus currently merely here for research purposes as of Kozeki v{Kozeki_Version}.")
	if (not File.Exists(Repacked_Folder)): Log.Critical(f"The \"{Repacked_Folder}\" folder was not found! Quitting."); exit();

	Buffer: bytes = b""; Repacked_Name: str = Repacked_Folder.split("/")[-1];
	Folder: File.Folder_Contents = File.List(Repacked_Folder);


	Log.Info(f"Repacking {Repacked_Name} containing {len(Folder[1])} files...");
	for Count, Data in enumerate(sorted(Folder[1])):
		Log.Debug(f"Reading: {Data}");
		with open(f"{Repacked_Folder}/{Data}", "r+b") as Data_Raw: Buffer += Data_Raw.read();
		Log.Carriage(f"Processed {Count+1}/{len(Folder[1])} Files");
	Log.Debug(f"Molru file of {len(Buffer)} Bytes in size.");
	
	with open(f"{Repacked_Name}.molru", "w+b") as Data: Data.write(Buffer);
	Log.Awaited().OK();









def Help():
	print("Usage");
	print("");
	print("python3 ./TSN_Kozeki.py [options]");
	print("python3 ./TSN_Kozeki.py --limit-logs --extractor regex");
	print("");
	print("A TSNA based tool to extract Blue Archive's .molru PC files, a cursed file type given to us who like to poke around a bit too much.");
	print("When running without any arguments, by defaults extracts every Molru file found in the BlueArchive_Data directory.");
	print("");
	print("Options");
	print("\t-h\t\t\t= Print usage information and exit.");
	print("\t-d\t\t\t= Enable Debug Mode.");
	print("\t--limit-logs\t\t= Disable showing which files are extracted, improves performance significantly.");
	print("");
	print("\t--extractor <extractor>\t= Enforce an extraction method. Available ones are: 'regex'. (default: 'regex').");
	print("\t--repack <folder>\t= The folder containing the data we wish to repack as a Molru file.");
	print("\t--skip-mxmc \t\t= Do not use the MXMC Definitions System, recommended on Windows where generating it is stupid slow.");
	print("\t--only-mxmc \t\t= Only execute Kozeki to generate a MXMC Definitions Cache, used for Data Research. Also saves an uncompressed version.");

if (__name__ == '__main__'):
	global Debug_Mode; Debug_Mode: bool;

	if (TSN_Abstracter.Version_Tuple[0] >= 6):
		# TSNA "Azure" v6+ Compatibility and avoid making users redownload the App.tsna file
		App.Name = "Kozeki";
		App.Description = "Kozeki is a TSNA based tool to extract Blue Archive's .molru PC files, a cursed file type given to us who like to poke around a bit too much.";
		App.Author = ["Ascellayn", "The Sirio Network"];
		App.License = "TSN License 2.1 - Universal";
		App.License_Year = "2025-2026";
		App.Codename = "TSN_Kozeki";
		App.Branch = "Azure";
		App.Version = (6,0,0);
		App.TSNA = (6,0,0);

		TSN_Abstracter.App_Init(False);
	else:
		Log.Stateless(f"Kozeki {Kozeki_Branch} - {Kozeki_Version} © Ascellayn / The Sirio Network (2025-2026) | TSN License 2.1 - Universal");
		Log.Stateless("Kozeki is a TSNA based tool to extract Blue Archive's .molru PC files, a cursed file type given to us who like to poke around a bit too much.\n");
		TSN_Abstracter.Require_Version((5,5,0));
		Log.Warning(f"You seem to be using TSN Abstracter 'Everest' (v5.X.X), Kozeki will still function just fine but do note that in the future you may need to download a newer version of TSNA if Kozeki ever needs a newer function from it.");

	# Argument Configuration
	Extractor: str = "regex";
	Repack_Folder: str | None = None;

	if (len(sys.argv) > 1):
		sys.argv.pop(0); # Useless
		if ("-h" in sys.argv):
			Help(); exit();

		try:
			while (sys.argv):
				match (sys.argv[0]):
					case "--extractor": Extractor = sys.argv.pop(1);
					case "--repack": Repack_Folder = sys.argv.pop(1);
					case "-d": Debug_Mode = True; print("== DEBUG MODE ENABLED ==");
					case "--skip-mxmc": MXMC_Disabled = True;
					case "--only-mxmc": MXMC_Disabled = False; MXMC_Only = True;
					case "--limit-logs": Limit_Logs = True;
					case _: raise Exception(f"Unknown argument: {sys.argv[0]}");
				sys.argv.pop(0);

		except Exception as Except:
			print(f"FATAL: A missing or invalid argument was passed through! Exiting.");
			raise Except;
			# ↑ Catching and then raising the exception is intended. Still informs the user what argument they got wrong without me having to do it myself, painfully copy pasting basically the same ugly code multiple times.


	try: Debug_Mode; # type: ignore | > shush, it's gonna be alright bb girl
	except NameError: Debug_Mode = False;

	# TSNA Configuration
	Config.Logger.Print_Level = 15 if (Debug_Mode) else 20; # type: ignore | > I SAID ITS GONNA BE ALRIGHT
	Config.Logger.File = False;

	MX_MediaCatalog();
	if (not MXMC_Only):
		if (not Repack_Folder): Kozeki_Extractor(Extractor);
		else: Kozeki_Repacker(Repack_Folder);
	else: File.JSON_Write("MXMC_Definitions.json", File.JSON_Read("MXMC_Definitions.cjson", True), False);

else: TSN_Abstracter.Require_Version((5,5,0));
# ↑ In case someone wants to import this file and use its extractors outside of the Kozeki script.
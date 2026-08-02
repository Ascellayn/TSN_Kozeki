from TSN_Abstracter import *;
import hashlib, re, sys, typing;
import multiprocessing, os;





More_Logs: bool = False;

MXMC_Only: bool = False;
MXMC_Disabled: bool = False;
MXMC_Dictionary: dict[str, list[tuple[str, str, str, str]]] = {};

# Determine which version of the game we are running, and set the Root folder where PUB is located accordingly
if (File.Exists("PUB/Ressource/Catalogue/iOS")):
	Data_Folder: str = ""; # This support is only theoretical because I can't get a version of Python higher than 3.9.9 on my iPhone, Palera1n Strap please fix
else: # PC (Steam)
	Data_Folder: str = "BlueArchive_Data/StreamingAssets/";





def MX_MediaCatalog() -> None:
	""" The MX Media Catalogue (MXMC) is a .bytes file containing the internal name of a file and its path.
	We use the MXMC to rename our extracted files to their actual names.
	
	Huge credits to @Apis035 for making me realize a SIGNIFICANTLY better way of handling MXMC."""
	if (MXMC_Disabled): return;

	# Hardcoded path for now because quite frankly the only file we need to deal with at the moment.
	global MXMC_Dictionary;

	MXMC_Init: int = Time.Get_Unix(True); MXMC_Progress: int = MXMC_Init;

	with open(f"{Data_Folder}PUB/Resource/Catalog/MediaResources/MediaCatalog.bytes", "r+b") as NCB: MXMC_Data: bytes = NCB.read();

	Log.Stateless(f"Calculating MXMC Hash...");
	MXMC_Dictionary["__Hash"] = hashlib.md5(MXMC_Data, usedforsecurity=False).hexdigest(); # pyright: ignore[reportArgumentType]
	Log.Awaited().OK();

	MXMC_Dictionary["__Size"] = int.from_bytes(MXMC_Data[1:4],byteorder="little"); # pyright: ignore[reportArgumentType] // stfu
	MXMC_Data = MXMC_Data[5:]; # Skip MXMC Header
	MXMC_Total: int = len(MXMC_Data);

	Log.Info(f"Need to process a total of {len(MXMC_Data)} Bytes; MXMC Hash: \"{MXMC_Dictionary["__Hash"]}\" - Size: \"{MXMC_Dictionary["__Size"]}\" ");

	if (File.Exists("MXMC_Definitions.cjson")):
		MXMC_Cached: dict[str, Any] = File.JSON_Read("MXMC_Definitions.cjson", True);
		if ("__Hash" in MXMC_Cached.keys()):
			if (MXMC_Cached["__Hash"] == MXMC_Dictionary["__Hash"]):
				Log.Info(f"Cached MXMC Definitions Cache found and versions match, avoiding re-discovering everything.");
				MXMC_Dictionary = MXMC_Cached;
				return;
			else: Log.Warning(f"An MXMC Definitions Cache was found but is outdated! Will need to rediscover... (Expected {MXMC_Dictionary["__Hash"]}, got {MXMC_Cached["__Hash"]})");
		else: Log.Warning(f"Pre-{App.Name} v0.8.3 MXMC Cache found, the cache will need to be re-discovered to properly make sure it is up to date!");
	else: Log.Warning(f"No MXMC Definitions Cache was found, discovering file names...");
	Log.Stateless("Kozeki will now attempt to parse every single Filename that Blue Archive uses.\nThis is used so that exported data from Molru files have proper file names instead of their raw hex positions.");

	Entries_Processed: int = 0;
	while (Entries_Processed < MXMC_Dictionary["__Size"]):
		# First u32 is currently unknown
			# Internal In-Game Name
		iLength: int = int.from_bytes(MXMC_Data[4:8], byteorder="little") + 8;
		iName: str = str(MXMC_Data[8:iLength], "ASCII");

			# Physical Location
		pLength: int = int.from_bytes(MXMC_Data[iLength+5:iLength+9], byteorder="little") + 8;
		pName: str = str(MXMC_Data[iLength+9:iLength+pLength+1], "ASCII");
		Content_Folder: bytes = MXMC_Data[iLength+pLength+1:iLength+pLength+2];

		match Content_Folder:
			case b"\x03": Key_Pre: str = f"{Data_Folder}PUB/Resource/GameData/MediaResources/";
			case b"\x02": Key_Pre: str = f"{Data_Folder}PUB/Resource/Preload/MediaResources/";
			case b"\x01": Key_Pre: str = f"{Data_Folder}";
			case _:
				Log.Critical(f"John Nexon added a new Folder ID to the MXMC File Format, please notify Ascellayn to go coin himself in THE FINALS.\nKozeki will now close to prevent bad extractions. And by close we mean crashin-");
				raise Exception(Content_Folder);
		
		Key: str = Key_Pre + "/".join(pName.split("/")[:-1]);
		if (Key not in MXMC_Dictionary.keys()): MXMC_Dictionary[Key] = [];
		MXMC_Dictionary[Key].append((
			iName,
			pName,
			iName.split("/")[-1],
			pName.split("/")[-1]
		));
		Log.Debug(f"Content Type: {Content_Folder} | Internal: char[{iLength}] \"{iName}\" | Physical: char[{pLength}] \"{pName}\"");

		if ((Time.Get_Unix() - MXMC_Progress) > 1):
			Log.Carriage(f"MX Catalog Parsing → {MXMC_Total - len(MXMC_Data)}/{MXMC_Total} ({round(((MXMC_Total - len(MXMC_Data))/MXMC_Total)*100, 2)}%) Bytes Processed");
			MXMC_Progress = Time.Get_Unix();

		MXMC_Data = MXMC_Data[iLength+pLength+9:];
		Entries_Processed += 1;

	Log.Awaited().OK(f"{len(MXMC_Dictionary.keys())} Folder Definitions Found");

	Log.Info(f"Writing Cached MXMC cJSON...");
	File.JSON_Write("MXMC_Definitions.cjson", MXMC_Dictionary, True);
	Log.Awaited().OK();





def Extract_Regex(F: str) -> None:
	""" Regex extraction, requires a hefty amount of memory and can be slow for larger files."""
	Molru_Init: int = Time.Get_Unix(True);

	Molru_Name: str = F.split("/")[-1];
	Molru_Path: str = F.replace(".molru", "");
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
	def Write_Unknown(Start: int | None) -> None:
		if (Start):
			if ((Start - Offset == 0)): return;

			# Avoid printing warning if it's the molru header
			if (Start != 53 and Offset != 0):
				Log.Warning(f"{Molru_Name}: Hex of {Start - Offset} Bytes @ 0x{String.Trailing_Zero(Offset, Trailing_Zeros)}-0x{String.Trailing_Zero(Start, Trailing_Zeros)}");

			with open(f"Extracted/{Molru_Path}/0x{String.Trailing_Zero(Offset, Trailing_Zeros)}-0x{String.Trailing_Zero(Start, Trailing_Zeros)}.hex", "w+b") as Data:
				Data.write(Bytes[Offset:Start]);
		else: # Flush the entire rest of the file if Start is None
			if (len(MXMC_Dictionary[Molru_Path]) == 1):
				Log.Warning(f"MXMC Failsafe: {MXMC_Dictionary[Molru_Path][-1][1]}");
				with open(f"Extracted/{Molru_Path}/{MXMC_Dictionary[Molru_Path].pop(0)[3]}", "w+b") as Data:
					Data.write(Bytes[Offset:]);
			else:
				Log.Warning(f"{Molru_Name}: EOF Hex of {len(Bytes) - Offset} Bytes @ 0x{String.Trailing_Zero(Offset, Trailing_Zeros)}-0x{String.Trailing_Zero(len(Bytes), Trailing_Zeros)}");
				with open(f"Extracted/{Molru_Path}/0x{String.Trailing_Zero(Offset, Trailing_Zeros)}-0x{String.Trailing_Zero(len(Bytes), Trailing_Zeros)}.hex", "w+b") as Data:
					Data.write(Bytes[Offset:]);



	def Write_Data(Type: str, Extension: str, Start: int, End: int) -> None:
		MXMC_Definitions: tuple[str, str, str, str] | None = None;
		File_Name: str | None = None;
		if (Molru_Path in MXMC_Dictionary.keys()):
			if (len(MXMC_Dictionary[Molru_Path]) != 0):
				MXMC_Definitions = MXMC_Dictionary[Molru_Path].pop(0);
				File_Name = MXMC_Definitions[3];

		if (not File_Name):
			File_Name = f"0x{String.Trailing_Zero(Start, Trailing_Zeros)}-0x{String.Trailing_Zero(End, Trailing_Zeros)}.{Extension}";

		if (More_Logs): Log.Stateless(f"{Molru_Name}: {Type} of {End - Start} Bytes @ 0x{String.Trailing_Zero(Start, Trailing_Zeros)}-0x{String.Trailing_Zero(End, Trailing_Zeros)} // \"{File_Name}\"");
		with open(f"Extracted/{Molru_Path}/{File_Name}", "w+b") as Data: Data.write(Bytes[Start:End]);





	Offset: int = 0; Buffer_Start: int = 0; # Generic Dynamic Values
	Serial: bytes = b""; # OGG Specific Variable, read OGG Section



	def Found(Indexes: tuple[int, int]) -> bool: return False if (Indexes == (-1, -1)) else True;
	for m in Extract:
		if (Found(m.span(1))): # JFIF / EXIF
			Start: int = m.span(1)[0]; End: int = m.span(1)[1];
			match (Bytes[Start+3:Start+4]):
				case b"\xE0": Write_Data("JFIF", "JFIF.jpg", Start, End);
				case b"\xE1": Write_Data("EXIF", "EXIF.jpg", Start, End);
				case b"\xE2": Write_Data("XICC JPEG", "XICC.jpg", Start, End);
				case b"\xDB": Write_Data("RAW JPEG", "RAW.jpg", Start, End);
				case _: Write_Data("UNKNOWN JPEG", "UNKNOWN.JPEG", Start, End); # Assume it's JPEG RAW if we get here... Though we'll never get here since the regex will fail if it is JPEG Raw.
			Write_Unknown(Start);
			Offset = End; continue;



		if (Found(m.span(2))): # OGG
			Start: int = m.span(2)[0];
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





		if (Found(m.span(3))): # PNG
			Start: int = m.span(3)[0]; End: int = m.span(3)[1];
			Write_Data("PNG", "png", Start, End);
			Write_Unknown(Start);
			Offset = End; continue;





	# Catch unknown data at the end of files
	if (Offset != len(Bytes)): Write_Unknown(None);
	if (Molru_Path in MXMC_Dictionary.keys()):
		if (len(MXMC_Dictionary[Molru_Path]) != 0):
			Log.Critical(f"The MXMC tells us there's {len(MXMC_Dictionary[Molru_Path])} more files hidden... But Kozeki failed to identify them!");

	if (More_Logs): Log.Stateless(f"{F}: Finished Processing in {Time.Elapsed_String(Time.Get_Unix(True) - Molru_Init, " ", Show_Until=-3)}");
	#exit();










def Pool_Initializer(more_logs: bool, data_folder: str, mxmc_dictionary: dict[str, list[tuple[str, str, str, str]]]):
	global More_Logs, Data_Folder, MXMC_Dictionary;
	More_Logs = more_logs;
	Data_Folder = data_folder;
	MXMC_Dictionary = mxmc_dictionary;



def Kozeki_Extractor(Extractor: str) -> None:
	if (not File.Exists("BlueArchive_Data") and not File.Exists("PUB")): Log.Critical("The \"BlueArchive_Data\" or \"PUB\" folder was not found! Quitting."); exit();

	Tree: File.Folder_Tree = File.Tree("BlueArchive_Data") if File.Exists("BlueArchive_Data") else File.Tree("PUB");
	def Molru_Recursion(Folder_Matrix: File.Folder_Matrix, Path: str = "BlueArchive_Data/", Molrus: set[str] = set()) -> set[str]:
		def Molru_Files(Files: list[str], Path: str) -> set[str]:
			sMolrus: set[str] = set();
			for f in Files:
				if (f.endswith(".molru")):
					sMolrus.add(f"{Path}{f}");
			return sMolrus;

		Path += f"{Folder_Matrix[0]}/"; Log.Debug(Path);
		Molrus.update(Molru_Files(list(Folder_Matrix[1][1]), Path));

		for f in Folder_Matrix[1][0]:
			Molrus.update(Molru_Recursion(f, Path, Molrus));
		
		return Molrus;

	Molrus: set[str] = set();
	for f in Tree[0]:
		Molrus.update(Molru_Recursion(f));

	Log.Info(f"Discovered {len(Molrus)} Molru files, proceeding to extraction.");

	Extract_Init: float = Time.Get_Unix(True);

	with multiprocessing.Pool(Extraction_Threads, initializer=Pool_Initializer, initargs=(More_Logs, Data_Folder, MXMC_Dictionary)) as P:
		match Extractor.lower():
			case "regex": P.imap_unordered(Extract_Regex, Molrus);
			case _: raise Exception(f"Unknown Extractor: {Extractor}");
		P.close(); P.join();


	"""
	for Molru in Molrus:
		Log.Info(f"Processing Molru \"{Molru}\"...");
		match Extractor.lower():
			case "regex": Extract_Regex(Molru);
			case _: raise Exception(f"Unknown Extractor: {Extractor}");
		Log.Awaited().OK();
	"""

	Log.Stateless(f"Extraction finished in {Time.Elapsed_String(Time.Get_Unix(True) - Extract_Init, " ", Show_Until=-3)}.");



def Kozeki_Repacker(Repacked_Folder: str) -> None:
	Log.Critical(f"The Kozeki Repacker currently does not create Molru files that can be loaded by Blue Archive.\nWe currently do not know how the Molru headers from Hex 0x04 to 0x34 work, which in turn, as likely a checksum is present, makes the game refuse to load properly the Molru file even if you bypass the \"Abnormal Client Detected\" message.\nThis feature is thus currently merely here for research purposes as of Kozeki v{".".join(String.ify_Array(App.Version))}.");
	if (not File.Exists(Repacked_Folder)): Log.Critical(f"The \"{Repacked_Folder}\" folder was not found! Quitting."); exit();

	Buffer: bytes = b""; Repacked_Name: str = Repacked_Folder.split("/")[-1];
	Folder: File.Folder_Contents = File.List(Repacked_Folder);


	Log.Info(f"Repacking {Repacked_Name} containing {len(Folder[1])} files...");
	for i, data in enumerate(sorted(Folder[1]), start=1):
		Log.Debug(f"Reading: {data}");
		with open(f"{Repacked_Folder}/{data}", "r+b") as Data_Raw: Buffer += Data_Raw.read();
		Log.Carriage(f"Processed {i}/{len(Folder[1])} Files");
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
	print("\t--more-logs\t\t= Show which files are being extracted, drastically lowers performance.");
	print("");
	print("\t--extractor <extractor>\t= Enforce an extraction method. Available ones are: 'regex'. (default: 'regex').");
	print("\t-t <threads>\t= Set how many threads Kozeki should use to Extract Molru files. Set this value lower to prevent overloading your device. (default: Maximimum available CPU Cores).");
	print("");
	print("\t--repack <folder>\t= The folder containing the data we wish to repack as a Molru file.");
	print("\t--skip-mxmc \t\t= Do not use the MXMC Definitions System when extracting files. Files will not have easy to read names.");
	print("\t--only-mxmc \t\t= Only execute Kozeki to generate a MXMC Definitions Cache, used for Data Research. Also saves an uncompressed version.");










if (__name__ == '__main__'):
	global Debug_Mode; Debug_Mode: bool;
	App.JSON({
		"Name": "Kozeki",
		"Description": "Kozeki is a TSNA based tool to extract Blue Archive's .molru PC files, a cursed file type given to us who like to poke around a bit too much.",
		"Author": ["Ascellayn", "The Sirio Network"],
		"Contributors": [],
		"License": "TSN License 2.2 - Universal",
		"License_Year": "2025-2026",
		"Codename": "TSN_Kozeki",
		"Branch": "Azure",
		"Version": [0,8,6],
		"Version_Prefix": "",
		"Version_Suffix": "",
		"TSNA": [6,1,0],
		"Public": [],
		"Private": []
	});
	TSN_Abstracter.App_Init(False);





	# Argument Configuration
	Extractor: str = "regex";
	Extraction_Threads: int = os.process_cpu_count();
	Repack_Folder: str | None = None;

	argv: list[str] = sys.argv[:];
	if (len(argv) > 1):
		print(argv);
		argv.pop(0); # Useless
		if ("-h" in argv):
			Help(); exit();

		try:
			while (argv): # TODO: Use argparse instead
				match (argv[0]):
					case "--extractor": Extractor = argv.pop(1);
					case "--repack": Repack_Folder = argv.pop(1);
					case "-t": Extraction_Threads = int(argv.pop(1));
					case "-d": Debug_Mode = True; print("== DEBUG MODE ENABLED ==");
					case "--skip-mxmc": MXMC_Disabled = True;
					case "--only-mxmc": MXMC_Disabled = False; MXMC_Only = True;
					case "--more-logs": More_Logs = True;
					case _: raise Exception(f"Unknown argument: {argv[0]}");
				argv.pop(0);

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

else: TSN_Abstracter.Require_Version((6,0,0));
# ↑ In case someone wants to import this file and use its extractors outside of the Kozeki script.
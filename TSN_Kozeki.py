from TSN_Abstracter import *;
import re, sys, typing;

Log.Clear();
Kozeki_Version: str = "v0.6.0";
Kozeki_Branch: str = "Azure";



def Extract_Regex(F: str) -> None:
	""" Regex extraction, requires a hefty amount of memory and can be slow for larger files."""
	Molru_Init: int = Time.Get_Unix(True);
	
	Molru_Name: str = F.split("/")[-1];
	File.Path_Require(f"Extracted/{F.replace(".molru", "")}/");

	with open(F, "r+b") as Molru: Bytes: bytes = Molru.read();
	Log.Debug(f"{Molru_Name}: Analyzing...");
	Extract: typing.Iterator[re.Match[bytes]] | None = re.finditer(b"""
		(\xFF\xD8...w.\x4A\x46\x49\x46.+?\xFF\xD9)|			# JFIF (Group 1)
		(\x4F\x67\x67\x53)|									Log# OGG (Group 2)
		(\x89\x50\x4E\x47.+?(?:\x49\x45\x4E\x44)....)	# PNG (Group 3)
	""", Bytes, re.DOTALL + re.VERBOSE);
	Log.Awaited().OK();





	Trailing_Zeros: int = len(str(len(Bytes))); 
	def Write_Unknown(Start: int) -> None:
		if (Start - Offset == 0): return;
		Log.Warning(f"{Molru_Name}: Unknown Hex of {Start - Offset} Bytes @ 0x{String.Trailing_Zero(Offset, Trailing_Zeros)}-0x{String.Trailing_Zero(Start, Trailing_Zeros)}...");
		with open(f"Extracted/{F.replace(".molru", "")}/0x{String.Trailing_Zero(Offset, Trailing_Zeros)}-0x{String.Trailing_Zero(Start, Trailing_Zeros)}.hex", "w+b") as Img: Img.write(Bytes[Offset:Start]);
		Log.Awaited().OK();


	def Write_Data(Type: str, Extension: str, Start: int, End: int) -> None:
		Log.Stateless(f"{Molru_Name}: {Type} of {End - Start} Bytes @ 0x{String.Trailing_Zero(Start, Trailing_Zeros)}-0x{String.Trailing_Zero(End, Trailing_Zeros)}");
		with open(f"Extracted/{F.replace(".molru", "")}/0x{String.Trailing_Zero(Start, Trailing_Zeros)}-0x{String.Trailing_Zero(End, Trailing_Zeros)}.{Extension}", "w+b") as Data: Data.write(Bytes[Start:End]);





	Offset: int = 0; Buffer_Start: int = 0; # Generic Dynamic Values
	Serial: bytes = b""; # OGG Specific Variable, read OGG Section



	def Found(Indexes: tuple[int, int]) -> bool: return False if (Indexes == (-1, -1)) else True;
	for Match in Extract:
		if (Found(Match.span(1))): # JFIF
			Start: int = Match.span(1)[0]; End: int = Match.span(1)[1];
			Write_Data("JFIF", "jpeg", Start, End);
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
	Log.Info(f"{F}: Finished Processing in {Time.Elapsed_String(Time.Get_Unix(True) - Molru_Init, " ", Show_Until=-3)}");










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
	print("python3 ./TSN_Kozeki.py -d --extractor slow");
	print("");
	print("A TSNA based tool to extract Blue Archive's .molru PC files, a cursed file type given to us who like to poke around a bit too much.");
	print("When running without any arguments, by defaults extracts every Molru file found in the BlueArchive_Data directory.");
	print("");
	print("Options");
	print("\t-h\t\t\t= Print usage information and exit.");
	print("\t-d\t\t\t= Enable Debug Mode.");
	print("");
	print("\t--extractor <extractor>\t= Enforce an extraction method. Available ones are: 'regex'. (default: 'regex').");
	print("\t--repack <folder>\t= The folder containing the data we wish to repack as a Molru file.");


if (__name__ == '__main__'):
	Log.Stateless(f"Kozeki {Kozeki_Branch} - {Kozeki_Version} © Ascellayn (2025) // TSN License 2.1 - Universal");
	Log.Stateless("Kozeki is a TSNA based tool to extract Blue Archive's .molru PC files, a cursed file type given to us who like to poke around a bit too much.\n");
	global Debug_Mode; Debug_Mode: bool;
	TSN_Abstracter.Require_Version((5,4,0));

	# Argument Configuration
	Extractor: str = "regex";
	Repack_Folder: str | None = None;

	if (len(sys.argv) > 1):
		sys.argv.pop(0); # Useless
		if ("-h" in sys.argv):
			Help(); exit();

		try:
			for Argument in sys.argv:
				match Argument:
					case "--extractor": Extractor = sys.argv.pop(1);
					case "--repack": Repack_Folder = sys.argv.pop(1);
					case "-d": Debug_Mode = True; print("== DEBUG MODE ENABLED ==");
					case _: raise Exception(f"Unknown argument: {Argument}");
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

	if (not Repack_Folder): Kozeki_Extractor(Extractor);
	else: Kozeki_Repacker(Repack_Folder);

else: TSN_Abstracter.Require_Version((5,4,0));
# ↑ In case someone wants to import this file and use its extractors outside of the Kozeki script.
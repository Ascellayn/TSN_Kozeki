from TSN_Abstracter import *;
import re, sys, typing;

Log.Clear();
Kozeki_Version: str = "v0.3.0";
Kozeki_Branch: str = "Azure";



def Extract_Regex(F: str) -> None:
	""" Regex extraction, requires a hefty amount of memory and can be slow for larger files."""
	Molru_Init: int = Time.Get_Unix(True);
	File.Path_Require(f"Extracted/{F.replace(".molru", "")}/");

	with open(F, "r+b") as Molru: Bytes: bytes = Molru.read();

	Log.Debug(f"Attempting to find files, this may take a while...");
	Extract: typing.Iterator[re.Match[bytes]] | None = re.finditer(b"""
	((?=\xFF\xD8.+\x4A\x46\x49\x46).+?(?<=\xFF\xD9))| # JFIF (Group 1)
	(\xFF) # Test (Group 2)
	""", Bytes, re.DOTALL + re.VERBOSE);
	Log.Awaited().OK();


	Offset: int = 0;
	def Write_Unknown(Start: int) -> None:
		if (Start - Offset == 0): return;
		Log.Info(f"Writing unknown hex of {Start} bytes in size...");
		with open(f"Extracted/{F.replace(".molru", "")}/0x{Offset}-0x{Start}.hex", "w+b") as IO: IO.write(Bytes[Offset:Start]);

	def Found(Indexes: tuple[int, int]) -> bool: return False if (Indexes == (-1, -1)) else True;
	for Match in Extract:
		if (Found(Match.span(1))): # JFIF
			Start: int = Match.span(0)[0]; End: int = Match.span(0)[1];
			Log.Info(f"Found JFIF of {End - Start} Bytes in size at 0x{Start}-0x{End}");
			with open(f"Extracted/{F.replace(".molru", "")}/0x{Start}-0x{End}.jpg", "w+b") as IO: IO.write(Bytes[Start:End]);
			Write_Unknown(Start);
			Offset = End;

		if (Found(Match.span(2))):
			#Log.Debug(f"Found TERMINATOR at 0x{Match.span(0)[0]}-0x{Match.span(0)[1]}");
			pass;

	Log.Info(f"Finished Processing \"{F}\" in {Time.Elapsed_String(Time.Get_Unix(True) - Molru_Init, " ", Show_Until=-3)}");










def Kozeki(Extractor: str) -> None:
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










def Help():
	print("Usage");
	print("");
	print("python3 ./TSN_Kozeki.py [options]");
	print("python3 ./TSN_Kozeki.py -d --extractor slow");
	print("");
	print("A TSNA based tool to extract Blue Archive's .molru PC files, a cursed file type given to us who like to poke around a bit too much.");
	print("");
	print("Options");
	print("\t-h\t\t\t= Print usage information and exit.");
	print("\t-d\t\t\t= Enable Debug Mode.");
	print("");
	print("\t--extractor <extractor>\t= Enforce an extraction method. Available ones are: 'regex'. (default: 'regex').");



if (__name__ == '__main__'):
	Log.Stateless(f"Kozeki {Kozeki_Branch} - {Kozeki_Version} © Ascellayn (2025) // TSN License 2.1 - Universal");
	Log.Stateless("Kozeki is a TSNA based tool to extract Blue Archive's .molru PC files, a cursed file type given to us who like to poke around a bit too much.\n");
	global Debug_Mode; Debug_Mode: bool;
	TSN_Abstracter.Require_Version((5,4,0));

	# Argument Configuration
	Extractor: str = "regex";

	if (len(sys.argv) > 1):
		sys.argv.pop(0); # Useless
		if ("-h" in sys.argv):
			Help(); exit();

		try:
			for Argument in sys.argv:
				match Argument:
					case "--extractor": Word_Filename = sys.argv.pop(1);
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

	Kozeki(Extractor);

else: TSN_Abstracter.Require_Version((5,4,0));
# ↑ In case someone wants to import this file and use its extractors outside of the Kozeki script.
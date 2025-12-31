from TSN_Abstracter import *;
import sys;

Log.Clear();
Kozeki_Version: str = "v0.2.1";
Kozeki_Branch: str = "Azure";



def Extract_Slow(F: str) -> None:
	""" Byte by Byte extraction, reveals data that is currently unknown by TSN_Kozeki  
	Warning: Painfully slow and to not be used! """
	Molru_Init: int = Time.Get_Unix(True);
	File.Path_Require(f"Extracted/{F}");
	File.Path_Require(f"Unknown/{F}");

	with open(F, "r+b") as Molru:
		Bytes: bytes = Molru.read();
		Bytes_Total: int = len(Bytes) - 1;

	# Special Bytes
	OxFF: bool = False;
	JPEG_Start: bool = False;
	JPEG_End: bool = False;

	JPEG_Data: bool = False;



	# Buffers
	Buffer_JPEG: bytes = b"";
	Buffer_Unknown: bytes = b"";



	Byte_Code: int; Byte: bytes;
	for Index, Byte_Code in enumerate(Bytes):
		Byte = bytes([Byte_Code]);

		# JPEG Detection
		JPEG_Start = True if (Byte == b"\xD8") else False;
		JPEG_End = True if (Byte == b"\xD9") else False;


			# Finish JPEG
		if (OxFF and JPEG_End):
			Buffer_JPEG += Byte; JPEG_Data = False;
			with open(f"Extracted/{F}/{Index}.jpg", "w+b") as JPEG: JPEG.write(Buffer_JPEG); Buffer_JPEG = b"";
			Log.Stateless(f"Writing JPEG → {Index}/{Bytes_Total} ({round((Index/Bytes_Total)*100, 2)}%) Bytes");
			JPEG_Data = False;

		elif (JPEG_Data): Buffer_JPEG += Byte;
		elif (OxFF and JPEG_Start):
			JPEG_Data = True; Buffer_JPEG += b"\xFF\xD8";

			if (len(Buffer_Unknown) > 1):
				Buffer_Unknown[:-1];
				with open(f"Unknown/{F}/{Index}.hex", "w+b") as Hex: Hex.write(Buffer_Unknown);
				Log.Stateless(f"Writing Hex → {Index}/{Bytes_Total} ({round((Index/Bytes_Total)*100, 2)}%) Bytes");
			Buffer_Unknown = b"";


		# Reset Magic and checks if random new file type in Molru
		if (not JPEG_Data and not OxFF): Buffer_Unknown += Byte;
		OxFF = True if (Byte == b"\xFF") else False;


	Log.Info(f"Finished Processing \"{F}\" in {Time.Elapsed_String(Time.Get_Unix(True) - Molru_Init, " ", Show_Until=-3)}");





def Extract_Deep(F: str) -> None:
	""" Byte by Byte extraction, may reveal data that is currently unknown by TSN_Kozeki """
	Molru_Init: int = Time.Get_Unix(True);
	File.Path_Require(f"Unknown/{F}");
	File.Path_Require(f"Extracted/{F}");

	with open(F, "r+b") as Molru: Bytes: bytes = Molru.read();
	Offset: int = 0;

	while (Bytes.find(b"\xFF\xD8") != -1):
		JPEG_Start: int = Bytes.find(b"\xFF\xD8");
		JPEG_End: int = Bytes.find(b"\xFF\xD9") + 2;
		if (JPEG_End == -1): break;

		if (JPEG_Start != 0):
			with open(f"Unknown/{F}/0x{Offset}-0x{Offset + JPEG_Start}.hex", "w+b") as Hex: Hex.write(Bytes[:JPEG_Start]);
			Log.Info("Unknown data found before JPEG File, writing.");

		with open(f"Extracted/{F}/0x{Offset + JPEG_Start}-0x{Offset + JPEG_End}.jpg", "w+b") as Hex: Hex.write(Bytes[JPEG_Start:JPEG_End]);
		Offset += JPEG_End + 2; Bytes = Bytes[JPEG_End:];
		
		Log.Info(f"JPEG File of {JPEG_End - JPEG_Start} bytes in size written. {len(Bytes)} Bytes left to process.");
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
						case "slow": Extract_Slow(f"{Path}{File}");
						case "deep": Extract_Deep(f"{Path}{File}");
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
	print("\t--extractor <extractor>\t= Enforce an extraction method. Available ones are: 'deep', 'slow'. (default: 'deep').");



if (__name__ == '__main__'):
	global Debug_Mode; Debug_Mode: bool;
	TSN_Abstracter.Require_Version((5,4,0));
	Debug_Mode = True; # Don't forget to remove this u idiot

	# Argument Configuration
	Extractor: str = "deep";

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
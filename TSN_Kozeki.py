from TSN_Abstracter import *;

Log.Clear();
File.Path_Require("Unknown");
File.Path_Require("Extracted");










def Extract_Slow(F: str) -> None:
	""" Byte by Byte extraction, reveals data that is currently unknown by TSN_Kozeki  
	Warning: Painfully slow and to not be used! """
	Molru_Init: int = Time.Get_Unix(True);
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
			with open(f"Extracted/{Index}.jpg", "w+b") as JPEG: JPEG.write(Buffer_JPEG); Buffer_JPEG = b"";
			Log.Stateless(f"Writing JPEG → {Index}/{Bytes_Total} ({round((Index/Bytes_Total)*100, 2)}%) Bytes");
			JPEG_Data = False;

		elif (JPEG_Data): Buffer_JPEG += Byte;
		elif (OxFF and JPEG_Start):
			JPEG_Data = True; Buffer_JPEG += b"\xFF\xD8";

			if (len(Buffer_Unknown) > 1):
				Buffer_Unknown[:-1];
				with open(f"Unknown/{Index}.hex", "w+b") as Hex: Hex.write(Buffer_Unknown);
				Log.Stateless(f"Writing Hex → {Index}/{Bytes_Total} ({round((Index/Bytes_Total)*100, 2)}%) Bytes");
			Buffer_Unknown = b"";


		# Reset Magic and checks if random new file type in Molru
		if (not JPEG_Data and not OxFF): Buffer_Unknown += Byte;
		OxFF = True if (Byte == b"\xFF") else False;


	Log.Info(f"Finished Processing \"{F}\" in {Time.Elapsed_String(Time.Get_Unix(True) - Molru_Init, " ", Show_Until=-3)}");





def Extract_Deep(F: str) -> None:
	""" Byte by Byte extraction, may reveal data that is currently unknown by TSN_Kozeki """
	Molru_Init: int = Time.Get_Unix(True);

	with open(F, "r+b") as Molru: Bytes: bytes = Molru.read();
	Offset: int = 0;

	while (Bytes.find(b"\xFF\xD8") != -1):
		JPEG_Start: int = Bytes.find(b"\xFF\xD8");
		JPEG_End: int = Bytes.find(b"\xFF\xD9") + 2;
		if (JPEG_End == -1): break;

		if (JPEG_Start != 0):
			with open(f"Unknown/0x{Offset}-0x{Offset + JPEG_Start}.hex", "w+b") as Hex: Hex.write(Bytes[:JPEG_Start]);
			Log.Info("Unknown data found before JPEG File, writing.");
	
		with open(f"Extracted/0x{Offset + JPEG_Start}-0x{Offset + JPEG_End}.jpg", "w+b") as Hex: Hex.write(Bytes[JPEG_Start:JPEG_End]);
		Offset += JPEG_End + 2; Bytes = Bytes[JPEG_End:];
		
		Log.Info(f"JPEG File of {JPEG_End - JPEG_Start} bytes in size written. {len(Bytes)} Bytes left to process.");
	Log.Info(f"Finished Processing \"{F}\" in {Time.Elapsed_String(Time.Get_Unix(True) - Molru_Init, " ", Show_Until=-3)}");

Extract_Deep("01_Background.molru");
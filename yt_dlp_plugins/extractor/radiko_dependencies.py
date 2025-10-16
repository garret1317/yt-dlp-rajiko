# Bundle importing code Copyright (c) 2021-2022 Grub4K, from yt-dont-lock-p.
# https://github.com/Grub4K/yt-dont-lock-p/blob/ff3b6e1d42ce8584153ae27544d2c05b50ab5954/yt_dlp_plugins/postprocessor/yt_dont_lock_p/__init__.py#L23-L46
# Used under 0BSD with permission

# https://discord.com/channels/807245652072857610/1112613156934668338/1416816007732920430 (yt-dlp discord server, https://discord.gg/H5MNcFW63r )
# [17:00] garret1317: @Grub4K can i pinch your MIT-licensed dependency bundling code to use in my 0BSD-licensed plugin?
# I will credit of course but i can't require that anyone else does the same
# (Any response to this message will be considered a written consent or refusal of the request)
# [17:04] Grub4K: Feel free to use that part under 0BSD
# [17:05] garret1317: 👍 cheers

try:
	import protobug
except ImportError:
	import sys
	from pathlib import Path

	# Try importing from zip file bundle
	search_path = str(Path(__file__).parent.parent)
	sys.path.append(search_path)
	try:
		import protobug
	except ImportError:
		protobug = None
	except Exception:
		protobug = None

	finally:
		sys.path.remove(search_path)

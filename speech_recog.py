import test01,speech_to_isl
import sys
""""
ytdownload.downloader("call accross")
test01.generateclip("call accross")

s=speech_to_isl.isl(sys.argv[1])

s=speech_to_isl.isl("I am reading a story")
"""
try:
	s = speech_to_isl.isl(sys.argv[1])
	s = s.strip()
	print("[speech_recog] starting test01.generateclip")
	test01.generateclip(s)
	print("[speech_recog] finished test01.generateclip")
	print("done!")
except Exception as e:
	# Fallback: skip Stanford/NLP step and build video directly from words/letters
	s = sys.argv[1]
	s = s.strip()
	try:
		print("[speech_recog] fallback starting test01.generateclip")
		test01.generateclip(s)
		print("[speech_recog] fallback finished test01.generateclip")
		# Print ISL-like output so server can parse it
		print("ISL:{" + s + "}")
		print("done!")
		sys.exit(0)
	except Exception as e2:
		print(e)
		print(e2)
		sys.exit(1)

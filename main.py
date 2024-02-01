import base64
import os

from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from PIL import Image, ImageFont, ImageChops
import sys
from Crypto.PublicKey import RSA
from PIL import ImageDraw


def generatePkPubKey(path="keys/"):
	os.mkdir(path)
	key = RSA.generate(4096)
	f = open("keys/private.pem", "wb")
	f.write(key.exportKey("PEM"))
	f.close()
	f = open("keys/public.pem", "wb")
	f.write(key.publickey().exportKey("PEM"))
	f.close()


def signMessage(message: bytes):
	f = open("keys/private.pem", "rb")
	key = RSA.importKey(f.read())
	f.close()
	h = SHA256.new(message)
	signature = PKCS1_v1_5.new(key).sign(h)
	return base64.b64encode(signature).decode()


def checkSignature(message: bytes, signature: bytes):
	shouldBe = signMessage(message)
	return shouldBe == signature


def invertHalf(inp, outp):
	img = Image.open(inp)
	m = img.height // 2
	pixels = img.load()

	for y in range(m, img.height):
		for x in range(0, img.width):
			r, g, b = pixels[x, y]
			r = r ^ 0b11111111
			g = g ^ 0b11111111
			b = b ^ 0b11111111
			pixels[x, y] = r, g, b
	img.save(outp)


def messageToBits(message: str):
	bits = []
	ml = len(message)
	countEncode = 0
	while ml > 255:
		bits.extend([1 for _ in range(8)])
		ml >>= 8
		countEncode += 1
	ml = len(message)
	bits.extend([int(b) for b in bin(ml)[2:].zfill(8 * (countEncode + 1))])
	for char in message:
		bits.extend([int(b) for b in bin(ord(char))[2:].zfill(8)])
	return bits


def getLength(bits):
	binToReadSize = 0
	while bits[binToReadSize*8:(binToReadSize+1)*8] == [1 for _ in range(8)]:
		binToReadSize += 1
	start = (binToReadSize * 2 + 1) * 8
	size = int("".join([str(b) for b in bits[binToReadSize*8:start]]), 2)
	return start, size


def bitsToMessage(bits):
	message = ""
	start, size = getLength(bits)
	for i in range(start, start + size * 8, 8):
		bi = bits[i:i+8]
		char = chr(int("".join([str(b) for b in bi]), 2))
		message += char
	return message


def storeMessage(inp: str, outp: str, message: str, fromPos=0, jumpBackAfterXChars=-1):
	img = Image.open(inp)
	pixels = img.load()
	message = messageToBits(message)
	if len(message) > ((img.width * img.height - fromPos) if jumpBackAfterXChars == -1 else (jumpBackAfterXChars * (img.height-1) - fromPos)):
		raise ValueError("Message is too long to fit in image")
	for y in range(fromPos//img.width, img.height):
		jumpBack = 0
		for x in range(0, img.width):
			if len(message) == 0:
				break
			if y*img.width + x < fromPos:
				continue
			if jumpBackAfterXChars != -1:
				if fromPos % img.width > x:
					continue
				if jumpBack == jumpBackAfterXChars:
					break
				jumpBack += 1
			# replace last bit of red pixel with message bit
			pixels[x, y] = pixels[x, y][0] & 0b11111110 | message[0], pixels[x, y][1], pixels[x, y][2]
			# pixels[x, y] = 0, 255 if message[0] else 0, 0
			message = message[1:]
	img.save(outp)


def recoverMessage(inp):
	img1 = Image.open(inp)
	pixels1 = img1.load()
	message = []
	for y in range(img1.height):
		for x in range(img1.width):
			message.append(pixels1[x, y][0] & 0b00000001)
	return message


def setupDiplomeBkg(path):
	"""
	The goal is to switch the 684*8 last pixels's red LSB value to 0
	:param path:
	:return:
	"""
	img = Image.open(path)
	pixels = img.load()
	size = img.height * img.width
	toEdit = size - 684 * 8
	for y in range(img.height):
		if y*img.width < toEdit:
			continue
		for x in range(img.width):
			if y*img.width + x < toEdit:
				continue
			pixels[x, y] = pixels[x, y][0] & 0b11111110, pixels[x, y][1], pixels[x, y][2]
	img.save(path[:-4] + "_prepared.png")


def putClearInformations(path, name, surname, birthDate, obtentionDate, diplomaNumber, diplomaName, diplomaFormation, mean, mention):
	img = Image.open(path)
	draw = ImageDraw.Draw(img)
	univFont = ImageFont.truetype("fonts/Roboto-Bold.ttf", 90)
	topFont = ImageFont.truetype("fonts/Roboto-Bold.ttf", 50)
	titleFont = ImageFont.truetype("fonts/Roboto-Bold.ttf", 40)
	textFont = ImageFont.truetype("fonts/Roboto-Regular.ttf", 30)
	smallFont = ImageFont.truetype("fonts/Roboto-Regular.ttf", 20)
	"""Infos à placer :
	diplomaName -> Centré à hauteur 200 police topFont couleur très claire
	"Diplôme de l'université" -> Centré à hauteur 180 police topFont
	"Formation " + diplomaFormation -> Centré à hauteur 250 police titleFont
	"Délivré le " + obtentionDate + " à l'étudiant :" -> Centré à hauteur 300 police textFont
	name + " " + surname -> Centré à hauteur 350 police textFont
	"Né(e) le " + birthDate -> Centré à hauteur 400 police textFont
	"avec la mention " + mention + " pour une moyenne de " + mean -> Centré à hauteur 450 police textFont
	"N° de diplôme : " + diplomaNumber -> Vers la droite à hauteur 520 police smallFont
	"""
	# Exemple de ligne à écrire :
	# draw.text((img.width // 2 - topFont.getlength("Diplôme de l'université") // 2, 180), "Diplôme de l'université", "black", topFont)
	draw.text((img.width // 2 - univFont.getlength(diplomaName) // 2, 200), diplomaName, "#f3f3f3", univFont)
	draw.text((img.width // 2 - topFont.getlength("Diplôme de l'université") // 2, 180), "Diplôme de l'université", "black", topFont)
	draw.text((img.width // 2 - titleFont.getlength("Formation " + diplomaFormation) // 2, 250), "Formation " + diplomaFormation, "black", titleFont)
	draw.text((img.width // 2 - textFont.getlength("Délivré le " + obtentionDate + " à l'étudiant :") // 2, 300), "Délivré le " + obtentionDate + " à l'étudiant :", "black", textFont)
	draw.text((img.width // 2 - textFont.getlength(name + " " + surname) // 2, 350), name + " " + surname, "black", textFont)
	draw.text((img.width // 2 - textFont.getlength("Né(e) le " + birthDate) // 2, 400), "Né(e) le " + birthDate, "black", textFont)
	draw.text((img.width // 2 - textFont.getlength("avec la mention " + mention + " pour une moyenne de " + mean) // 2, 450), "avec la mention " + mention + " pour une moyenne de " + mean, "black", textFont)
	draw.text((img.width - smallFont.getlength("N° de diplôme : " + diplomaNumber) - 130, 520), "N° de diplôme : " + diplomaNumber, "black", smallFont)
	img.save("tmp/" + name + "_" + surname + "_" + diplomaName + ".png")
	return "tmp/" + name + "_" + surname + "_" + diplomaName + ".png"


def putHiddenInformations(base, diplomaNumber: str, name: str, surname: str, notes: list[float], coefficients: list[int], codes: list[str]):
	"""
	Infos à cacher :
	- Numéro de diplôme
	- Notes / Coefficients de chaque matière avec le code de la matière
	- Signature contenant ces informations
	- Clé publique de la signature
	- Nom / Prénom

	La clé publique de la signature sera cachée à partir de la ligne 20 de l'image
	La signature sera cachée à partir du début de l'image
	Le numéro de diplôme sera caché dans un carré de 8x10 pixels en haut à droite de l'image
	Le nom / prénom puis les notes / coefficients / codes des matières seront cachés à partir de la ligne 150 de l'image, suivi de la moyenne (puis du numéro de diplôme afin de pouvoir récupérer les informations)
	"""
	signature = signMessage((diplomaNumber + str(notes) + str(coefficients) + name + surname).encode())
	img = Image.open(base)
	pubKey = open("keys/public.pem", "rb").read()
	# Stringify the public key
	pubKey = pubKey.decode("ascii")
	basePath = base[:-4]
	storeMessage(base, basePath + "_generated.png", diplomaNumber, img.width - 8, 8)
	storeMessage(basePath + "_generated.png", basePath + "_generated.png", "--".join([name, surname] + [f"{notes[i]:.2f}-{coefficients[i]}-{codes[i]}" for i in range(len(notes))]+[f"{calcMean(notes,coefficients):.2f}"])+diplomaNumber, 150*img.width)
	storeMessage(basePath + "_generated.png", basePath + "_generated.png", signature, img.width*img.height - 687*8)
	storeMessage(basePath + "_generated.png", basePath + "_generated.png", pubKey, img.width*20)
	return basePath + "_generated.png"


def putAllInformations(base, name, surname, birthDate, obtentionDate, diplomaNumber, diplomaName, diplomaFormation, mean, mention, notes, coefficients, codes):
	genName = putClearInformations(base, name, surname, birthDate, obtentionDate, diplomaNumber, diplomaName, diplomaFormation, mean, mention)
	lastGenName = putHiddenInformations(genName, diplomaNumber, name, surname, notes, coefficients, codes)
	# Move the generated file to "generated/name_surname_diplomaNumber.png"
	if os.path.exists("generated/" + name + "_" + surname + "_" + diplomaNumber + ".png"):
		os.remove("generated/" + name + "_" + surname + "_" + diplomaNumber + ".png")
	os.rename(lastGenName, "generated/" + name + "_" + surname + "_" + diplomaNumber + ".png")
	os.remove(genName)
	return "generated/" + name + "_" + surname + "_" + diplomaNumber + ".png"


def calcMean(notes, coefficients):
	return sum([notes[i]*coefficients[i] for i in range(len(notes))])/sum(coefficients)


def checkDiplome(path):
	# Get the hidden informations
	fullHiddenMessage = recoverMessage(path)
	imgDimensions = Image.open(path).size
	# Get the signature
	signature = bitsToMessage(fullHiddenMessage[-687*8:])
	# Get the public key
	pubKey = bitsToMessage(fullHiddenMessage[20*imgDimensions[0]:20*imgDimensions[0]+6416])
	# Check if the public key is valid
	if pubKey != open("keys/public.pem", "rb").read().decode("ascii"):
		raise Exception("Invalid public key")
	# Get the diploma number
	diplomaNumber = []
	for i in range(11):
		diplomaNumber += fullHiddenMessage[imgDimensions[0]-8+i*imgDimensions[0]:(i+1)*imgDimensions[0]]
	diplomaNumber = bitsToMessage(diplomaNumber)
	# Get the notes / coefficients / codes
	i = 150*imgDimensions[0]
	v = bitsToMessage(fullHiddenMessage[i:])
	values = v.split("--")
	notes, coefficients, codes = zip(*[tuple(map(str, value.split("-"))) for value in values[2:-1]])
	name, surname = values[0], values[1]
	notes = list(map(float, notes))
	coefficients = list(map(int, coefficients))
	# Get the mean
	mean = float(values[-1][:len(values[-1])-len(diplomaNumber)])
	# Check if the mean is correct
	if abs(mean - calcMean(notes, coefficients)) > 0.01:
		raise Exception(f"Invalid mean : {mean} != {sum(notes)/sum(coefficients)}")
	# Check if the signature is valid
	if not checkSignature((diplomaNumber + str(notes) + str(coefficients) + name + surname).encode(), signature):
		raise Exception("Invalid signature")
	return "Diploma is valid hiddenwise", diplomaNumber, name, surname, [(codes[i], notes[i], coefficients[i]) for i in range(len(notes))], round(mean, 2)


def showDiff(path1, path2, path3):
	img1 = Image.open(path1)
	img2 = Image.open(path2)
	diff = ImageChops.difference(img1, img2)
	for x in range(diff.width):
		for y in range(diff.height):
			if diff.getpixel((x, y)) != (0, 0, 0, 0) and diff.getpixel((x, y)) != (0, 0, 0):
				diff.putpixel((x, y), (255, 0, 0))
			else:
				diff.putpixel((x, y), tuple([v//2 for v in img1.getpixel((x, y))]))
	diff.save(path3)


def main(command, args):
	if command == "invert_half":
		invertHalf(args[0], args[1])
	elif command == "storeMessage":
		storeMessage(args[0], args[1], args[2], args[3], args[4])
	elif command == "recoverMessage":
		print(bitsToMessage(recoverMessage(args[0])))
	elif command == "setupKeys":
		generatePkPubKey(args[0])
	elif command == "sign":
		print(signMessage(args[0].encode()))
	elif command == "checkSignature":
		print(checkSignature(args[0].encode(), args[1].encode()))
	elif command == "setupDiplomeBkg":
		setupDiplomeBkg(args[0])
	elif command == "putClearInformations":
		putClearInformations(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
	elif command == "putHiddenInformations":
		notes = [float(note) for note in args[4].split("-")]
		coefficients = [int(coefficient) for coefficient in args[5].split("-")]
		codes = args[6].split("-")
		putHiddenInformations(args[0], args[1], args[2], args[3], notes, coefficients, codes)
	elif command == "showDiff":
		showDiff(args[0], args[1], args[2])
	elif command == "putAllInformations":
		notes = [float(note) for note in args[10].split("-")]
		coefficients = [int(coefficient) for coefficient in args[11].split("-")]
		codes = args[12].split("-")
		putAllInformations(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9], notes, coefficients, codes)
	elif command == "checkDiplome":
		print(checkDiplome(args[0]))
	elif command == "help":
		print("Available commands :")
		print("help")
		print("invert_half <input> <output>")
		print("storeMessage <input> <output> <message> <fromPos> <jumpBackAfterXChars>")
		print("recoverMessage <input>")
		print("setupKeys <name>")
		print("sign <message>")
		print("checkSignature <message> <signature>")
		print("setupDiplomeBkg <input>")
		print("putClearInformations <input> <name> <surname> <birthDate> <obtentionDate> <diplomaNumber> <diplomaName> <diplomaFormation> <mean> <mention>")
		print("putHiddenInformations <input> <diplomaNumber> <name> <surname> <notes> <coefficients> <codes>")
		print("showDiff <input1> <input2> <output>")
		print("putAllInformations <input> <name> <surname> <birthDate> <obtentionDate> <diplomaNumber> <diplomaName> <diplomaFormation> <mean> <mention> <notes> <coefficients> <codes>")
		print("checkDiplome <input>")


if __name__ == "__main__":
	# sys.argv = [sys.argv[0]] + ["setupDiplomeBkg", ".\\templates\\diplome-BG.png"]
	# sys.argv = [sys.argv[0]] + ["showDiff", '.\\templates\\diplome-BG.png', '.\\templates\\diplome-BG_prepared.png', '.\\tmp\\checkDiff.png']
	# sys.argv = [sys.argv[0]] + ["putClearInformations", '.\\templates\\diplome-BG_prepared.png', 'HYVERNAT', 'Pierre', 'jour de sa naissance', '16/01/2024', '84za5zs21d', 'NIHCAMCURT', 'Informatique', '18.74', 'TB']
	# sys.argv = [sys.argv[0]] + ["showDiff", '.\\templates\\diplome-BG.png', '.\\tmp\\HYVERNAT_Pierre_NIHCAMCURT.png', '.\\tmp\\checkDiff.png']
	# sys.argv = [sys.argv[0]] + ["putHiddenInformations", '.\\templates\\diplome-BG.png', 'HYVERNAT', 'Pierre', '84za5zs21d', '20-19-18', '2-13-8', 'INFO907-INFO908-INFO909']
	# sys.argv = [sys.argv[0]] + ["showDiff", '.\\templates\\diplome-BG.png', '.\\tmp\\HYVERNAT_Pierre_NIHCAMCURT_allInfos.png', '.\\tmp\\checkDiff.png']
	sys.argv = [sys.argv[0]] + ["putAllInformations", '.\\templates\\diplome-BG_prepared.png', 'HYVERNAT', 'Pierre', 'jour de sa naissance', '16/01/2024', '84za5zs21d', 'NIHCAMCURT', 'Informatique', '18.74', 'TB', '20-19-18', '2-13-8', 'INFO907-INFO908-INFO909']
	# sys.argv = [sys.argv[0]] + ["showDiff", '.\\templates\\diplome-BG.png', '.\\generated\\HYVERNAT_Pierre_84za5zs21d.png', '.\\tmp\\checkDiff.png']
	sys.argv = [sys.argv[0]] + ["checkDiplome", '.\\generated\\HYVERNAT_Pierre_84za5zs21d.png']
	cmd = sys.argv[1]
	main(cmd, sys.argv[2:])

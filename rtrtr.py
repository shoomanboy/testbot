import googletrans
from googletrans import Translator



slovo = input()
dest=input()
translator = Translator()
perevod = translator.translate(slovo, dest=dest)
print(perevod.text)
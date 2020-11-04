from telegram import Update, ReplyKeyboardRemove,ReplyKeyboardMarkup
from telegram.ext import Updater,CallbackContext,Filters,MessageHandler,CommandHandler,ConversationHandler
import googletrans
from googletrans import Translator
from mongodb import mdb
import MongoDB_settingsVlad
from MongoDB_settingsVlad import TG_Token

button_translate="translator"
button_help="/help"
button_menu="/menu"
japan_rus="->rus"
rus_japan="->japan"
spisok_slov="список переведенных слов"
button_end="/end"
src=0   # Исходный язык
dest=0  # Язык назначения

def dontknow(update: Update,
             context: CallbackContext):  # Если непривально введена команда,то будет отправляться пользователю данная команда
    update.message.reply_text(text='Я вас не понимаю,нажмите на команду')




def message_handler(update:Update,context:CallbackContext):
    my_keyboard=ReplyKeyboardMarkup([[button_translate],[button_help]])
    update.message.reply_text(
        text="Привет %s, давай общаться\n Нажми на одну из кнопок." % (format(update.message.chat.first_name)),
        reply_markup=my_keyboard)
    id=update.message.chat.id
    user=mdb.find_one({"_id":id})
    if user==None:
        mdb.insert_one({"_id":id})
    return "spisok comand"

def spisok_comand(update:Update,context:CallbackContext):
    my_keyboard=ReplyKeyboardMarkup([[button_translate],[button_help],[button_end]])

    if update.message.text==button_translate:
        return spisok_translator(update=update,context=context)
    if update.message.text==button_menu:
        return update.message.reply_text(text="Вы сейчас в главном меню",reply_markup=my_keyboard)
    if update.message.text==button_help:
        update.message.reply_text(text="С помощью команды 'translator' вы поподете в переводчик\nКоманда'/menu' вас перенаправит в главное меню",reply_markup=my_keyboard)
        return "spisok comand"
    if update.message.text==button_end:
        update.message.reply_text(text="До скорой встречий,чтобы я снова заработал напиши команду\n'/start'")
        return ConversationHandler.END

def spisok_translator(update:Update,context:CallbackContext):
    if update.message.text==button_translate:
        translator_keyboard = ReplyKeyboardMarkup([[japan_rus], [rus_japan], [spisok_slov],[button_menu]])
        update.message.reply_text(text="Выберите действие", reply_markup=translator_keyboard)
        return "handler"
    if update.message.text==button_menu:
        my_keyboard = ReplyKeyboardMarkup([[button_translate], [button_help],[button_end]])
        update.message.reply_text(text="Вы сейчас в главном меню",reply_markup=my_keyboard)
        return "spisok comand"

def handler(update:Update,context:CallbackContext):
    global dest
    id = update.message.chat.id
    if update.message.text == rus_japan:
        dest = "ja" # dest-язык назначения
        update.message.reply_text(text="Введите слово для перевода на японский!",reply_markup=ReplyKeyboardRemove())
        return "translator_handler"

    if update.message.text==japan_rus:
        dest="ru"   # dest-язык назначения
        update.message.reply_text(text="Введите слово для перевода на русский!",reply_markup=ReplyKeyboardRemove())
        return "translator_handler"

    if update.message.text==spisok_slov and mdb.find_one({"_id":id,"translator":{"$exists":True}})!=None:
        words=mdb.find_one({"_id":id})
        for i,item in enumerate(words["translator"]["ru_words"]):
            words["translator"]["ru_words"][i]+=" -%s"%words["translator"]["ja_words"][i]
        update.message.reply_text("\n".join(words["translator"]["ru_words"]))
    elif update.message.text==spisok_slov and mdb.find_one({"_id":id,"translator":{"$exists":True}})==None:
        update.message.reply_text(text="нет переведенных слов")
    if update.message.text==button_menu:
        return spisok_translator(update=update,context=context)


def translator_handler(update:Update,context:CallbackContext):
    global dest
    translator_keyboard = ReplyKeyboardMarkup([[japan_rus], [rus_japan], [spisok_slov], [button_menu]])
    id=update.message.chat.id
    slovo=update.message.text
    translator=Translator()
    perevod=translator.translate(slovo,dest=dest)
    if dest=="ja":
        result = mdb.update_one({"_id": id},{"$push": {"translator.ru_words": slovo, "translator.ja_words": perevod.text}})
        update.message.reply_text(
            text="Перевод: %s-%s\nПроизношение: %s" % (slovo, perevod.text, perevod.pronunciation))
    update.message.reply_text(text="Выберите действие", reply_markup=translator_keyboard)
    if dest=="ru":
        result = mdb.update_one({"_id": id}, {"$push": {"translator.ru_words": perevod.text, "translator.ja_words": slovo}})
        update.message.reply_text(text="Перевод: %s-%s" % (slovo, perevod.text))
    return "handler"


def main():
    print("Бот переводчик запущен!")
    updater=Updater(
        token=TG_Token,
        use_context=True,
    )
    start_handler=updater.dispatcher.add_handler(
        ConversationHandler(entry_points=[CommandHandler("start",message_handler)],
                            states={
                                "spisok comand":[MessageHandler(Filters.regex("translator|/menu|/help|/end"),spisok_comand)],
                                "translator":[MessageHandler(Filters.regex("translator|->rus|->japan|список переведенных слов|/menu"),spisok_translator)],
                                "handler":[MessageHandler(Filters.regex("translator|->rus|->japan|список переведенных слов|/menu"),handler)],
                                "translator_handler":[MessageHandler(Filters.all,translator_handler)]
                            },
                            fallbacks=[MessageHandler(Filters.text | Filters.video | Filters.document | Filters.photo,dontknow)]
                            )
    )
    updater.start_polling()
    updater.idle()

if __name__== "__main__":
    main()
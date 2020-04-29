import logging
import os

from sqlalchemy.orm.exc import NoResultFound
from telegram import *
from telegram.ext import *

import config
import core
from core import db_map

logging.basicConfig(handlers=[logging.FileHandler('log.txt', 'w', 'utf-8')],
                    level=logging.INFO,
                    format='[*] %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             parse_mode=ParseMode.MARKDOWN,
                             text="Бот говорит привет!\n"
                                  "\n"
                                  "Узнай что говорит человек фразой:\n"
                                  "`Что говорит имя-человека`\n"
                                  "\n"
                                  "Если неизвестно что он говорит, то скажи мне что он говорит фразой:\n"
                                  "`Имя-человека говорит привет мир`")


def inline(update, context):
    name = update.inline_query.query.lower()
    umf = update.inline_query.from_user

    if not name:
        results = [
            InlineQueryResultArticle(
                id=umf.id,
                title="Введите имя",
                input_message_content=InputTextMessageContent("Введите имя"),
                description="Введите имя")]

        update.inline_query.answer(results, cache_time=1, is_personal=True)

    else:

        session = db_map.Session()
        try:
            say = session. \
                query(db_map.WhoSayTable). \
                filter(db_map.WhoSayTable.name == name).one()

            results = [
                InlineQueryResultArticle(
                    id=umf.id,
                    title=f"Что говорит {name}",
                    input_message_content=InputTextMessageContent("{} говoрит {}".format(name.capitalize(), say.say)),
                    description="{} говoрит {}".format(name.capitalize(), say.say))]

            update.inline_query.answer(results, cache_time=1, is_personal=True)

        except NoResultFound:
            results = [
                InlineQueryResultArticle(
                    id=umf.id,
                    title="Такого имени не найдено",
                    input_message_content=InputTextMessageContent("Такого имени не найдено"),
                    description="Такого имени не найдено")]

            update.inline_query.answer(results, cache_time=1, is_personal=True)


def dump(update, context):
    session = db_map.Session()

    t_dump = session.query(db_map.WhoSayTable).order_by(db_map.WhoSayTable.id).all()
    result = [f"id: {x.id}\nname: {x.name}\nsay: {x.say}" for x in t_dump]
    with open('dump.txt', 'w') as file:
        file.write("\n\n".join(result))

    context.bot.send_document(chat_id=update.message.chat_id,
                              document=open('dump.txt', 'rb'))

    os.remove('dump.txt')


def log(update, context):
    log_file = os.path.abspath('log.txt')
    try:
        context.bot.send_document(chat_id=update.message.chat.id, document=open(log_file, 'rb'))

    except TelegramError:
        update.message.reply_text("File is empty")


def error(update, context):
    print('Update "%s" caused error "%s"', update, context.error)
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    db_map.Base.metadata.create_all(db_map.engine)

    updater = Updater(config.TOKEN, use_context=True)
    dp = updater.dispatcher

    filters = ~Filters.update.edited_message
    admin_filters = ~Filters.update.edited_message & Filters.user(user_id=config.ADMINS)

    # All

    dp.add_handler(CommandHandler('start', start, filters=filters))

    dp.add_handler(CommandHandler('log', log, filters=admin_filters))
    dp.add_handler(CommandHandler('dump', dump, filters=admin_filters))

    dp.add_handler(MessageHandler(filters & Filters.text, core.message.message_core))
    dp.add_handler(InlineQueryHandler(inline))

    # ERROR

    dp.add_error_handler(error)

    updater.start_polling(clean=True)
    updater.idle()


if __name__ == '__main__':
    main()

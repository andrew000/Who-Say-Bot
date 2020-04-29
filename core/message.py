from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import config
from core.db_map import WhoSayTable, Session


def replacer(string: str) -> str:
    for char in ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>',
                 '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']:
        string = string.replace(char, '')

    return string


def get_name(message: list) -> dict:
    if "говорит" in message:
        dictionary = {'name': " ".join(message[:message.index("говорит")]),
                      'say': " ".join(message[(message.index("говорит") + 1):])}
        return dictionary


def message_core(update, context):
    message = replacer(update.message.text).lower().split()
    if len(message) < 2:
        return
    session = Session()

    if message[0:2] == ['что', 'говорит']:
        name = " ".join(message[2:])

        try:
            say = session.query(WhoSayTable). \
                filter(WhoSayTable.name == name).one()

            update.message.reply_text("{} говорит {}".format(name.capitalize(), say.say))

        except NoResultFound:
            update.message.reply_text("Неизвестно что говорит {}".format(name))

        finally:
            session.close()

    else:
        dictionary = get_name(message)
        if not dictionary:
            return
        if dictionary['name'] == '':
            return

        elif dictionary['name'] != '' and dictionary['say'] == '':
            """
            Function to get what NAME is SAYING.
            Example: Андрей говорит
            """
            name = dictionary['name']

            try:
                say = session.query(WhoSayTable). \
                    filter(WhoSayTable.name == name).one()

                update.message.reply_text("{} говорит {}".format(dictionary['name'].capitalize(), say.say))

            except NoResultFound:
                update.message.reply_text("Неизвестно что говорит {}".format(dictionary['name'].capitalize()))

            finally:
                session.close()

        elif dictionary['name'] != '' and dictionary['say'] != '':
            """
            Function to add or update what NAME is SAYING.
            Example: Сука Андрей говорит бля ты уебан...
            """

            if len(dictionary['name']) > config.MAX_LENGTH_NAME:
                update.message.reply_text("Слишком длинное имя")
                return

            if len(dictionary['say']) > config.MAX_LENGTH_SAY:
                update.message.reply_text("{} много говорит".format(dictionary['name'].capitalize()))
                return

            name = dictionary['name']
            say = dictionary['say']

            try:
                data = WhoSayTable(name=name, say=say)
                session.add(data)
                session.commit()
                update.message.reply_text("Добавлено: {} говорит {}".format(dictionary['name'].capitalize(),
                                                                            dictionary['say']))

            except IntegrityError:
                session.rollback()
                try:
                    session.query(WhoSayTable). \
                        filter(WhoSayTable.name == name). \
                        update({WhoSayTable.say: say})
                    session.commit()

                    update.message.reply_text("Изменено: {} говорит {}".format(dictionary['name'].capitalize(),
                                                                               dictionary['say']))

                except Exception as err:
                    session.rollback()
                    update.message.reply_text("Была вызвана ошибка:\n\n{}".format(str(err)))

            finally:
                session.close()

        else:
            session.close()
            return

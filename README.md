Инструкция пользования приложением:
1) Бот работает на локальном хосте, а значит запускать его нужно через ваше IDE, которым вы пользуетесь
2) Для правильной работы бота нужно сделать следующее: 1) Тут на выбор: 1 - написать мне чтобы я дал доступ к базе данных FireBase
                                                                        2 - Создать свою базу данных в FireBase  и заметить файл json в приложении, а также в файле dream_trip_bot.py в 16-17 строчке, а именно # Инициализация Firebase
cred = credentials.Certificate("dreamtrip-29c62-firebase-adminsdk-nr3zi-afa1f51676.json")
firebase_admin.initialize_app(cred) поменять название на ваш файл json
3) Для запуска бота в телеграмме нам потребуется: запустить файл dream_trip_bot.py и также запустить файл app.py( он нам нужен для того чтобы подгружать картинки в самом боте и сама подгрузка проходит через контейнер в docker
( И так как бот работает на хосте, я думаю стоит и создать контейнер тоже( Я так думаю, скажу честно, сам не знаю))) ) )
4) После запуска нужных файлов можно начать пользоваться ботом в телеграмме( Вот тег бота @drmtrip_bot)


Правила пользования ботом
1) Вас приветствует бот и предлагает начать ваше планирование отпуска
2) Нажимаем на кнопку Начать плаинирование и отвечаем на вопросы, которые у вас спрашивает бот
3) В зависимости от ответов бот будет вести себя поразному, если к примеру на вопрос "Согласован ли отпуск с вашим руководством" вы отвечает нет,
бот предложит вам спланировать отпуск потом, когда будет возможность это сделать
4) После ответов на вопросы мы можем просмотреть наш план отпуска в отдельном разделе для этого ( Он так и назвается " Мои планы " )
5) Можно также редактировать план отпуска, если что то вдруг изменилось
6) Кнопка "Напомнить о планирвоании" отвечает за  напоминание о приближении отпуска с обратным отсчетом и с выводом изображением в зависимости от того, какую страну вы выбрали( список стран ограничен )
Если была выбрана "Горная страна" будет показана картинка с горами, если "Морская" страна, то картинка с морем


Напоминалку о планировании я сделал не по тз, объясню почему
Я сделал вывод изображения для проверки работоспособности вывода изображения в боте. Изменить настройки для еженедельного напоминания я не успел ( не уложился в дедлайн)
По факту сделана ежедневная напоминалка, и вроде как она работает корректно( я проверял )


Надеюсь мой проект не сильно засудят)))
Ведь я работал над ботом один,  и скажу честно, много что не знал)) Для себя я узнал много чего нового, и я с полной уверенностью могу сказать, что это точно мне пригодится в будущем))




echo "Написал что-то в консоль"
# Создаём файл с расширением py.
touch -f source.py
# Записываем текст программы, которая записывает сообщение в текстовый файл.
echo "with open('pwned.txt', 'w') as f:" > source.py
echo "    f.write('You have been pwned!')" >> source.py
# Просматриваем текст программы.
cat source.py
# Запускаем программу на языке
python3 source.py

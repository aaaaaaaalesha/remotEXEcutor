echo "Написал что-то в консоль"
touch -f source.py
echo "with open('pwned.txt', 'w') as f:" > source.py
echo "    f.write('You have been pwned!')" >> source.py
cat source.py
python3 source.py

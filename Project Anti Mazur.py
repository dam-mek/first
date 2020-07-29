# -*- coding: utf-8 -*-
import EngineSynonym
import ExtraStaff

# TODO
#  1) проверять регист букв в слове: слова могут быть в прописном шрифте (ТЕКСТ), только первая бука (Текст),
#  никакая (текст)
#  2) преобразование в начальную форму с помощью сайта для начальным форм
#  3) если перед словом стоит хэштег #, то слово не учитывается (#пропусти)
#  4) работа с словоизменением через https://www.translate.ru/grammar/ru-en/
#  5) создание телеграм-бота
#  6) личная база данных с синонимами
#  7) научиться работать с git


def convert_string2list(s):
    converted = []
    alpha = False
    for x in s:
        if x.isalpha() or x == '-':
            if alpha:
                converted[-1] += x
            else:
                converted.append(x)
            alpha = True
        else:
            if alpha or not converted:
                converted.append(x)
            else:
                converted[-1] += x
            alpha = False
    return converted


app = EngineSynonym.SynonymOnline()
app.add_site('https://synonymonline.ru', ExtraStaff.post0, ExtraStaff.convert_link0)
app.add_site('https://sinonim.org', ExtraStaff.post1, ExtraStaff.convert_link1)
# app.add_site('https://ru.wikipedia.org/wiki', ExtraStaff.post_wiki, ExtraStaff.convert_link_wiki)
# app.add_site('https://ru.wikipedia.org/wiki', ExtraStaff.post_wiki, ExtraStaff.convert_link_wiki1)
# app.add_site('https://ru.wikipedia.org/wiki', ExtraStaff.post_wiki, ExtraStaff.convert_link_wiki2)
# app.add_site('https://www.google.com/search?q=', ExtraStaff.post_google, ExtraStaff.convert_link_google)

text = open('input.txt', 'r', encoding='utf-8').read()
# text = 'Одно из которых было уничтожено моментально. А жизнь, то по ходу'
# text = 'моментально жизнь'
# text = 'проезжему, годный, проезжему, годный, проезжему, годный, проезжему, годный'
# text = "днями, часы, сутки"
# text = 'Ёбаный рот этого казино, блядь! Ты кто такой, сука, чтоб это сделать?'
# text = 'зеленее, зелены, ртах, умны, сука, умным, умных, летающий, умнее, умна, умнейший, умнейшую, умнейших, умнейше'
# text = 'летающий, прилетите, унижаемый, будешь, унизь, унизьте, унижая, унизив'
# text = 'летающий'
new_text = ''
# open('output.txt', 'w', encoding='utf-8').write('')
file = open('output.txt', 'w', encoding='utf-8')
list_text = convert_string2list(text)
for i in range(len(list_text)):
    symbols = list_text[i]
    if symbols.isalpha() and len(symbols) > 2:
        print(symbols)
        syn = app.get(symbols)
        if symbols.isupper():
            syn = syn.upper()
        elif symbols.istitle():
            syn = syn.capitalize()
        elif symbols.islower():
            syn = syn.lower()
        print(syn)
        i += 1
        print('\033[32m', str(round((i+1)/(len(list_text)+1)*100)) + '%', i//2, len(list_text))
        print()
        print('\033[47m')
        print('\033[0m')
        added = syn
    else:
        added = symbols
    new_text += added
    file.write(added)


file.close()
print(new_text)



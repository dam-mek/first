import requests
from lxml import html
from random import randint

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/81.0.4044.138 Safari/537.36'
}


class Staff:
    information = {
        'gender': None,
        'amount': None,
        'case': None,
        'rank': None,
        'view': None,
        'time': None,
        'face': None,
        'voice': None,
        'communion': None,
        'adverb': None,
        'short form': None,
        'infinitive': None,
        'imperative': None
    }
    syn_information = {
        'gender': None,
        'amount': None,
        'case': None,
        'rank': None,
        'view': None,
        'time': None,
        'face': None,
        'voice': None,
        'communion': None,
        'adverb': None,
        'short form': None,
        'infinitive': None,
        'imperative': None
    }
    """
        'gender'     — род: 0 — мужской, 1 — женский, 2 — средний
        'amount'     — число: 0 — единственное, 1 — множественное
        'case'       — падеж: 0 — именит., 1 — родит., 2 — дател., 3 — винит., 4 — творит., 5 — предлож.
        'rank'       — степень: 0 — превосходная, 1 — сравнительная
        'view'       — вид: 0 — несовершенный, 1 — совершенный
        'time'       — время: 0 — прошедшее, 1 — настоящее, 2 — будущее
        'face'       — лицо: нужное местоимение (я, ты, он, она, оно, мы, вы, они)
        'voice'      — залог: 0 — действительный, 1 — страдательный
        'communion'  — причастие/деепричастие: 0 — причастие, 1 — деепричастие
        'adverb'     — наречие: True — да
        'short form' — краткая форма: True — да
        'infinitive' — бесконечность: True — да
        'imperative' — повелительное наклонение: True — да
    """

    _ranks = {
        'п': 0,
        'с': 1
    }
    _cases = {
        'и': 0,
        'р': 1,
        'д': 2,
        'в': 3,
        'т': 4,
        'п': 5
    }
    _views = {
        'н': 0,
        'с': 1
    }
    _times = {
        'п': 0,
        'н': 1,
        'б': 2
    }
    _genders = {
        'м': 0,
        'ж': 1,
        'с': 2
    }
    _amounts = {
        'е': 0,
        'м': 1
    }
    _communions = {
        'п': 0,
        'д': 1
    }


class FunctionsOfParsingSyn(Staff):

    def get_syn(self, site):
        gender = site.xpath('//*[@id="fwi_gram1"]/span/p/span[4]')[0].text
        if gender is not None:
            gender = self._genders[gender[0].lower()]
        self.syn_information['gender'] = gender
        sections = site.xpath('//span[@class="sforms_src"]')
        syn_word = None
        for tag in sections[0].getchildren():
            try:
                cls = tag.attrib['class']
            except KeyError:
                continue
            if cls == 'phdr':
                self._parse_syn_phdr(tag)
                for x in self.information:
                    print('\033[45m\033[30m' + x.ljust(11) + '\033[0m\033[33m',
                          self.syn_information[x] if self.syn_information[x] is not None else '')
                print()
                continue
            elif cls == 'wordforms':
                syn_word = self._parse_syn_class_wordforms(tag)
            elif cls == 'transl_form ins':
                syn_word = self._parse_syn_class_transl_form_ins(tag)
            elif cls.split()[0] == 'wfSpan':
                syn_word = self._parse_syn_class_wfspan(tag)
            else:
                print('\033[41mIDONTGIVEFUCK', cls, tag, end='\n\033[0m')

            for state in self.syn_information:
                self.syn_information[state] = None
            self.syn_information['gender'] = gender
            if syn_word is not None:
                return syn_word

    def _parse_syn_phdr(self, tag):
        """
        Заполняет syn_information из phdr существительного или прилагательного.

        Заполняются gender, amount, rank, adverb, short form.

        :param tag: <class 'lxml.html.HtmlElement'>
        :return: None
        """
        phdr = tag.xpath(".//b")[0].text.lower()
        for state in phdr.split(', '):
            # print('state', state)
            if 'род' in state:
                self.syn_information['gender'] = self._genders[state[0]]
            elif 'число' in state:
                self.syn_information['amount'] = self._amounts[state[0]]
            elif 'степень' in state:
                self.syn_information['rank'] = self._ranks[state[0]]
            elif 'наречие' in state:
                self.syn_information['adverb'] = True
            elif 'краткие формы' == state:
                self.syn_information['short form'] = True
            else:
                print('\033[41mIDONTGIVEFUCK', state, tag)
                print('\033[0m')

    def _parse_syn_class_wordforms(self, tag):
        """
        Заполняет syn_information из tag существительного или прилагательного.

        Заполняются gender, case, amount.

        Возвращает True, если удалось найти слово и заполнить information.
        :param tag: <class 'lxml.html.HtmlElement'>
        :return: bool
        """

        for tr in tag.getchildren():
            tds = tr.getchildren()
            if self.syn_information['short form']:
                gender = tds[0].getchildren()[0].text
                maybe_word = tds[1].getchildren()[0].text
                if 'числ' in gender:
                    self.syn_information['amount'] = 1
                else:
                    self.syn_information['gender'] = self._genders[gender.split()[2][0]]
                if self.information == self.syn_information:
                    return maybe_word
                self.syn_information['amount'] = None
                self.syn_information['gender'] = None
            else:
                case = tds[0].text
                if case is None:
                    try:
                        case = tds[0].getchildren()[0].text
                    except IndexError:
                        continue
                    if case is None:
                        continue
                case = case.lower()[0]
                self.syn_information['case'] = self._cases[case]
                for i in range(1, len(tds)):
                    try:
                        for maybe_word in tds[i].getchildren()[0].text.split(' / '):
                            tmp = False
                            if self.syn_information['amount'] is None:
                                tmp = True
                                self.syn_information['amount'] = i - 1
                            if self.information == self.syn_information:
                                return maybe_word
                            if tmp:
                                self.syn_information['amount'] = None
                    except TypeError:
                        continue
                    except AttributeError:
                        continue

    def _parse_syn_verb_phdr(self, tag):
        """
        Заполняет syn_information из tag глагола.

        Заполняются view, time, communion, imperative, infinitive, face, voice, amount (только для повелительного).


        :param tag:
        :return:
        """

        is_used_time = False
        phdr = tag.xpath('.//*[@class="hdr"]/text()')[0].lower()
        for state in phdr.split(', '):
            print(state)
            if 'вид' in state:
                self.syn_information['view'] = self._views[state[0]]
            elif 'время' in state:
                self.syn_information['time'] = self._times[state[0]]
                is_used_time = True
            elif 'причастие' in state:
                self.syn_information['communion'] = self._communions[state[0]]
            elif 'повелительное наклонение' == state:
                self.syn_information['imperative'] = True
            elif 'инфинитив' == state:
                self.syn_information['infinitive'] = True
            else:
                print('\033[41mIDONTGIVEFUCK', state)
                print('\033[0m')
        return is_used_time

    def _parse_syn_class_wfspan(self, tag):
        """
        Заполняет syn_information из tag глагола.

        Заполняются view, time, communion, imperative, infinitive, face, voice, amount (только для повелительного).

        Возвращает True, если удалось найти слово и заполнить syn_information.
        :param tag: <class 'lxml.html.HtmlElement'>
        :return: bool
        """

        is_used_time = self._parse_syn_verb_phdr(tag)

        faces = []
        maybe_words = []
        for line in tag.xpath('.//*[@class="tr_f"]'):
            # print(html.tostring(line, pretty_print=True, encoding='unicode'), end='')
            f = line.xpath('.//f')
            if len(f):
                maybe_word = f[0].text.lower()
                maybe_words.append(maybe_word)
                face = line.xpath('.//value')[0].text
                if face is not None:
                    faces.append(face.lower().strip())
            else:
                maybe_word = line.xpath('.//value')[0].text.lower()
                maybe_words.append(maybe_word)
            #     face = ''
            # if face:
            #     print(end='\033[36m')
            #     print(face)
            # print(end='\033[35m')
            # print(maybe_word)
            # print(end='\033[0m')
        for i in range(len(maybe_words)):
            # if faces:
            #     print('\033[36m' + faces[i], end=' ')
            # print('\033[35m' + maybe_words[i])
            maybe_word = maybe_words[i]
            if faces:
                self.syn_information['face'] = faces[i]
            if self.syn_information['imperative']:
                self.syn_information['amount'] = int(maybe_word.endswith('те'))
            if self.syn_information['communion'] == 0:  # причастие
                if self.syn_information['view'] == 0:  # несовершенный
                    if i == 0:
                        self.syn_information['time'] = 1
                        self.syn_information['voice'] = 0
                    elif i == 1:
                        self.syn_information['time'] = 0
                        self.syn_information['voice'] = 0
                    elif i == 2:
                        self.syn_information['voice'] = 1
                else:  # совершенный
                    self.syn_information['voice'] = i
            if self.information == self.syn_information:
                return maybe_word

            for x in self.information:
                print('\033[45m\033[30m' + x.ljust(11) + '\033[0m\033[33m',
                      str(self.information[x] if self.information[x] is not None else '').ljust(5),
                      self.syn_information[x] if self.syn_information[x] is not None else '')
            print()

            if not is_used_time:
                self.syn_information['time'] = None
            self.syn_information['amount'] = None
            self.syn_information['face'] = None
            self.syn_information['voice'] = None

    def _parse_syn_class_transl_form_ins(self, tag):
        """
        Возвращает True, если удалось найти слово прилагательное.

        :param tag: <class 'lxml.html.HtmlElement'>
        :return: bool
        """

        for maybe_word in tag.getchildren()[0].text.split(' / '):
            if self.syn_information == self.information:
                return maybe_word


class FunctionsOfParsingWord(Staff):

    def parse_sections(self, site, word):
        gender = site.xpath('//*[@id="fwi_gram1"]/span/p/span[4]')[0].text
        if gender is not None:
            gender = self._genders[gender[0].lower()]
        self.information['gender'] = gender
        sections = site.xpath('//span[@class="sforms_src"]')
        success = False
        for tag in sections[0].getchildren():
            try:
                cls = tag.attrib['class']
            except KeyError:
                continue
            if cls == 'phdr':
                self._parse_phdr(tag)
                continue
            elif cls == 'wordforms':
                success = self._parse_class_wordforms(tag, word)
            elif cls == 'transl_form ins':
                success = self._parse_class_transl_form_ins(tag, word)
            elif cls.split()[0] == 'wfSpan':
                success = self._parse_class_wfspan(tag, word)
            else:
                print('\033[41mIDONTGIVEFUCK', cls, tag, end='\n\033[0m')
            if success:
                return True
            for state in self.information:
                self.information[state] = None
            self.information['gender'] = gender
        return False

    def _parse_phdr(self, tag):
        """
        Заполняет information из phdr существительного или прилагательного.

        Заполняются gender, amount, rank, adverb, short form.

        :param tag: <class 'lxml.html.HtmlElement'>
        :return: None
        """

        phdr = tag.xpath(".//b")[0].text.lower()
        for state in phdr.split(', '):
            print('state', state)
            if 'род' in state:
                self.information['gender'] = self._genders[state[0]]
            elif 'число' in state:
                self.information['amount'] = self._amounts[state[0]]
            elif 'степень' in state:
                self.information['rank'] = self._ranks[state[0]]
            elif 'наречие' in state:
                self.information['adverb'] = True
            elif 'краткие формы' == state:
                self.information['short form'] = True
            else:
                print('\033[41mIDONTGIVEFUCK', state, tag)
                print('\033[0m')

    def _parse_class_wordforms(self, tag, word):
        """
        Заполняет information из tag существительного или прилагательного.

        Заполняются gender, case, amount.

        Возвращает True, если удалось найти слово и заполнить information.
        :param tag: <class 'lxml.html.HtmlElement'>
        :param word: string
        :return: bool
        """

        for tr in tag.getchildren():
            tds = tr.getchildren()
            if self.information['short form']:
                gender = tds[0].getchildren()[0].text
                maybe_word = tds[1].getchildren()[0].text
                if maybe_word == word:
                    if 'числ' in gender:
                        self.information['amount'] = 1
                    else:
                        self.information['gender'] = self._genders[gender.split()[2][0]]
                    return True
            else:
                case = tds[0].text
                if case is None:
                    try:
                        case = tds[0].getchildren()[0].text
                    except IndexError:
                        continue
                    if case is None:
                        continue
                case = case.lower()[0]
                for i in range(1, len(tds)):
                    try:
                        for maybe_word in tds[i].getchildren()[0].text.split(' / '):
                            if maybe_word == word:
                                self.information['case'] = self._cases[case]
                                if self.information['amount'] is None:
                                    self.information['amount'] = i - 1
                                return True
                    except TypeError:
                        continue
                    except AttributeError:
                        continue
        return False

    def _parse_class_wfspan(self, tag, word):
        """
        Заполняет information из tag глагола.

        Заполняются view, time, communion, imperative, infinitive, face, voice, amount (только для повелительного).

        Возвращает True, если удалось найти слово и заполнить information.
        :param tag: <class 'lxml.html.HtmlElement'>
        :param word: string
        :return: bool
        """
        phdr = tag.xpath('.//*[@class="hdr"]/text()')[0].lower()
        # print('\033[34mstate:\033[0m', phdr)
        for state in phdr.split(', '):
            if 'вид' in state:
                self.information['view'] = self._views[state[0]]
            elif 'время' in state:
                self.information['time'] = self._times[state[0]]
            elif 'причастие' in state:
                self.information['communion'] = self._communions[state[0]]
            elif 'повелительное наклонение' == state:
                self.information['imperative'] = True
            elif 'инфинитив' == state:
                self.information['infinitive'] = True
            else:
                print('\033[41mIDONTGIVEFUCK', state, tag)
                print('\033[0m')
        # print(html.tostring(tag, pretty_print=True, encoding='unicode'))
        faces = []
        maybe_words = []
        for line in tag.xpath('.//*[@class="tr_f"]'):
            # print(html.tostring(line, pretty_print=True, encoding='unicode'), end='')
            f = line.xpath('.//f')
            if len(f):
                maybe_word = f[0].text.lower()
                maybe_words.append(maybe_word)
                face = line.xpath('.//value')[0].text
                if face is not None:
                    faces.append(face.lower().strip())
            else:
                maybe_word = line.xpath('.//value')[0].text.lower()
                maybe_words.append(maybe_word)
            #     face = ''
            # if face:
            #     print(end='\033[36m')
            #     print(face)
            # print(end='\033[35m')
            # print(maybe_word)
            # print(end='\033[0m')
        for i in range(len(maybe_words)):
            # if faces:
            #     print('\033[36m' + faces[i], end=' ')
            # print('\033[35m' + maybe_words[i])
            maybe_word = maybe_words[i]
            if maybe_word == word:
                if faces:
                    self.information['face'] = faces[i]
                if self.information['imperative']:
                    if maybe_word.endswith('те'):
                        self.information['amount'] = 1
                    else:
                        self.information['amount'] = 0
                if self.information['communion'] == 0:  # причастие
                    if self.information['view'] == 0:  # несовершенный
                        if i == 0:
                            self.information['time'] = 1
                            self.information['voice'] = 0
                        elif i == 1:
                            self.information['time'] = 0
                            self.information['voice'] = 0
                        elif i == 2:
                            self.information['voice'] = 1
                    else:  # совершенный
                        self.information['voice'] = i
                return True
        return False

    @staticmethod
    def _parse_class_transl_form_ins(tag, word):
        """
        Возвращает True, если удалось найти слово прилагательное.

        :param tag: <class 'lxml.html.HtmlElement'>
        :param word: string
        :return: bool
        """

        for maybe_word in tag.getchildren()[0].text.split(' / '):
            if maybe_word == word:
                return True
        return False


class SynonymOnline(FunctionsOfParsingWord, FunctionsOfParsingSyn):
    urls = []
    posts = []
    convert_link = []
    count = 0

    def __init__(self):
        self.session = requests.session()

    def get(self, word):
        word = word.lower()
        site = self._bring_site(word)
        if site is None:
            return word

        for state in self.information:
            self.information[state] = None
        success = super().parse_sections(site, word)
        for x in self.information:
            print('\033[45m\033[30m' + x.ljust(11) + '\033[0m\033[33m',
                  self.information[x] if self.information[x] is not None else '')
        print('\033[36mTrue\033[0m' if success else '\033[31mFalse\033[0m')
        print()

        started_form = self._to_started_form(site)
        print('\033[35mstarted\033[0m')
        syn_words = self._find(started_form)
        print('\033[35mfound\033[0m')
        while syn_words:
            syn_word = syn_words.pop(randint(0, len(syn_words)-1))
            print(syn_word)
            site = self._bring_site(syn_word)
            print('\033[35mbrounght\033[0m')
            if site is None:
                continue
            syn_word = super().get_syn(site)
            print('\033[35mgot syn\033[0m')
            if syn_word is None:
                continue
            return syn_word
        return word

    def _find(self, word):
        words = []
        for i in range(self.count):
            link = self.urls[i] + SynonymOnline.convert_link[i](word)
            error = 'fuck'
            while error is not None:
                try:
                    site = self.session.get(link, headers=headers)
                    error = None
                except requests.exceptions.ConnectionError as e:
                    error = e
                    print('\033[31m' + str(error))
            if site.status_code == 404:
                print('\033[31mError:', word, i)
                continue
            synonyms = SynonymOnline.posts[i](site.text)
            if synonyms is not None:
                words.extend(synonyms)
        s = ''
        for x in words:
            s += str(x) + ', '
        print('\033[34m' + s[:-2] + '\033[0m')
        words = list(set(words))
        return words

    def _bring_site(self, word):
        print('\033[32mstart\033[0m')
        while True:
            site = self.session.get('https://www.translate.ru/grammar/ru-en/' + word, headers=headers)
            if site.status_code == 404:
                return None
            site = html.fromstring(site.text)
            if site.xpath('.//div[@class="error"]') or site.xpath('.//div[@id="GoToTranslatorText"]'):
                print('\033[31m' + '-' * 23 + '\033[0m')
                return None
            if site.xpath('//span[@class="sforms_src"]'):
                break
        return site

    def add_site(self, link, post, convert_link):
        self.urls.append(link)
        self.posts.append(post)
        self.convert_link.append(convert_link)
        self.count += 1

    @staticmethod
    def _to_started_form(site):
        word = site.xpath('.//span[@class="sforms_src"]/p/b/span[@class="source_only"]')[0]
        return word.text.lower()

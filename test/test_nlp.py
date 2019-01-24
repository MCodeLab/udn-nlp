import unittest

from udn_nlp import nlp

class NLPTestCase(unittest.TestCase):
    def test_check_mistakes(self):
        sorted_words = nlp.check_mistakes("This is a asdfkg sentence, contttining; missssstakes all over ThE pLLace")
        right_words = sorted_words['right_words']
        wrong_words = sorted_words['wrong_words']

        self.assertEqual(len(right_words), 7)
        self.assertEqual(len(wrong_words), 4)

        # Capitalization should be preserved
        self.assertIn('This', right_words)
        self.assertNotIn('this', right_words)

        self.assertIn('asdfkg', wrong_words)

        # Word validity should be case-insensitive
        self.assertIn('ThE', right_words)

        # Punctuation should not be stripped
        self.assertIn('sentence,', right_words)
        self.assertIn('contttining;', wrong_words)

    def test_filter_words(self):
        filtered_text, words_filtered = nlp.filter_words('HEARTITORIUM  Tha HeartitoHom ia mlaaing foam  thia leeue af The Telegram an  aooeunt of tha illneaa af Miaa  Kaye.')
        self.assertEqual(filtered_text, '[5;35] foam [3;11] The Telegram an [1;7] of [4;16] Kaye.')
        self.assertEqual(words_filtered, ['HEARTITORIUM', 'Tha', 'HeartitoHom', 'ia', 'mlaaing', 'thia', 'leeue', 'af', 'aooeunt', 'tha', 'illneaa', 'af', 'Miaa'])
 # She es pacta to return ta  her dutiee In the next day ar aa  and ejueettona aubmrtted ta her  will be answered in their turn.

    def test_filter_words_edgecase(self):
        self.maxDiff = None
        # test filter_words on cases that previously crashed, such as 16005 and 18002511
        filtered_text, words_filtered = nlp.filter_words("""U  Mm H. Nicholes Dies  At ProYo Hospital  Iroiigut Home for Ilurlal Funeral  Sen Ices Held Wednesday.  John H. Nicholes died of tubcrcu-Boils  tubcrcu-Boils last Mojidny nt tho Provo hospl.  m and was brought homo to Amcrl-Bin  Amcrl-Bin Fork for burial Wednesday. He  Mad been ailing for some time and tlir  Hod was not unexpected. Ills wife  Hho wus formerly Mrs. Mnry Steele  Weeded him to tho groat boyoud  M years ago. Hu leaves quite  Homier of brothers and Hlstors, mot?  whom live In American Fork. H(  Ho leaves four children, Mrs Mat'  Jcliolos-Cunteruiali and Jiih. Nlcholo  B Seattle, and Mrs, May O'lfrlen am  renco Nlrholes, who renldo In Sal  Me City,  JJolm Nleholon was n son of Joslnl  HW Ann Nicholes and was born I  porlcan Fork fi7 years ago. Moa  K? his llfi has been spent hero lend  t a (Uli't farmor'a Ufo.  Funeral services woro hold nt th  V homo rosldeuco In Second V  lneday nfternoon nt 2 o'clock. '  H Chlpmnn presldliig: other rcmnrl  're miiilH by Stophen P. linker. Joh  H. Forbes and James H. Clarke; solos  so-los wcrcjung by Messrs Myron Chip,  man, Alfred Jensen nnd E. M. V.  'Jones,  Thoro was a largo attendance oi  rolntlves and friends, and tho flornl  offorlngs were many and beautiful,  \" -""")
        self.assertEqual(filtered_text, '''[4;13] Dies At [1;5] Hospital [1;8] Home for [1;7] Funeral [1;3] Ices Held Wednesday. John [2;10] died of [2;26] last [2;9] tho Provo [2;7] and was brought [1;4]to [2;18] Fork for burial Wednesday. He Mad been ailing for some time and [1;4] Hod was not unexpected. Ills wife [2;6] formerly [2;8] Steele Weeded him to tho [3;12] years ago. [1;2] leaves quite Homier of brothers and [2;12] whom live In American Fork. [1;2] Ho leaves four children, [1;3] Mat' [1;20] and [3;13] Seattle, and[1;4] May [1;8] am [2;14] who [1;6] In Sal Me City, [2;13] was [1;1] son of [2;8]Ann [1;8] and was born I [1;7] Fork [1;3] years ago. [2;5] his [1;4] has been spen [1;1] hero lend t a [3;18] Funeral services [1;4] hold [1;2] th [3;14] In Second[4;18] 2 o [1;1] clock. ' [3;19] other [3;15] by [2;9] linker. [2;5] Forbes and James [1;2] Clarke; solos [2;14] by [1;6] Myron Chip, man, Alfred Jensen [6;21] wasa largo attendance [2;11] and friends, and tho [2;15] were many and beautiful, [2;2]''')
        self.assertEqual(words_filtered, [])

    def test_generate_nltk_text(self):
        # test from Heartitorium September 6, 1917
        text = nlp.generate_nltk_text_from_doc(18002511)
        print(text.tokens)

        # TODO verify that collocations aren't produced for non-adjacent words (i.e. gibberish in between)

        print(text.collocations())
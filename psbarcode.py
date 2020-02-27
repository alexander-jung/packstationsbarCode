"""
aus https://github.com/probonopd/packstation-barcode/blob/master/barcode.py
und https://gist.github.com/arturfsousa/3716729/783372dc486c88f9be16dbbc4c70dbe0caa515b2
zusammengebaut, aber online connection entfernt, nur lokaler aufruf
"""
import itertools
import string
import sys
import webbrowser

import luhn


# Deutsche Post DHL hat einfach an Packstationen den Kartenleser
# ausgebaut und duch einen Barcodeleser ersetzt, ohne den
# Besitzern einer Goldcard automatisch rechtzeitig eine neue
# Karte zuzuschicken. Man kann aber weiterhin an solchen Stationen
# Pakete abholen, nur muss man jetzt die PostNummer manuell eintippen.
# Mit diesem Skript generieren wir uns den entsprechenden Barcode, da das
# Zusenden einer neuen Karte bei DHL beauftragt werden muss, die alte Karte
# in der Zwischenzeit sofort gesperrt wird und die neue bis zu 2 Wochen
# dauern kann. Das ist maximal kundenunfreundlich.
# Sicherheitstechnisch liegt kein Verstoß vor, da man durch Eintippen
# der PostNummer sowieso Pakete abholen kann und die Umrechnung von
# PostNummer zu Barcode im Netz bereits vielfach beschrieben ist.
# Der 16-stellige ITF-Barcode ist relativ einfach aufgebaut:
# "3”+”[so viele ‘0’, dass die Zahl insgesamt 16 Stellen hat]”
# +”[Postnummer*631]”+”[Luhn-Prüfziffer über ‘Postnummer*631’]"
# http://www.frei-tag.com/index.php?/archives/445-DHL-Packstation-ohne-Goldcard.html

def generate(number):
    postnummer = int(number)

    number = postnummer * 631
    luhnnr = luhn.generate(str(number))
    number = "3" + (str(number) + str(luhnnr)).zfill(15)

    return str(number)


# Beispiel anhand einer zufallsgenerierten Zahl:
# 20281557 ergibt 3000127976624677
assert generate("20281557") == "3000127976624677"

# generate interleave2of5 bar code as html

DIGITS = [
    ['n', 'n', 'w', 'w', 'n'],
    ['w', 'n', 'n', 'n', 'w'],
    ['n', 'w', 'n', 'n', 'w'],
    ['w', 'w', 'n', 'n', 'n'],
    ['n', 'n', 'w', 'n', 'w'],
    ['w', 'n', 'w', 'n', 'n'],
    ['n', 'w', 'w', 'n', 'n'],
    ['n', 'n', 'n', 'w', 'w'],
    ['w', 'n', 'n', 'w', 'n'],
    ['n', 'w', 'n', 'w', 'n'],
]

template_str = """<html lang="en">
  <head>
    <style>
        #barcode {height: 60px;}
        #barcode span {margin: 0;padding-bottom: 34px;height: 16px;}
        .n {padding-right: 1px;}
        .w {padding-right: 3px;}
        .n, .w {background-color: #000;}
        .s {background-color: #fff;}
    </style>
      <title></title>
  </head>
  <body>
    <div id="barcode">
      $barcode
    </div>
  </body>
</html>"""


def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *args)


def interleave2of5(code):
    digits = ['n', 'n s', 'n', 'n s']

    if len(code) % 2 != 0:
        code = '0' + code

    for digt1, digt2 in grouper(2, code):
        digt1_repr = DIGITS[int(digt1)]
        digt2_repr = map(lambda x: x + ' s', DIGITS[int(digt2)])
        digits.extend(itertools.chain(*zip(digt1_repr, digt2_repr)))

    digits.extend(['w', 'n s', 'n'])

    result = []
    for digit in digits:
        result.append('<span class="%s"/>' % digit)

    return ''.join(result)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("erzeugt aus der packstations Nummer ein HTML-file mit dem Barcode\n"
              "benoetigt die packstations Nummer als Parameter")
    else:
        packstationsnummer = sys.argv[1]
        template = string.Template(template_str)
        html = template.substitute(dict(barcode=interleave2of5(generate(packstationsnummer))))
        filename = 'packstationsbarcode' + packstationsnummer + '.html'
        f = open(filename, 'w')
        f.write(html)
        f.close()
        webbrowser.open_new_tab(filename);

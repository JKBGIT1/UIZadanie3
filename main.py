import csv
import copy
import random

class ReprezentaciaJedinca:
    def __init__(self, pocetZoranych, chromozom):
        self.pocetZoranych = pocetZoranych
        self.chromozom = chromozom

    def nahradChromozom(self, chromozom): # nahradi cely chromozom
        self.chromozom = chromozom

    def anulujPocetZoranych(self): # anuluje fitness ohodnotenie
        self.pocetZoranych = 0

    def zvysZorane(self): # zvysi fitness ohodnotenie o 1
        self.pocetZoranych = self.pocetZoranych + 1

    def vratZorane(self): # vrati fitness ohodnotenie
        return self.pocetZoranych

    def pridajDoChromozomu(self, gen): # prida gen na koniec chromozomu
        self.chromozom.append(gen)

    def vratDlzkuChromozomu(self): # vrati dlzku chromozomu
        return len(self.chromozom)

    def vratPrvokChromozomu(self, prvok): # vrati konkretny gen chromozomu
        return self.chromozom[prvok]

    def vratChromozom(self): # vrati cely chromozom jedinca
        return self.chromozom

    def zmenHodnotu(self, prvok, hodnota): # zmeni gen v chromozome
        self.chromozom[prvok] = hodnota

    def vypisChromozom(self): # vypise geny chromozomu
        for i in range(len(self.chromozom)):
            print(self.chromozom[i], end=" ")
        print("")


otocka = True # podla hodnoty v tejto premenej mnich vie ako sa ma tocit
mutacia = 0.15 # ak je hodnota z operacie random.uniform(0, 1) mensia ako hodnota v tejto premenej, tak sa vykona mutacia genu
generacia = [] # do tohto listu vkladam prvu vytvorenu generaciu a nasledne list zmenim, ked sa vytvori vzdy nova generacia
novaKrv = False # v pride, ked je hodnota tejto premennej True, tak sa do novej generacie pridavaju random vygenerovany jedinci, ked nenastalo krizenie
ruleta = True # ak ma premena hodnotu True, tak sa jedinci vyberaju pomocou typu selekcie ruleta
crossover = 0.9 # v podmienka vykonam random.uniform(0, 1) a ak je hodnota, tejto random operacie mensia ako hodnota tejto premenej, tak sa vykona krizenie, inak sa vykona bud pridanie novej krvi alebo sa vyberie jedinec, ktory len prejde do novej generacie
novaFitness = 0 # postupne hodnotim generaciu, ktoru vytvaram tym, ze fitness vytvorenych jedincov priratam do tejto premenej
celkovaFitness = 0 # po vytvoreni dalsej generacie tato premena vyjadruje to aka je vytvorena generacia dobra a je to potrebne kvoli rulete
elitarizmus = True # ak hodnota tejto premennej True, tak do novej generacie prejde jeden najlepsi z predoslej
pooranaZahradka = False # ak sa hodnota tejto premenej zmeni na True, tak sa vytvoril jedinec, ktory pooral celu zahradku
pocetJedincovGeneracia = 50 # pocet jedincov pre kazdu generaciu
najlepsi = None # tu bude na konci algoritmu najlepsi jedinec zo vsetkych generacii
# nahadzem sem suradnice, z ktoryhc moze mnich vstupit do zahradky
mozneVstupy = {1: {}, 2: {}, 3: {}, 4: {}} # vytvoril som dictionary v dictionary, 1 = oranie z lava do prava, 2 = oranie z hora dole, 3 = oranie z prava do lava, 4 = oranie z dola hore
dlzkaChromozomu = polickaNaOranie = pocetMoznychVstupov = 0 # tieto premene zmenia hodnotu pri nacitani zahradky, ktoru bude mnich orat


def vytvorZahradku(): # nacitanie zahradky zo suboru vstup.txt, tiez tu zistim maximalnu dlzkuChromozomu a policka, ktore treba poorat
    global dlzkaChromozomu, polickaNaOranie, pocetGenovGeneracia

    file = open('vstup.txt', 'r')
    pocetKamenov = 0
    zahradka = [[]]
    i = 0

    while True:
        char = file.read(1) # subor citam pismenko po pismenku
        if char == '\n': # ak je koniec riadka v subore, tak pridam list do zahradky
            i = i + 1
            zahradka.append([])
        elif not char: # ak som na konci suboru, tak breaknem cyklus
            break
        else: # vykona sa ak nie je koniec suboru alebo precitany znak nie je novy riadok
            if char == '0': # znak je 0, takze sa zvysi pocet policok, ktore musi mnich poorat
                polickaNaOranie = polickaNaOranie + 1
            else: # ked znak nie je 0, tak to je kamen, teda sa zvysi pocet kamenov na mape
                pocetKamenov = pocetKamenov + 1
            zahradka[i].append(char) # znak pridam do zahradky

    file.close()

    dlzkaChromozomu = len(zahradka) + len(zahradka[0]) + pocetKamenov # polovica obvodu + pocet kamenov v zahradka = dlzka chromozomu

    return zahradka # vratim nacitanu zahradku


def zistiParametre(): # nacitanie udajov od pouzivatela, podla ktorych bude algoritmus postupovat
    global pocetJedincovGeneracia, elitarizmus, crossover, mutacia, ruleta, novaKrv

    pocetJedincovGeneracia = int(input("Zadaj pocet jedincov generacie: "))
    crossover = float(input("Zadaj pravdepodobnost krizenia (0, 1): "))
    mutacia = float(input("Zadaj pravdepodonost mutacie (0, 1): "))
    if (input("Vyber selekcny algoritmus (ruleta/turnaj): ") == "ruleta"):
        ruleta = True
    else:
        ruleta = False
    if (str(input("Chces elitarizmus (ano/nie): ")) == "ano"):
        elitarizmus = True
    else:
        elitarizmus = False
    if (input("Chces pridavanie novej krvi (ano/nie): ") == "ano"):
        novaKrv = True
    else:
        novaKrv = False



def vypisZahradku(zahradka): # funkcia sluzi na vypis zahradky
    for i in range(len(zahradka)):
        for j in range(len(zahradka[i])):
            print('{:2}'.format(zahradka[i][j]), end=" ")
        print("")
    print("Pocet policok na oranie: " + str(polickaNaOranie))


def vypisZahradkuPostupnost(oranie, postup, jedinec): # vypisem zahradku, postupnost orania a pocet policok, ktore boli poorane
    for i in range(len(postup)):
        print(str(postup[i]) + " ", end=" ")
    print("\n")
    vypisZahradku(oranie)
    print("Pocet pooranych: " + str(jedinec.vratZorane()))
    print("")


def zistiVstupyZlava(zahradka): # funkcia zisti vsetky mozne vstupy z laveho okraja zahradky
    global mozneVstupy, pocetMoznychVstupov
    for i in range(len(zahradka) - 1, -1, -1): # tento for cyklus prejde cely stlpec na lavej strane a zisti, z ktoreho policka sa da vstupit do zahradky
        if (zahradka[i][0] != 'K'): # tato podmienka zabezpeci, ze sa da z aktualneho policka vstupit na zahradu
            # zvysim celkovy pocetMoznychVstupov, pretoze tato premena my symbolizuje pocet vstupov a pocet jednicov v generacii
            pocetMoznychVstupov = pocetMoznychVstupov + 1
            # vstup si ulozim ako dictionary s klucom(pocetMoznychVstupov) a hodnotou(suradnice policka), ktory sa nachadza pod klucom 1 v hlavnom dictionary
            mozneVstupy.get(1).update({pocetMoznychVstupov: (i, 0)})


def zistiVstupyZhora(zahradka): # funkcia zisti vsetky mozne vstupy z vrchneho okraja zahradky
    global mozneVstupy, pocetMoznychVstupov
    for i in range(len(zahradka[0])): # tento for cyklus prejde cely horny riadok a zisti, z ktoreho policka sa da vstupit do zahradky
        if (zahradka[0][i] != 'K'): # tato podmienka zabezpeci, ze da z aktualneho policka vstupit na zahradu
            # zvysim celkovy pocetMoznychVstupov, pretoze tato premena my symbolizuje pocet vstupov a pocet jednicov v generacii
            pocetMoznychVstupov = pocetMoznychVstupov + 1
            # vstup si ulozim ako dictionary s klucom(pocetMoznychVstupov) a hodnotou(suradnice policka), ktory sa nachadza pod klucom 2 v hlavnom dictionary
            mozneVstupy.get(2).update({pocetMoznychVstupov: (0, i)})


def zistiVstupyZprava(zahradka): # funkcia zisti vsetky mozne vstupy z praveho okraja zahradky
    global mozneVstupy, pocetMoznychVstupov
    for i in range(len(zahradka)): # tento for cyklus prejde cely pravy stlpec a zisti, z ktoreho policka sa da vstupit do zahradky
        if (zahradka[i][len(zahradka[0]) - 1] != 'K'): # tato podmienka zabezpeci, ze da z aktualneho policka vstupit na zahradu
            # zvysim celkovy pocetMoznychVstupov, pretoze tato premena my symbolizuje pocet vstupov a pocet jednicov v generacii
            pocetMoznychVstupov = pocetMoznychVstupov + 1
            # vstup si ulozim ako dictionary s klucom(pocetMoznychVstupov) a hodnotou(suradnice policka), ktory sa nachadza pod klucom 3 v hlavnom dictionary
            mozneVstupy.get(3).update({pocetMoznychVstupov: (i, len(zahradka[0]) - 1)})


def zistiVstupyZdola(zahradka): # funkcia zisti vsetky mozne vstupy z dolneho okraja zahradky
    global mozneVstupy, pocetMoznychVstupov
    for i in range(len(zahradka[0]) - 1, - 1, -1): # tento for cyklus prejde cely dolny riadok a zisti, z ktoreho policka sa da vstupit do zahradky
        if (zahradka[len(zahradka) - 1][i] != 'K'): # tato podmienka zabezpeci, ze da z aktualneho policka vstupit na zahradu
            # zvysim celkovy pocetMoznychVstupov, pretoze tato premena my symbolizuje pocet vstupov a pocet jednicov v generacii
            pocetMoznychVstupov = pocetMoznychVstupov + 1
            # vstup si ulozim ako dictionary s klucom(pocetMoznychVstupov) a hodnotou(suradnice policka), ktory sa nachadza pod klucom 4 v hlavnom dictionary
            mozneVstupy.get(4).update({pocetMoznychVstupov: (len(zahradka) - 1, i)})


def zistiVstupy(zahradka): # zisti vsetky vstupy do zahradky a ulozi ich do vytvorenych dictionary v dictionary mozneVstupy
    zistiVstupyZlava(zahradka) # mozne vstupy z lavej strany zahradky
    zistiVstupyZhora(zahradka) # mozne vstupy z hora zahradky
    zistiVstupyZprava(zahradka) # mozne vstupy z pravej strany zahradky
    zistiVstupyZdola(zahradka) # mozne vstupy z dola zahradky


def oranieZlava(suradniceXY, oranie, jedinec, vstup):
    global otocka
    x, y = suradniceXY

    while (y < len(oranie[x])):
        if (oranie[x][y] != '0'):  # mnich narazil na prekazku alebo poorane policko
            if otocka:  # mnich by chcel ist do lava
                if (x - 1 < 0):  # mnich by mal ist mimo mapu
                    if (x + 1 < len(oranie) and oranie[x + 1][y - 1] == '0'):  # mnich by mal ist mimo mapu, ale moze ist do prava
                        otocka = True
                        return oranieZhora((x + 1, y - 1), oranie, jedinec, vstup)
                    else:  # mnich moze ist iba mimo mapu
                        otocka = False
                        return True
                elif (oranie[x - 1][y - 1] != '0'):  # mnich nemoze ist do lava, pretoze je poorane alebo tam je prekazka
                    if (x + 1 < len(oranie) and oranie[x + 1][y - 1] == '0'):  # mnich nemoze ist do lava, ale moze ist do prava
                        otocka = True
                        return oranieZhora((x + 1, y - 1), oranie, jedinec, vstup)
                    else:  # mnich sa zasekol, tuto to konci
                        return False
                else:  # mnich moze ist do lava
                    otocka = False
                    return oranieZdola((x - 1, y - 1), oranie, jedinec, vstup)
            else:  # mnich chce ist do prava
                if (x + 1 == len(oranie)):  # mnich by mal ist mimo mapu ak pojde do prava
                    if (x - 1 >= 0 and oranie[x - 1][y - 1] == '0'):  # mnich by mal ist mimo mapu, ale moze ist do lava
                        otocka = False
                        return oranieZdola((x - 1, y - 1), oranie, jedinec, vstup)
                    else:  # mnich moze ist iba mimo mapu
                        otocka = True
                        return True
                elif (oranie[x + 1][y - 1] != '0'):  # mnich nemoze ist do prava, pretoze je poorane alebo tam je prekazka
                    if (x - 1 >= 0 and oranie[x - 1][y - 1] == '0'):  # mnich moze ist do lava
                        otocka = False
                        return oranieZdola((x - 1, y - 1), oranie, jedinec, vstup)
                    else:  # mnich sa zasekol
                        return False
                else:  # mnich moze ist do prava
                    otocka = True
                    return oranieZhora((x + 1, y - 1), oranie, jedinec, vstup)
        elif (oranie[x][y] == '0'):
            oranie[x][y] = str(vstup)
            jedinec.zvysZorane()
            y = y + 1

    if (y >= len(oranie[x])):  # mnich vysiel zo zahradky, pretoze ju presiel po dlzke celu, takze idem skusat dalsi vstup
        return True


def oranieZhora(suradniceXY, oranie, jedinec, vstup):
    global otocka
    x, y = suradniceXY

    while (x < len(oranie)):
        if (oranie[x][y] != '0'):  # mnich narazil na prekazku alebo poorane policko
            if otocka:  # mnich by chce ist do lava
                if (y + 1 >= len(oranie[x])):  # mnich by mal ist mimo mapu
                    if (y - 1 >= 0 and oranie[x - 1][y - 1] == '0'):  # mnich by mal ist mimo mapu, ale moze ist do prava
                        otocka = True
                        return oranieZprava((x - 1, y - 1), oranie, jedinec, vstup)
                    else:  # mnich moze ist iba mimo mapu
                        otocka = False
                        return True
                elif (oranie[x - 1][y + 1] != '0'):  # mnich nemoze ist do lava, pretoze je poorane alebo tam je prekazka
                    if (y - 1 >= 0 and oranie[x - 1][y - 1] == '0'):  # mnich nemoze ist do lava, ale moze ist do prava
                        otocka = True
                        return oranieZprava((x - 1, y - 1), oranie, jedinec, vstup)
                    else:  # mnich sa zasekol, tuto to konci
                        return False
                else:  # mnich moze ist do lava
                    otocka = False
                    return oranieZlava((x - 1, y + 1), oranie, jedinec, vstup)
            else:  # mnich chce ist do prava
                if (y - 1 < 0):  # mnich by mal ist mimo mapu ak pojde do prava
                    if (y + 1 < len(oranie[x]) and oranie[x - 1][y + 1] == '0'):  # mnich by mal ist mimo mapu, ale moze ist do lava
                        otocka = False
                        return oranieZlava((x - 1, y + 1), oranie, jedinec, vstup)
                    else:  # mnich moze ist iba mimo mapu
                        otocka = True
                        return True
                elif (oranie[x - 1][y - 1] != '0'):  # mnich nemoze ist do prava, pretoze je poorane alebo tam je prekazka
                    if (y + 1 < len(oranie[x]) and oranie[x - 1][y + 1] == '0'):  # mnich moze ist do lava
                        otocka = False
                        return oranieZlava((x - 1, y + 1), oranie, jedinec, vstup)
                    else:  # mnich sa zasekol
                        return False
                else:  # mnich moze ist do prava
                    otocka = True
                    return oranieZprava((x - 1, y - 1), oranie, jedinec, vstup)
        elif (oranie[x][y] == '0'):
            oranie[x][y] = str(vstup)
            jedinec.zvysZorane()
            x = x + 1

    if (x >= len(oranie)):  # mnich vysiel zo zahradky, pretoze ju presiel po sirke celu, takze idem skusat dalsi vstup
        return True


def oranieZprava(suradniceXY, oranie, jedinec, vstup):
    global otocka
    x, y = suradniceXY

    while(y >= 0):
        if (oranie[x][y] != '0'):  # mnich narazil na prekazku alebo poorane policko
            if otocka:  # mnich by chce ist do lava
                if (x + 1 >= len(oranie)):  # mnich by mal ist mimo mapu
                    if (x - 1 >= 0 and oranie[x - 1][y + 1] == '0'):  # mnich by mal ist mimo mapu, ale moze ist do prava
                        otocka = True
                        return oranieZdola((x - 1, y + 1), oranie, jedinec, vstup)
                    else:  # mnich moze ist iba mimo mapu
                        otocka = False
                        return True
                elif (oranie[x + 1][y + 1] != '0'):  # mnich nemoze ist do lava, pretoze je poorane alebo tam je prekazka
                    if (x - 1 >= 0 and oranie[x - 1][y + 1] == '0'):  # mnich nemoze ist do lava, ale moze ist do prava
                        otocka = True
                        return oranieZdola((x - 1, y + 1), oranie, jedinec, vstup)
                    else:  # mnich sa zasekol, tuto to konci
                        return False
                else:  # mnich moze ist do lava
                    otocka = False
                    return oranieZhora((x + 1, y + 1), oranie, jedinec, vstup)
            else:  # mnich chce ist do prava
                if (x - 1 < 0):  # mnich by mal ist mimo mapu ak pojde do prava
                    if (x + 1 < len(oranie) and oranie[x + 1][y + 1] == '0'):  # mnich by mal ist mimo mapu, ale moze ist do lava
                        otocka = False
                        return oranieZhora((x + 1, y + 1), oranie, jedinec, vstup)
                    else:  # mnich moze ist iba mimo mapu
                        otocka = True
                        return True
                elif (oranie[x - 1][y + 1] != '0'):  # mnich nemoze ist do prava, pretoze je poorane alebo tam je prekazka
                    if (x + 1 < len(oranie) and oranie[x + 1][y + 1] == '0'):  # mnich moze ist do lava
                        otocka = False
                        return oranieZhora((x + 1, y + 1), oranie, jedinec, vstup)
                    else:  # mnich sa zasekol
                        return False
                else:  # mnich moze ist do prava
                    otocka = True
                    return oranieZdola((x - 1, y + 1), oranie, jedinec, vstup)
        elif (oranie[x][y] == '0'):
            oranie[x][y] = str(vstup)
            jedinec.zvysZorane()
            y = y - 1

    if (y < 0):  # mnich vysiel zo zahradky, pretoze ju presiel po dlzke celu, takze idem skusat dalsi vstup
        return True


def oranieZdola(suradniceXY, oranie, jedinec, vstup):
    global otocka
    x, y = suradniceXY

    while(x >= 0):
        if (oranie[x][y] != '0'):  # mnich narazil na prekazku alebo poorane policko
            if otocka:  # mnich by chce ist do lava
                if (y - 1 < 0):  # mnich by mal ist mimo mapu
                    if (y + 1 < len(oranie[x]) and oranie[x + 1][y + 1] == '0'):  # mnich by mal ist mimo mapu, ale moze ist do prava
                        otocka = True
                        return oranieZlava((x + 1, y + 1), oranie, jedinec, vstup)
                    else:  # mnich moze ist iba mimo mapu
                        otocka = False
                        return True
                elif (oranie[x + 1][y - 1] != '0'):  # mnich nemoze ist do lava, pretoze je poorane alebo tam je prekazka
                    if (y + 1 < len(oranie[x]) and oranie[x + 1][y + 1] == '0'):  # mnich nemoze ist do lava, ale moze ist do prava
                        otocka = True
                        return oranieZlava((x + 1, y + 1), oranie, jedinec, vstup)
                    else:  # mnich sa zasekol, tuto to konci
                        return False
                else:  # mnich moze ist do lava
                    otocka = False
                    return oranieZprava((x + 1, y - 1), oranie, jedinec, vstup)
            else:  # mnich chce ist do prava
                if (y + 1 >= len(oranie[x])):  # mnich by mal ist mimo mapu ak pojde do prava
                    if (y - 1 >= 0 and oranie[x + 1][y - 1] == '0'):  # mnich by mal ist mimo mapu, ale moze ist do lava
                        otocka = False
                        return oranieZprava((x + 1, y - 1), oranie, jedinec, vstup)
                    else:  # mnich moze ist iba mimo mapu
                        otocka = True
                        return True
                elif (oranie[x + 1][y + 1] != '0'):  # mnich nemoze ist do prava, pretoze je poorane alebo tam je prekazka
                    if (y - 1 >= 0 and oranie[x + 1][y - 1] == '0'):  # mnich moze ist do lava
                        otocka = False
                        return oranieZprava((x + 1, y - 1), oranie, jedinec, vstup)
                    else:  # mnich sa zasekol
                        return False
                else:  # mnich moze ist do prava
                    otocka = True
                    return oranieZlava((x + 1, y + 1), oranie, jedinec, vstup)
        elif (oranie[x][y] == '0'):
            oranie[x][y] = str(vstup)
            jedinec.zvysZorane()
            x = x - 1

    if (x < 0):  # mnich vysiel zo zahradky, pretoze ju presiel po sirke celu, takze idem skusat dalsi vstup
        return True


def ohodnotOranie(jedinec, zahradka, ibaVypis): # tato funkcia ohodnoti fitness pre jedinca, ktory do nej vstupy
    global otocka, pooranaZahradka

    postup = [] # postup vstupov, podla ktorych mnich oral
    otocka = True # na zaciatku musim inicializovat na True, pretoze mnich sa bude snazit ist najprv dolava
    jedinec.anulujPocetZoranych() # anulujem fitness funkciu a pojdem ju hodnotit

    oranie = copy.deepcopy(zahradka) # zahradka je dvojrozmerny list, preto ho treba prekopirovat pomocou tejto kniznice
    for i in range(jedinec.vratDlzkuChromozomu()): # prejdem jednotlive geny chromozomu poporadi v cykle
        if (mozneVstupy.get(1).get(jedinec.vratPrvokChromozomu(i)) is not None): # vyskusam, ci tento gen vstupuje zlava
            suradniceXY = mozneVstupy.get(1).get(jedinec.vratPrvokChromozomu(i)) # zistim suradnice z ktorych mnich vstupi do zahradky
            if oranie[suradniceXY[0]][suradniceXY[1]] == '0': # ak je mozny vstup z tychto suradnic, tak mnich bude orat, inak pojde na dalsi gen chromozomu
                oranieZlava(suradniceXY, oranie, jedinec, jedinec.vratPrvokChromozomu(i)) # zacne oranie zlava
                postup.append(jedinec.vratPrvokChromozomu(i)) # gen sa prida do postupnosti vstupov orania
        elif (mozneVstupy.get(2).get(jedinec.vratPrvokChromozomu(i)) is not None): # vykusam, ci tento gen vstupuje zhora
            suradniceXY = mozneVstupy.get(2).get(jedinec.vratPrvokChromozomu(i)) # zistim suradnice z ktorych mnich vstupi do zahradky
            if oranie[suradniceXY[0]][suradniceXY[1]] == '0': # ak je mozny vstup z tychto suradnic, tak mnich bude orat, inak pojde na dalsi gen chromozomu
                oranieZhora(suradniceXY, oranie, jedinec, jedinec.vratPrvokChromozomu(i)) # zacne oranie zhora
                postup.append(jedinec.vratPrvokChromozomu(i)) # gen sa prida do postupnosti vstupov orania
        elif (mozneVstupy.get(3).get(jedinec.vratPrvokChromozomu(i)) is not None): # vyskusam, ci tento gen vstupuje zprava
            suradniceXY = mozneVstupy.get(3).get(jedinec.vratPrvokChromozomu(i)) # zistim suradnice z ktorych mnich vstupi do zahradky
            if oranie[suradniceXY[0]][suradniceXY[1]] == '0': # ak je mozny vstup z tychto suradnic ,tak mnich bude orat, inak pojde na dalsi gen chromozomu
                oranieZprava(suradniceXY, oranie, jedinec, jedinec.vratPrvokChromozomu(i)) # zacne orania zprava
                postup.append(jedinec.vratPrvokChromozomu(i)) # gen sa prida do postupnosti vstupov orania
        else: # gen uz moze vstupovat iba zdola
            suradniceXY = mozneVstupy.get(4).get(jedinec.vratPrvokChromozomu(i)) # zistim suradnice z ktorych mnich vstupi do zahradky
            if oranie[suradniceXY[0]][suradniceXY[1]] == '0': # ak je mozny vstup z tychto suradnic, tak mnich bude orat, inak pojde na dalsi gen chromozomu
                oranieZdola(suradniceXY, oranie, jedinec, jedinec.vratPrvokChromozomu(i)) # zacne oranie zdola
                postup.append(jedinec.vratPrvokChromozomu(i)) # gen sa prida do postupnosti vstupov orania

        if jedinec.vratZorane() == polickaNaOranie: # ak mnich pooral celu zahradku, tak sa ukonci program
            print("VYPIS CHROMOZOMU:")
            jedinec.vypisChromozom() # vypise sa postupnost genov chromozomu
            print("SPRAVNA POSTUPNOST ORANIA:")
            vypisZahradkuPostupnost(oranie, postup, jedinec) # vypise sa aj postupnost vstupov, ktore mnich vyuzil pri orani
            pooranaZahradka = True # signalizuje, ze sa ma skoncit program
            return

    if (ibaVypis): # v pripade ze nebol vytvoreny jedinec, ktory pooral celu zahradku, tak sa vypise celkovy najlepsi
        print("VYPIS CHROMOZOMU:")
        jedinec.vypisChromozom()
        vypisZahradkuPostupnost(oranie, postup, jedinec)

    return


def vytvorPrvuGeneraciu(zahradka): # funkcia turbo nahodne vytvori prvu generaciu s ktorou bude algoritmus pracovat
    global pooranaZahradka, celkovaFitness, najlepsi
    # ak ma generacia pocet jedincov, ktory ma mat alebo sa nasiel jedinec, ktory dokaze poorat celu zahradku, tak sa skonci cyklus
    while (len(generacia) <= pocetJedincovGeneracia and pooranaZahradka == False):
        vytvaranyJedinec = ReprezentaciaJedinca(0, []) # vytvori sa novy jedince, ktoremu sa budu nahodne generovat geny chromozomu

        while (vytvaranyJedinec.vratDlzkuChromozomu() <= dlzkaChromozomu): # pokial dlzka chromozomu jedinca nie je maximalna, tak sa bude vykonavat cyklus
            vytvaranyJedinec.pridajDoChromozomu(random.randint(1, pocetMoznychVstupov)) # random gen sa prida na koniec chromozomu

        ohodnotOranie(vytvaranyJedinec, zahradka, False) # vytvoreny jedinec sa ohodnoti

        if (len(generacia) == 0): # najlepsi este nebol inicializovany, tak je prvy vytvoreny najlepsi
            najlepsi = copy.deepcopy(vytvaranyJedinec)
        elif (najlepsi.vratZorane() < vytvaranyJedinec.vratZorane()): # ak sa vytvori lepsi ako je aktualny najlepsi, tak vytvoreny bude novy najlepsi
            najlepsi = copy.deepcopy(vytvaranyJedinec)

        celkovaFitness = celkovaFitness + vytvaranyJedinec.vratZorane() # je potrebne vediet celkovu fitness populacie, v pripade, ze sa pouzivatel rozhodne pre ruletu
        generacia.append(vytvaranyJedinec) # vytvoreny jedinec sa prida do generacie


def spustiRuletu(): # pomocou ruletoveho algoritmu selekcie sa vybere jedinec z generacie
    cisloFitness = random.randint(0, celkovaFitness) # vygeneruje sa nahodne cislo, od 0 po celkovu fitness generacie

    pocitadlo = 0
    for i in range(len(generacia)): # ruleta sa toci, pokial nie je na jedincovi, ktoreho ma vybrat
        if (pocitadlo + generacia[i].vratZorane() >= cisloFitness):
            return generacia[i]
        else:
            pocitadlo = pocitadlo + generacia[i].vratZorane()


def vyberDoTurnaja():
    jedinci = []

    while (len(jedinci) < 4): # v cykle vyberiem 4 nahodnych jedincov z generacie
        vybratyJedinec = generacia.__getitem__(random.randint(0, len(generacia) - 1))
        jedinci.append(vybratyJedinec)

    return jedinci


def zacniTurnaj():
    jedinci = vyberDoTurnaja()
    if (jedinci[0].vratZorane() > jedinci[1].vratZorane()): # ak ma prvy jedinec lepsie fitness ohodnotenie ako druhy, tak postupuje
        prvyPostup = jedinci[0]
    else: # inak postupuje druhy jedinec
        prvyPostup = jedinci[1]
    if (jedinci[2].vratZorane() > jedinci[3].vratZorane()): # ak ma treti jedinec lepsie fitness ohodnotenie ako stvrty, tak postupuje
        druhyPostup = jedinci[2]
    else: # inak postupuje stvrty jedinec
        druhyPostup = jedinci[3]
    if prvyPostup.vratZorane() > druhyPostup.vratZorane(): # ak ma jedinec z prveho postupu lepsie ohodnotenie ako ten z druheho, tak vyhral turnaj
        return prvyPostup
    else: # inak vyhral turnaj jedinec z druheho postupu
        return druhyPostup


def vykonajKrizenie(prvyVybratyJedinec, druhyVybratyJedinec):
    novyJedinec = ReprezentaciaJedinca(0, [])
    # v cykle sa bude vytvarat chromozom noveho jedinca, ktory bude dostavat geny od rodicov nahodne s rovnakou pravdepodobnostou
    for i in range(0, prvyVybratyJedinec.vratDlzkuChromozomu()):
        if (random.uniform(0, 1) <= 0.5):
            novyJedinec.pridajDoChromozomu(prvyVybratyJedinec.vratPrvokChromozomu(i))
        else:
            novyJedinec.pridajDoChromozomu(druhyVybratyJedinec.vratPrvokChromozomu(i))

    return novyJedinec


def skusMutaciu(novaGeneracia, novyJedinec, zahradka):
    global novaFitness, najlepsi

    for i in range(0, novyJedinec.vratDlzkuChromozomu()): # postupne sa prechadza chromozom novo vytvoreneho jedinca a skusa sa, ci bude aktualny gen mutovat
        if (random.uniform(0, 1) <= mutacia):
            novyJedinec.zmenHodnotu(i, random.randint(1, pocetMoznychVstupov))

    ohodnotOranie(novyJedinec, zahradka, False) # vytvoreny jedinec sa ohodnoti
    if (najlepsi.vratZorane() < novyJedinec.vratZorane()): # ak je vytvoreny jedinec lepsi ako je aktualne najlepsi, tak bude on novy najlepsi
        najlepsi = copy.deepcopy(novyJedinec)

    novaFitness = novaFitness + novyJedinec.vratZorane() # jeho fitness sa prida k celkovej fitness novej generacie, pretoze bude potrebna kvoli rulete
    novaGeneracia.append(novyJedinec) # vytvoreny jedinec sa prida do novej generacie


def pridajNovuKrvDoGeneracie(novaGeneracia, zahradka):
    global novaFitness, najlepsi

    vytvaranyJedinec = ReprezentaciaJedinca(0, [])
    while (vytvaranyJedinec.vratDlzkuChromozomu() <= dlzkaChromozomu): # nahodne sa generuju geny chromozomu
        vytvaranyJedinec.pridajDoChromozomu(random.randint(1, pocetMoznychVstupov))

    ohodnotOranie(vytvaranyJedinec, zahradka, False) # nahodne vytvoreny jedinec sa ohodnoti
    if (najlepsi.vratZorane() < vytvaranyJedinec.vratZorane()): # ak je vytvoreny jedinec lepsi ako je aktualne najlepsi, tak bude on novy najlepsi
        najlepsi = copy.deepcopy(vytvaranyJedinec)

    novaFitness = novaFitness + vytvaranyJedinec.vratZorane() # jeho fitness sa prida do celkovej fitness novej generacie, pretoze bude potrebna kvoli rulete
    novaGeneracia.append(vytvaranyJedinec) # vytvoreny jedinec sa prida do novej generacie


def pridajVybranyZTurnaja(novaGeneracia): # pomocou turnaja sa vybere jedinec zo starej generacie a prida sa do novej
    global novaFitness

    prvyVybratyJedinec = zacniTurnaj()
    novaFitness = novaFitness + prvyVybratyJedinec.vratZorane()
    novaGeneracia.append(prvyVybratyJedinec)


def pridajVybranyZRulety(novaGeneracia): # pomou rulety sa vybere jedinec zo starej generacie a prida sa do novej
    global novaFitness

    prvyVybratyJedinec = spustiRuletu()
    novaFitness = novaFitness + prvyVybratyJedinec.vratZorane()
    novaGeneracia.append(prvyVybratyJedinec)


def vytvorDalsiuGeneraciu(zahradka): # tato funkcia vytvara novu generaciu
    global generacia, celkovaFitness, novaFitness

    novaFitness = 0 # bude sa pocitat celkova fitness novo vytvorenej generacie, ale na zaciatku je 0
    novaGeneracia = []
    if (elitarizmus): # ak sa pouzivatel vybral moznost elitarizmu, tak sa prida najlepsi jedinec zo starej generacie do novej
        novaGeneracia.append(generacia.__getitem__(0))
        novaFitness = novaFitness + generacia.__getitem__(0).vratZorane()

    while (len(novaGeneracia) < len(generacia)): # and pooranaZahradka == False
        if (ruleta): # vykona sa ruleta
            # ak je vysledok random cisla mensi ako hodnota premennej crossover, ktoru zadaval pouzivatel, tak sa vykona krizenie, pricom sa rodicia vyberu pomocou turnaja
            if (random.uniform(0, 1) <= crossover):
                prvyVybratyJedinec = spustiRuletu()
                druhyVybratyJedinec = spustiRuletu()
                novyJedinec = vykonajKrizenie(prvyVybratyJedinec, druhyVybratyJedinec)
                skusMutaciu(novaGeneracia, novyJedinec, zahradka) # na zaver ide novo vytvoreny jedinec skusit mutovat a nasledne bude ohodnoteni
            else: # ak sa nevykona krizenie, tak sa vytvori nova krv, ktora sa prida do novej generacie alebo sa pomocou rulety vybere jedinec, ktory pojde do novej generacie
                if (novaKrv):
                    pridajNovuKrvDoGeneracie(novaGeneracia, zahradka)
                else:
                    pridajVybranyZRulety(novaGeneracia)
        else: # vykona sa turnaj
            # ak je vysledok random cisla mensi ako hodnota premennej crossover, ktoru zadaval pouzivatel, tak sa vykona krizenie, pricom sa rodicia vyberu pomocou turnaja
            if (random.uniform(0, 1) <= crossover):
                prvyVybratyJedinec = zacniTurnaj()
                druhyVybratyJedinec = zacniTurnaj()
                novyJedinec = vykonajKrizenie(prvyVybratyJedinec, druhyVybratyJedinec)
                skusMutaciu(novaGeneracia, novyJedinec, zahradka) # na zaver ide novo vytvoreny jedinec skusit mutovat a nasledne bude ohodnoteni
            else: # ak sa nevykona krizenie, tak sa vytvori nova krv, ktora sa prida do novej generacie alebo sa pomocou turnaju vybere jedinec, ktory pojde do novej generacie
                if (novaKrv):
                    pridajNovuKrvDoGeneracie(novaGeneracia, zahradka)
                else:
                    pridajVybranyZTurnaja(novaGeneracia)

    celkovaFitness = novaFitness # musim zmenit celkovu fitness na fitness generacie, ktora bola vytvorena, je to potrebne kvoli rulete
    generacia = novaGeneracia # vymenim staru generaciu za novu


zahradka = vytvorZahradku() # program nacita rozlozenie zahradky zo suboru vstupy.txt a zisti maximalnu dlzku genu
zistiParametre() # nacita od pouzivatela pocet jedincov generacie, pravdepodobnost crossoveru a mutacie, typ selektivneho algoritmus, ci sa ma vykonat elitarizmus a pridavat "nova krv"
vypisZahradku(zahradka) # skontrolujem, ci sa zahradka nacitala dobre
zistiVstupy(zahradka) # zisti vsetky mozne vstupy z okrajov zahradky
print(mozneVstupy) # potrebujem si skontrolovat, ci zratal vsetky
vytvorPrvuGeneraciu(zahradka) # vytvori sa prva generacia
generacia.sort(key=lambda x: x.pocetZoranych, reverse=True) # ak sa ma vykonavat elitarizmus, tak je potrebne usporiadat generaciu zostupne podla fitness ohodnotenia

pocetGeneracii = 0
# ak sa uz vytvorilo 1000 generacii a nenaslo sa riesenie, tak program skonci inak skonci, ked sa vytvoril jedinec, ktory poora celu zahradku
while (pooranaZahradka == False and pocetGeneracii < 1000):
    print("CISLO GENERACIE: " + str(pocetGeneracii + 1)) # informativny vypis aby som vedel v ktorej generacii vznikol jedinec, ktory poora celu zahradku
    vytvorDalsiuGeneraciu(zahradka) # vytvaram dalsiu generaciu
    generacia.sort(key=lambda x: x.pocetZoranych, reverse=True) # ak sa ma vykonavat elitarizmus, tak je potrebne usporiadat generaciu zostupne podla fitness ohodnotenia
    pocetGeneracii = pocetGeneracii + 1

if (pooranaZahradka == False): # ak sa nevytvoril jedinec, ktory dokazal poorat celu zahradku, tak vypisem celkoveho najlepsieho
    ohodnotOranie(najlepsi, zahradka, True)

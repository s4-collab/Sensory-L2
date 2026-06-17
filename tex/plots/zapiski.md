
# Notatki

informacje co do wykresów, liczby do skopiowania itp

## wykresy

### calibration.pdf

Krzywa kalibracji:
z odpowednim zaokrąglemien już:
$y = (0,0407 \pm 0,0002) x - 0,185 \pm 0,009$
$R^2 = 0,9999$ (dokładniej 0,9998717)

po przekształceniu

$x = \frac{y + (0,185 \pm 0,009)}{0,0407 \pm 0,0002}$

### cooling.pdf

krzywa chłodzenia
linie kolorowe to te 3 fragmenty:

- czerwona - chłodzenie (ciecz)
- zielona - plateau
- niebieska - chłodzenie (tutaj był stały metal)

punkty mają SEM odpowiednio (czerwony/niebieski)
2,4812 i 2,4523 mV

finalnie obliczona temperatura to
$T = 65,2 \pm 0,4$°C

### heating.pdf

krzywa podczas ogrzewania
kolory:

- czeerwony - grzanie (ciało stałe)
- zielony - plateau
- niebieski - grzanie (ciecz)

punkty mają odpowiednio (czerwony/niebieski)
2,7408 i 2,7875 mV

finalna obliczona temperatura to
$T = 72,5 \pm 0,5$°C

### informacje

niepewność temperatury liczyłem metodą różniczki zupełnej

wzór:
$\mathcal{E} = a\cdot T -b$  UWAGA, minus przed b!!!!!
$T = \frac{\mathcal{E} + b}{a}$
$\Delta T = \frac{\delta T}{\delta a} \cdot \Delta a + \frac{\delta T}{\delta b} \cdot \Delta b + \frac{\delta T}{\delta \mathcal{E}} \cdot \Delta \mathcal{E}$

po uproszczeniu (jak dobrze policzyłem)

$\Delta T = \frac{\left|\mathcal{E} + b\right|}{a^2} \cdot \Delta a + \frac{\Delta b}{\left|a\right|} + \frac{\Delta \mathcal{E}}{\left|a\right|}$

### Obliczenia

ponieważ różnica poniędzy 65,2 a 72,5 jest większa niż 3, mamy policzyć średnią

więc obliczona temperatura topnienia tego metalu to $\frac{65,2+72,5}{2}=68,9 \pm 0,5$

zgodnie z [źródłem](https://pubs.acs.org/doi/10.1021/acs.inorgchem.6b02068)
temperatura to 70 stopni
wnioski na spokojnie

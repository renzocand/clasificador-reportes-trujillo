# -*- coding: utf-8 -*-
"""
Generador del corpus de reportes ciudadanos de infraestructura publica - Trujillo 2026
Proyecto: Sistemas Inteligentes y Machine Learning - UPN
Docente: Dr. Victor Jaime Polo Romero

Los reportes se construyen por composicion: nucleo + detalle + agravante + intro + cierre,
con sustitucion de sinonimos y ruido de tipeo. Esto evita que los textos se repitan y que
el clasificador memorice plantillas en lugar de aprender vocabulario.

Salida: reportes_ciudadanos_trujillo_2026.csv  (500 registros)
"""
import random, unicodedata, csv
from datetime import date, timedelta

SEED = 42
random.seed(SEED)

# ---------------------------------------------------------------- referencias geograficas
ZONAS = {
    "Trujillo - cercado":   ["la av. Espana", "el jr. Pizarro", "la av. America", "el ovalo Mansiche",
                             "la av. Larco", "Husares de Junin", "urb. Palermo", "urb. San Andres",
                             "Las Quintanas", "urb. Primavera", "El Recreo", "urb. Santa Maria",
                             "la av. Fatima", "Monserrate", "Covicorti"],
    "Victor Larco Herrera": ["Buenos Aires", "urb. California", "la av. Larco cuadra 12", "Vista Alegre",
                             "urb. El Golf", "Liberacion Social", "Huerta Grande"],
    "La Esperanza":         ["la av. Condorcanqui", "Manuel Arevalo", "Wichanzao", "Santa Veronica",
                             "Pueblo Libre", "Jerusalen"],
    "El Porvenir":          ["la av. Pumacahua", "Rio Seco", "Miguel Grau", "Nuevo Porvenir", "Alto Mochica"],
    "Alto Trujillo":        ["el sector B", "el sector E", "la zona alta", "el comite 12", "el sector I"],
    "Florencia de Mora":    ["la av. 26 de Marzo", "el mercado", "la zona central", "Villa Hermosa"],
    "Huanchaco":            ["el balneario", "la av. Victor Larco", "El Tropico", "Huanchaquito", "Villa del Mar"],
    "Moche":                ["el centro de Moche", "la carretera a las huacas", "la campina", "Las Delicias"],
    "Laredo":               ["la plaza de Laredo", "la av. Trujillo", "Barraza", "Menocucho"],
    "Salaverry":            ["el puerto", "la av. principal", "Villa del Mar"],
}
ZONA_PESOS = [28, 13, 12, 10, 9, 6, 7, 6, 5, 4]

CANALES = ["facebook", "x", "app_municipal", "libro_reclamaciones", "whatsapp", "redaccion_propia"]
CANAL_PESOS = [34, 12, 18, 8, 10, 18]
ANOTADORES = ["M. Azcarate", "R. Candiotti", "A. Del Portal", "H. Arteaga"]

# ---------------------------------------------------------------- nucleos por categoria y gravedad
NUCLEOS = {
"C1": {
 "grave": ["hay un forado enorme en {r}", "se hundio la pista en {r}", "se abrio un hueco profundo en {r}",
           "hay una zanja abierta y sin señalizar en {r}", "la vereda de {r} esta levantada de golpe",
           "el bache de {r} ya es un crater", "se desprendio todo el asfalto en {r}",
           "quedo un hueco destapado despues de la obra en {r}", "hay un desnivel bravo en la pista de {r}",
           "colapso parte de la calzada en {r}"],
 "moderado": ["hay un bache mediano en {r}", "la pista de {r} esta toda deteriorada",
              "la vereda frente a {r} esta rota", "el pasaje de {r} sigue sin asfaltar",
              "hay varios huecos regados en {r}", "las veredas de {r} estan hundidas en varios tramos",
              "la pista de {r} esta parchada por todos lados", "el asfalto de {r} se esta levantando",
              "la berma de {r} esta destrozada", "la pista de {r} se llena de agua cuando llueve"],
 "leve": ["la vereda de {r} tiene rajaduras finitas", "el sardinel de {r} esta descascarado",
          "la pista de {r} necesita mantenimiento preventivo", "la vereda de {r} esta despintada",
          "hay unas grietas chiquitas en la pista de {r}", "las juntas de la vereda de {r} estan abiertas"],
},
"C2": {
 "grave": ["hay un cable colgando bien bajito en {r}", "hay un cable caido en {r}",
           "el poste de {r} tiene el cable pelado", "se vino abajo el poste de {r}",
           "cuelgan cables sueltos sobre la vereda de {r}", "el poste de {r} esta inclinado y a punto de caerse",
           "el poste de {r} echa chispas", "los cables de {r} quedaron tirados en el suelo",
           "hay un cable pelado al alcance de la mano en {r}", "chisporrotea la conexion del poste de {r}"],
 "moderado": ["el poste de {r} esta apagado", "toda la cuadra de {r} esta a oscuras",
              "la luminaria del parque de {r} esta quemada", "no prende el alumbrado de {r}",
              "se quedo sin luz la vereda de {r}", "las luminarias de {r} no encienden",
              "el alumbrado de {r} lleva dias sin funcionar", "la esquina de {r} quedo totalmente oscura",
              "apagaron el alumbrado de {r} y no lo repusieron"],
 "leve": ["el foco del poste de {r} parpadea", "la luminaria de {r} alumbra muy poquito",
          "la luminaria de {r} esta sucia", "el poste de {r} tiene la tapa del tablero suelta",
          "la luz de {r} prende un poco tarde"],
},
"C3": {
 "grave": ["el desague esta rebalsando en {r}", "hay un buzon destapado en {r}",
           "hay una fuga fuerte de agua en {r}", "el buzon de {r} esta abierto y sin señalizacion",
           "corren aguas servidas por la vereda de {r}", "se rompio la matriz en {r}",
           "el agua sale a chorros en {r}", "el desague de {r} rebalso hasta la pista",
           "quedo el buzon de {r} sin tapa", "se socavo la pista por la fuga en {r}"],
 "moderado": ["se atoro el desague del pasaje de {r}", "hay una fuga de agua en la vereda de {r}",
              "el desague de {r} se atora cada semana", "baja muy poquita agua en {r}",
              "el agua sale turbia en {r}", "se empoza el agua en {r}",
              "hay mal olor a desague en {r}", "la presion del agua en {r} esta bajisima",
              "gotea permanentemente la conexion de {r}"],
 "leve": ["el buzon de {r} esta hundido unos centimetros", "la tapa del buzon de {r} esta floja y suena",
          "la tapa del buzon de {r} quedo mal nivelada", "hay una humedad en la vereda de {r}",
          "la caja de agua de {r} esta sin tapa pero es superficial"],
},
"C4": {
 "grave": ["hay una montaña de basura en {r}", "estan quemando basura en {r}",
           "se formo un punto critico de basura en {r}", "hay basura con desmonte y animales muertos en {r}",
           "botan desmonte al canal de {r}", "la basura de {r} ya atrajo ratas y moscas",
           "hay desechos de construccion tapando media via en {r}", "estan botando residuos de un taller en {r}"],
 "moderado": ["el camion de la basura no pasa por {r}", "hay desmonte tirado en {r}",
              "se acumula basura en la esquina de {r}", "el contenedor de {r} esta rebalsando",
              "hay bolsas rotas regadas en la vereda de {r}", "no recogen la basura de {r} desde hace dias",
              "la gente bota basura a cualquier hora en {r}", "quedo el desmonte de una obra en {r}"],
 "leve": ["hay unas bolsas de basura en la esquina de {r}", "el tacho del parque de {r} esta lleno",
          "hay papeles y botellas regados en {r}", "quedaron restos de poda en la vereda de {r}"],
},
"C5": {
 "grave": ["hay un arbol a punto de caerse en el parque de {r}",
           "los juegos del parque de {r} tienen fierros expuestos",
           "quedo una rama grande colgando en el parque de {r}", "el columpio del parque de {r} esta partido",
           "se cayo un arbol sobre la vereda del parque de {r}", "el tobogan del parque de {r} esta roto y con puntas",
           "el arbol de {r} tiene las raices levantadas y se inclina sobre la vereda"],
 "moderado": ["el parque de {r} esta seco", "los juegos infantiles del parque de {r} estan oxidados",
              "el parque de {r} esta lleno de maleza", "no hacen mantenimiento de las areas verdes de {r}",
              "no riegan el parque de {r}", "las plantas del parque de {r} se estan muriendo",
              "el parque de {r} quedo sin cerco y entran los perros", "faltan podar los arboles de {r}"],
 "leve": ["el pasto del parque de {r} esta crecidisimo", "las bancas del parque de {r} estan despintadas",
          "la jardinera de {r} quedo pelada despues de la poda", "el letrero del parque de {r} esta viejo",
          "falta pintar las rejas del parque de {r}"],
},
"C6": {
 "grave": ["el semaforo del cruce de {r} esta apagado", "el semaforo de {r} quedo en intermitente",
           "se cayo la señal de pare de {r}", "el semaforo peatonal de {r} no funciona",
           "no hay ningun semaforo operativo en el cruce de {r}", "el semaforo de {r} marca verde en los dos sentidos",
           "quedo tapada la señal de pare de {r}", "el semaforo de {r} se apaga y prende solo"],
 "moderado": ["el semaforo peatonal de {r} da muy poco tiempo para cruzar",
              "falta un reductor de velocidad en {r}", "la señal de transito de {r} esta doblada",
              "no hay señalizacion en el cruce de {r}", "el semaforo de {r} se demora muchisimo en cambiar",
              "falta señalizar el paradero de {r}", "la señal de {r} quedo tapada por un arbol"],
 "leve": ["el pintado de la linea peatonal de {r} esta borrado", "la señal con el nombre de la calle de {r} esta torcida",
          "las lineas de estacionamiento de {r} estan desgastadas", "el poste de la señal de {r} esta oxidado",
          "falta repintar el crucero peatonal de {r}"],
},
}

DETALLES = {
"C1": {"grave": ["ya se cayeron dos motos esta semana", "un taxi rompio la llanta ahi mismo",
                 "una señora se tropezo y se fracturo la muñeca", "los carros lo esquivan de golpe y casi chocan",
                 "de noche no se ve nada", "cualquiera se mata ahi", "ya hubo un accidente"],
       "moderado": ["cada vez esta mas grande", "parece trocha", "no se puede pasar con el coche del bebe",
                    "cuando llueve se vuelve puro lodo", "los mototaxis se tienen que desviar",
                    "ya incomoda caminar", "da pena el carro"],
       "leve": ["es mas tema de presentacion", "todavia no molesta", "conviene atenderlo antes que crezca",
                "no es urgente"]},
"C2": {"grave": ["cualquiera se puede enganchar", "esta a la altura de la cabeza", "echa chispas cuando llueve",
                 "hay riesgo de electrocucion", "un perro ya se electrocuto ahi", "da miedo pasar por debajo"],
       "moderado": ["da miedo pasar de noche", "la calle esta oscurisima", "ya se llevaron un celular ahi",
                    "no se ve nada a partir de las siete", "ya reportamos a la empresa y nada"],
       "leve": ["alumbra pero poquito", "no es urgente", "seria bueno que lo revisen en la proxima ronda"]},
"C3": {"grave": ["todo apesta", "un carro casi se mete adentro", "ya socavo la pista",
                 "el agua se mete a las casas", "es un foco infeccioso", "hay riesgo de que alguien caiga"],
       "moderado": ["el agua se empoza y huele mal", "se desperdicia agua todo el dia",
                    "ya reportamos varias veces", "no alcanza ni para llenar el tanque",
                    "sale con tierra", "es incomodo pero se puede vivir"],
       "leve": ["todavia no molesta", "conviene revisarlo", "es un detalle nomas"]},
"C4": {"grave": ["ya hay ratas y perros escarbando", "el humo entra a las casas", "es un foco infeccioso",
                 "el olor es insoportable", "ya se esta tapando el canal", "hay moscas por todos lados"],
       "moderado": ["los carros tienen que esquivar", "los perros abren las bolsas en la noche",
                    "se acumula todos los dias", "ya lleva varios dias ahi", "afea toda la cuadra"],
       "leve": ["recien de ayer pero mejor avisar", "no es urgente", "conviene vaciarlo"]},
"C5": {"grave": ["un niño se puede cortar", "esta inclinado sobre donde juegan", "va a pasar una desgracia",
                 "si cae le puede caer encima a alguien", "los fierros estan oxidados y filudos"],
       "moderado": ["da pena verlo", "ya se meten a tomar de noche", "las plantas se estan secando",
                    "los juegos ya no se pueden usar", "nadie hace mantenimiento hace meses"],
       "leve": ["ya no se puede ni caminar por el pasto", "es tema de presentacion", "no corre prisa"]},
"C6": {"grave": ["los carros pasan como locos", "ya hubo un choque esta semana", "van a atropellar a alguien",
                 "nadie respeta el cruce", "es un cruce peligrosisimo", "los carros no frenan"],
       "moderado": ["se hace cola larga", "los carros corren demasiado", "no se entiende que indica",
                    "no se sabe quien pasa primero", "hay que cruzar corriendo"],
       "leve": ["casi no se ve", "es un detalle de mantenimiento", "no es urgente"]},
}

AGRAVANTE_VULNERABLE = [
 "por ahi pasan los niños del colegio", "justo al frente hay un colegio",
 "por ahi cruzan los escolares a la hora de salida", "al lado hay una posta medica",
 "por esa vereda caminan los ancianos del asilo", "es la ruta de los chicos del colegio",
 "los niños juegan al costado", "ahi mismo funciona un nido",
]

INTROS = ["", "", "", "", "", "buenos dias, ", "buenas tardes, ", "por favor ", "señores de la muni, ",
          "denuncio que ", "quiero reportar que ", "alguien puede ver que ", "xfa ", "ya es el colmo, ",
          "otra vez ", "reitero mi reclamo, ", "hace {d} dias que ", "desde hace {d} dias ",
          "buen dia, ", "vecinos de la zona reportamos que "]

CIERRES = ["", "", "", "", "", " nadie viene a ver", " por favor atiendan", " ya reclamamos varias veces",
           " urge una solucion", " gracias", " hasta cuando", " atiendan por favor", " espero respuesta",
           " el vecindario ya se canso", " lleva {d} dias asi", " van {d} dias y nada",
           " ojala esta vez manden a alguien", " ya no sabemos a quien acudir"]

SINONIMOS = {
 "carros": ["carros", "autos", "vehiculos"],
 "niños": ["niños", "chicos", "escolares"],
 "peligro": ["peligro", "riesgo"],
 "vereda": ["vereda", "acera"],
 "muni": ["muni", "municipalidad", "municipio"],
}
REEMPLAZOS_TIPEO = [(" que ", " q "), (" por favor", " xfa"), (" para ", " pa "), (" porque ", " xq "),
                    ("tambien", "tmb"), (" muy ", " re "), ("esta ", "sta ")]
TILDES = [("dias", "días"), ("esta ", "está "), ("desague", "desagüe"), ("semaforo", "semáforo"),
          ("señalizacion", "señalización"), ("mas ", "más "), ("camion", "camión"), ("ovalo", "óvalo"),
          ("arbol", "árbol"), ("peligrosisimo", "peligrosísimo")]

def sinonimizar(t):
    for base, opciones in SINONIMOS.items():
        if base in t and random.random() < 0.5:
            t = t.replace(base, random.choice(opciones), 1)
    return t

def acentuar(t):
    if random.random() < 0.45:
        for a, b in TILDES:
            t = t.replace(a, b)
    return t

def ensuciar(t):
    if random.random() < 0.35:
        a, b = random.choice(REEMPLAZOS_TIPEO)
        t = t.replace(a, b, 1)
    if random.random() < 0.15:
        t = (t.replace(",", ",,", 1) if "," in t else t + "!!")
    if random.random() < 0.10:
        t = t.upper()
    if random.random() < 0.15:
        t = t + "..."
    if random.random() < 0.08:
        t = t.replace(" ", "  ", 1)
    return t

PAL_RIESGO = ["peligro", "riesgo", "accidente", "se cayo", "se mata", "desgracia", "atropell", "choque",
              "urge", "urgente", "chispas", "electrocu", "infeccios", "fractur", "miedo", "se voltea"]
PAL_MENORES = ["niño", "niños", "chicos", "colegio", "escolar", "escolares", "nido", "anciano", "asilo", "bebe"]

def normaliza(s):
    s = s.lower()
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def bandera(texto, palabras):
    t = normaliza(texto)
    return int(any(normaliza(p) in t for p in palabras))

CUOTAS = {"C1": 110, "C2": 85, "C3": 90, "C4": 95, "C5": 60, "C6": 60}
MEZCLA_GRAVEDAD = ["grave"] * 32 + ["moderado"] * 44 + ["leve"] * 24

CATEGORIAS = {"C1": "C1 Vias y veredas", "C2": "C2 Alumbrado publico", "C3": "C3 Agua y desague",
              "C4": "C4 Residuos solidos", "C5": "C5 Areas verdes y parques",
              "C6": "C6 Señalizacion y semaforos"}

def construir(cod, gravedad, referencia, dias):
    partes = [random.choice(NUCLEOS[cod][gravedad]).format(r=referencia)]
    if random.random() < 0.80:
        partes.append(random.choice(DETALLES[cod][gravedad]))
    prioridad = {"grave": "alta", "moderado": "media", "leve": "baja"}[gravedad]
    if gravedad == "moderado" and random.random() < 0.30:
        partes.append(random.choice(AGRAVANTE_VULNERABLE))
        if random.random() < 0.60:
            prioridad = "alta"
    elif gravedad == "grave" and random.random() < 0.25:
        partes.append(random.choice(AGRAVANTE_VULNERABLE))
    elif gravedad == "leve" and dias > 20 and random.random() < 0.35:
        prioridad = "media"
    texto = ", ".join(partes)
    texto = random.choice(INTROS).format(d=dias) + texto + random.choice(CIERRES).format(d=dias)
    return ensuciar(acentuar(sinonimizar(texto))).strip(), prioridad

filas, id_actual, fecha_base = [], 1, date(2025, 10, 1)
for cod, cuota in CUOTAS.items():
    for i in range(cuota):
        gravedad = random.choice(MEZCLA_GRAVEDAD)
        zona = random.choices(list(ZONAS.keys()), weights=ZONA_PESOS, k=1)[0]
        referencia = random.choice(ZONAS[zona])
        dias = {"grave": random.choice([0, 1, 1, 2, 2, 3, 4, 5]),
                "moderado": random.choice([2, 3, 5, 7, 8, 10, 12, 15]),
                "leve": random.choice([5, 10, 15, 20, 25, 30, 45, 60])}[gravedad]
        texto, prioridad = construir(cod, gravedad, referencia, dias)
        filas.append({"id_reporte": id_actual, "texto_reporte": texto,
                      "canal": random.choices(CANALES, weights=CANAL_PESOS, k=1)[0],
                      "zona": zona, "dias_transcurridos": dias,
                      "fecha_reporte": (fecha_base + timedelta(days=random.randint(0, 330))).isoformat(),
                      "anotador": random.choice(ANOTADORES), "categoria": CATEGORIAS[cod],
                      "prioridad": prioridad, "_cod": cod})
        id_actual += 1

random.shuffle(filas)

# (a) reportes mixtos
for fila in filas[:26]:
    otro = random.choice([c for c in CUOTAS if c != fila["_cod"]])
    extra = random.choice(NUCLEOS[otro][random.choice(["moderado", "leve"])]).format(
        r=random.choice(ZONAS[fila["zona"]]))
    fila["texto_reporte"] = fila["texto_reporte"] + " y ademas " + extra

# (b) reportes vagos o muy cortos
VAGOS = ["arreglen {r} por favor", "hay un problema serio en {r}", "en {r} todo esta destrozado",
         "vengan a ver {r}", "otra vez lo mismo en {r}", "{r} esta en pesimo estado",
         "nadie atiende {r}", "sigue igual {r}"]
for fila in filas[26:64]:
    fila["texto_reporte"] = random.choice(VAGOS).format(r=random.choice(ZONAS[fila["zona"]]))

# (c) desacuerdo de anotadores en prioridad (nunca se baja una alta)
ORDEN = ["baja", "media", "alta"]
for fila in filas[64:99]:
    if fila["prioridad"] != "alta":
        fila["prioridad"] = ORDEN[min(ORDEN.index(fila["prioridad"]) + 1, 2)]

# (d) categorias discutibles
CONFUSIONES = {"C2 Alumbrado publico": "C6 Señalizacion y semaforos",
               "C6 Señalizacion y semaforos": "C1 Vias y veredas",
               "C1 Vias y veredas": "C3 Agua y desague",
               "C4 Residuos solidos": "C5 Areas verdes y parques",
               "C5 Areas verdes y parques": "C4 Residuos solidos",
               "C3 Agua y desague": "C1 Vias y veredas"}
for fila in filas[99:114]:
    fila["categoria"] = CONFUSIONES[fila["categoria"]]

for fila in filas:
    t = fila["texto_reporte"]
    fila["longitud_texto"] = len(t.split())
    fila["menciona_riesgo"] = bandera(t, PAL_RIESGO)
    fila["menciona_menores"] = bandera(t, PAL_MENORES)
    del fila["_cod"]

filas.sort(key=lambda f: f["id_reporte"])

COLUMNAS = ["id_reporte", "texto_reporte", "canal", "zona", "longitud_texto", "menciona_riesgo",
            "menciona_menores", "dias_transcurridos", "fecha_reporte", "anotador", "categoria", "prioridad"]
with open("/mnt/user-data/outputs/reportes_ciudadanos_trujillo_2026.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLUMNAS, extrasaction="ignore")
    w.writeheader(); w.writerows(filas)

print(f"Registros: {len(filas)} | textos unicos: {len(set(f['texto_reporte'] for f in filas))}")
for campo in ["categoria", "prioridad"]:
    print(f"\n{campo}:")
    for v in sorted(set(f[campo] for f in filas)):
        print(f"  {v}: {sum(1 for f in filas if f[campo] == v)}")
print(f"\nLongitud media: {sum(f['longitud_texto'] for f in filas)/len(filas):.1f} palabras")

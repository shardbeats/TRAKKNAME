"""Seed data: English/Spanish word banks (verbs, adjectives, nouns)."""
from __future__ import annotations


EN_VERBS = """run rise fall drift fade burn break float dream wander chase escape breathe move slide glow crash flow strike survive fly dive climb crawl creep glide hover land launch leave return arrive depart vanish appear dance bounce sway swing rock roll spin turn twist shake shiver tremble whisper shout scream cry laugh smile weep mourn pray shine sparkle flicker blaze freeze melt pour rain storm thunder light ignite explode implode erupt collapse crawl race rush sprint stroll strut flex stunt shine grind hustle stack count spend shine ride drive slide cruise coast soar swoop sweep blast bang knock push pull drag lift drop catch throw spin win lose fight bleed heal scar breathe bleed pray vibe ride glide shine""".split()
# pad/trim to exactly 100 unique-ish


# pad/trim to exactly 100 unique-ish
EN_VERBS = (EN_VERBS + ["haunt","linger","echo","beckon","summon","conjure","bless","curse","crave","hunger","thirst","devour","taste","touch","hold","release","surrender","conquer","reign","remember","forget","forgive","promise","confess"])[:100]


EN_ADJECTIVES = """midnight broken savage silent neon cold lost golden reckless velvet dark electric lonely wild restless frozen heavy toxic sacred hollow royal faded jaded lucid vivid hazy smoky misty cloudy stormy rainy sunny blazing icy frosty velvet satin silk chrome platinum diamond crystal marble stone iron steel bronze copper ruby emerald sapphire onyx ivory ebony crimson scarlet violet indigo amber honey sugar bitter sweet sour salty spicy haunted cursed blessed lucky unlucky lonely crowded empty hollow vacant secret hidden forbidden sacred profane ancient modern future past timeless endless infinite finite fragile strong soft hard smooth rough sharp dull blunt bright dim glowing radiant shining sparkling glittering shimmering flickering burning freezing melting floating sinking soaring crashing silent loud quiet noisy calm chaotic peaceful violent gentle brutal tender cruel kind wicked holy sinful pure dirty clean stained midnight ultraviolet infrared cosmic astral lunar solar stellar ocean desert urban rural rusted polished cracked shattered mended woven twisted braided brazen timid bold brave meek proud humble lavish modest feral tamed feral saintly sinful divine mortal eternal fleeting lasting faded vivid unspoken unsung unseen unknown famous nameless numbered countless reckless careful wild tame""".split()


EN_ADJECTIVES = list(dict.fromkeys(EN_ADJECTIVES))[:150]
while len(EN_ADJECTIVES) < 150:
    EN_ADJECTIVES += [f"after{w}" for w in ["glow","hours","dark","light","rain","dusk","dawn","mid","night"]]


EN_ADJECTIVES = EN_ADJECTIVES[:150]


EN_NOUNS = """pressure dreams nights shadows ritual city motion fire money ghost thunder rain desire echo vision memory streets diamonds danger silence nights lights smoke mirrors crown throne block hood avenue boulevard freeway highway church temple chapel altar prayer hymn choir velvet satin silk denim leather chrome steel gold silver platinum ice frost snow storm cloud fog mist dust ash ember flame spark flash bolt wave tide ocean river lake stream desert dune canyon valley mountain peak forest garden rose thorn vine wine honey milk sugar salt pepper silk thunder lightning hurricane tornado quake static noise signal frequency wave channel static vinyl tape record needle groove bass drum snare hat kick snare melody harmony chord rhythm tempo swing bounce groove loop sample verse hook bridge outro intro anthem ballad hymn lullaby elegy ode saga myth legend fable omen prophecy curse blessing spell potion venom honey nectar wine rose lotus orchid iris dawn dusk midnight noon morning evening autumn winter spring summer ghost phantom spirit soul heart mind body blood bone skin tear sweat scar wound crown jewel gem pearl ruby diamond gold chain whip car ghost rider driver pilot captain king queen prince princess knight bishop rook pawn ace joker thief hustler player dealer winner loser lover fighter dreamer believer sinner saint angel demon devil monster beast wolf snake dove raven crow eagle hawk falcon lion tiger panther leopard jaguar cobra viper rose thorn crown flame night light star moon sun sky heaven hell purgatory eden babel zion mecca oasis mirage comet meteor nova nebula galaxy cosmos orbit planet saturn venus mars jupiter mercury neon chrome velvet static fever rush crush lust trust faith doubt hope fear pain pleasure bliss ache throb pulse beat tempo swing drip splash wave flood drought famine feast hunger thirst craving urge itch scratch scar kiss hug touch glance stare gaze wink smile frown tear laugh cry sigh breath breeze gust storm calm chaos order cipher code key lock chain rope wire cable signal static noise voice tone echo reverb delay loop tape vinyl wax wax gold ice drip sauce motion pressure pain glory fame fortune fate destiny karma luck chance risk gamble bet pot jackpot vault safe haven harbor shelter home house crib pad loft suite villa mansion castle palace shack alley street road block corner avenue strip lane path trail track route passport ticket visa stamp letter note memo diary journal book page chapter verse psalm mantra chant prayer wish dream hope plan plot scheme move play game set match round bout fight war battle siege storm raid heist lick score bag pack bundle stash vault reign crown throne kingdom empire dynasty era age epoch season hour minute moment second breath heartbeat pulse wave tide phase stage light shadow shade gloom gleam glow glint spark flare blaze inferno wildfire bonfire candle lamp lantern torch beacon lighthouse tower spire steeple bridge tunnel gate door window wall floor roof ceiling skyline horizon vista view scene sight vision dream mirage fantasy fable legend myth saga story tale yarn lore chronicle anthem hymn psalm ode elegy verse chorus hook bridge melody song tune jam joint banger slapper heater knock bop anthem classic timeless gem jewel treasure chest vault prize trophy medal ribbon badge honor glory fame shine glow light""".split()


EN_NOUNS = list(dict.fromkeys(EN_NOUNS))[:200]
while len(EN_NOUNS) < 200:
    EN_NOUNS += ["mirage","halo","onset","afterglow","nightfall","daybreak","crossroads","ultraviolet"]


EN_NOUNS = EN_NOUNS[:200]


ES_VERBS = """corre sube cae flota quema rompe sueña vaga persigue escapa respira mueve desliza brilla choca fluye golpea sobrevive vuela sumerge escala repta acecha planea aterriza despega parte regresa llega desaparece aparece baila rebota mece gira rueda tiembla susurra grita llora ríe sonríe reza brilla parpadea arde congela derrite llueve truena ilumina enciende explota colapsa corre apresura pasea presume brilla lucha sangra sana recuerda olvida perdona promete confiesa jura vela canta llora gime habla calla mira observa toca abraza suelta rinde conquista reina late vibra rueda fluye sueña anhela desea teme ama odia extraña busca encuentra pierde gana juega apuesta quema enciende apaga prende moja seca pinta borra escribe canta grita corre salta baila gira brilla quema""".split()


ES_VERBS = list(dict.fromkeys(ES_VERBS))[:100]
while len(ES_VERBS) < 100:
    ES_VERBS += ["navega","cruza","enciende","apaga","despierta","duerme"]


ES_VERBS = ES_VERBS[:100]


ES_ADJECTIVES = """medianoche roto salvaje silencioso neón frío perdido dorado temerario aterciopelado oscuro eléctrico solitario inquieto helado pesado tóxico sagrado hueco real marchito lúcido vívido brumoso ahumado tormentoso lluvioso ardiente gélido cromado platino cristal mármol hierro acero bronce cobre rubí esmeralda zafiro ónix marfil ébano carmesí violeta ámbar miel dulce amargo prohibido maldito bendito eterno infinito frágil fuerte suave áspero afilado brillante radiante destellante ardiendo flotante callado ruidoso tranquilo caótico pacífico violento tierno brutal cruel santo puro sucio limpio antiguo moderno futuro eterno fugaz duradero oculto secreto libre preso bravo manso feroz divino mortal nocturno diurno urbano rural oxidado pulido roto etéreo astral lunar solar cósmico profundo leve denso claro turbio dulce amargo eterno breve largo corto alto bajo grande pequeño inmenso leve grave agudo sordo ciego mudo frío caliente tibio fresco seco mojado eterno oscuro claro pálido intenso suave feroz manso bravo eterno infinito fugaz etéreo oscuro claro roto libre loco cuerdo triste feliz solo pleno vacío lleno roto eterno""".split()


ES_ADJECTIVES = list(dict.fromkeys(ES_ADJECTIVES))
# Curated extension with real title-worthy adjectives (never placeholders).
ES_ADJECTIVES += ["sombrío", "tenebroso", "pasional", "frenético", "indomable",
    "voraz", "letal", "celestial", "infernal", "angelical", "diabólico", "magnético",
    "vibrante", "hermoso", "bello", "colosal", "épico", "legendario", "mágico",
    "rebelde", "errante", "íntimo", "único"]
ES_ADJECTIVES = list(dict.fromkeys(ES_ADJECTIVES))[:150]

# Spanish nouns with gender metadata: (word, gender, number)


# Spanish nouns with gender metadata: (word, gender, number)
ES_NOUNS_RAW: list[tuple[str, str, str]] = [
    ("noche","feminine","singular"),("sombra","feminine","singular"),("fuego","masculine","singular"),
    ("calle","feminine","singular"),("sueño","masculine","singular"),("deseo","masculine","singular"),
    ("ruido","masculine","singular"),("silencio","masculine","singular"),("luces","feminine","plural"),
    ("presión","feminine","singular"),("veneno","masculine","singular"),("hielo","masculine","singular"),
    ("oro","masculine","singular"),("fantasma","masculine","singular"),("ritual","masculine","singular"),
    ("ciudad","feminine","singular"),("movimiento","masculine","singular"),("dinero","masculine","singular"),
    ("trueno","masculine","singular"),("lluvia","feminine","singular"),("eco","masculine","singular"),
    ("visión","feminine","singular"),("memoria","feminine","singular"),("peligro","masculine","singular"),
    ("corona","feminine","singular"),("trono","masculine","singular"),("barrio","masculine","singular"),
    ("avenida","feminine","singular"),("iglesia","feminine","singular"),("altar","masculine","singular"),
    ("oración","feminine","singular"),("coro","masculine","singular"),("espejos","masculine","plural"),
    ("humo","masculine","singular"),("tormenta","feminine","singular"),("niebla","feminine","singular"),
    ("polvo","masculine","singular"),("ceniza","feminine","singular"),("llama","feminine","singular"),
    ("chispa","feminine","singular"),("ola","feminine","singular"),("marea","feminine","singular"),
    ("océano","masculine","singular"),("río","masculine","singular"),("desierto","masculine","singular"),
    ("montaña","feminine","singular"),("bosque","masculine","singular"),("rosa","feminine","singular"),
    ("vino","masculine","singular"),("miel","feminine","singular"),("bajo","masculine","singular"),
    ("tambor","masculine","singular"),("melodía","feminine","singular"),("armonía","feminine","singular"),
    ("ritmo","masculine","singular"),("verso","masculine","singular"),("coro","masculine","singular"),
    ("himno","masculine","singular"),("elegía","feminine","singular"),("mito","masculine","singular"),
    ("leyenda","feminine","singular"),("profecía","feminine","singular"),("hechizo","masculine","singular"),
    ("cielo","masculine","singular"),("infierno","masculine","singular"),("paraíso","masculine","singular"),
    ("oasis","masculine","singular"),("cometa","masculine","singular"),("galaxia","feminine","singular"),
    ("cosmos","masculine","singular"),("planeta","masculine","singular"),("estrella","feminine","singular"),
    ("luna","feminine","singular"),("sol","masculine","singular"),("fiebre","feminine","singular"),
    ("deseo","masculine","singular"),("fe","feminine","singular"),("duda","feminine","singular"),
    ("esperanza","feminine","singular"),("miedo","masculine","singular"),("dolor","masculine","singular"),
    ("placer","masculine","singular"),("latido","masculine","singular"),("pulso","masculine","singular"),
    ("golpe","masculine","singular"),("ola","feminine","singular"),("voz","feminine","singular"),
    ("tono","masculine","singular"),("llave","feminine","singular"),("cadena","feminine","singular"),
    ("refugio","masculine","singular"),("hogar","masculine","singular"),("casa","feminine","singular"),
    ("castillo","masculine","singular"),("palacio","masculine","singular"),("callejón","masculine","singular"),
    ("camino","masculine","singular"),("ruta","feminine","singular"),("carta","feminine","singular"),
    ("diario","masculine","singular"),("libro","masculine","singular"),("capítulo","masculine","singular"),
    ("guerra","feminine","singular"),("batalla","feminine","singular"),("tesoro","masculine","singular"),
    ("gloria","feminine","singular"),("fama","feminine","singular"),("fortuna","feminine","singular"),
    ("destino","masculine","singular"),("karma","masculine","singular"),("suerte","feminine","singular"),
    ("apuesta","feminine","singular"),("reino","masculine","singular"),("era","feminine","singular"),
    ("época","feminine","singular"),("hora","feminine","singular"),("momento","masculine","singular"),
    ("aliento","masculine","singular"),("vela","feminine","singular"),("faro","masculine","singular"),
    ("puente","masculine","singular"),("puerta","feminine","singular"),("ventana","feminine","singular"),
    ("horizonte","masculine","singular"),("vista","feminine","singular"),("canción","feminine","singular"),
    ("himno","masculine","singular"),("verso","masculine","singular"),("joya","feminine","singular"),
    ("ángel","masculine","singular"),("demonio","masculine","singular"),("bestia","feminine","singular"),
    ("lobo","masculine","singular"),("serpiente","feminine","singular"),("paloma","feminine","singular"),
    ("cuervo","masculine","singular"),("águila","feminine","singular"),("león","masculine","singular"),
    ("rosa","feminine","singular"),("espina","feminine","singular"),("llama","feminine","singular"),
    ("amor","masculine","singular"),("odio","masculine","singular"),("pecado","masculine","singular"),
    ("santo","masculine","singular"),("alma","feminine","singular"),("corazón","masculine","singular"),
    ("sangre","feminine","singular"),("lágrima","feminine","singular"),("cicatriz","feminine","singular"),
    ("beso","masculine","singular"),("abrazo","masculine","singular"),("mirada","feminine","singular"),
    ("rey","masculine","singular"),("reina","feminine","singular"),("príncipe","masculine","singular"),
    ("caballero","masculine","singular"),("ladrón","masculine","singular"),("amante","masculine","singular"),
    ("soñador","masculine","singular"),("creyente","masculine","singular"),("arena","feminine","singular"),
    ("mar","masculine","singular"),("selva","feminine","singular"),("nieve","feminine","singular"),
    ("invierno","masculine","singular"),("otoño","masculine","singular"),("primavera","feminine","singular"),
    ("verano","masculine","singular"),("amanecer","masculine","singular"),("atardecer","masculine","singular"),
    ("medianoche","feminine","singular"),("mediodía","masculine","singular"),("sueños","masculine","plural"),
    ("sombras","feminine","plural"),("noches","feminine","plural"),("diamantes","masculine","plural"),
    ("fantasmas","masculine","plural"),("cadenas","feminine","plural"),("flores","feminine","plural"),
    ("estrellas","feminine","plural"),("olas","feminine","plural"),("voces","feminine","plural"),
    ("pasos","masculine","plural"),("gritos","masculine","plural"),("secretos","masculine","plural"),
    ("deseos","masculine","plural"),("pecados","masculine","plural"),("milagros","masculine","plural"),
    ("tardes","feminine","plural"),("mañanas","feminine","plural"),("caminos","masculine","plural"),
    ("puentes","masculine","plural"),("reyes","masculine","plural"),("lobos","masculine","plural"),
    ("rosas","feminine","plural"),("espinas","feminine","plural"),("llamas","feminine","plural"),
    ("corazones","masculine","plural"),("almas","feminine","plural"),("lágrimas","feminine","plural"),
    ("heridas","feminine","plural"),("cicatrices","feminine","plural"),("promesas","feminine","plural"),
    ("mentiras","feminine","plural"),("verdades","feminine","plural"),("historias","feminine","plural"),
    ("canciones","feminine","plural"),("melodías","feminine","plural"),("tambores","masculine","plural"),
    ("trompetas","feminine","plural"),("guitarras","feminine","plural"),("pianos","masculine","plural"),
    ("violines","masculine","plural"),
]
# trim/dedup to >=200


# trim/dedup to >=200
_seen = set(); _esn = []
for w, g, n in ES_NOUNS_RAW:
    if w not in _seen:
        _seen.add(w); _esn.append((w, g, n))


ES_NOUNS_RAW = _esn
assert len(ES_NOUNS_RAW) >= 200, "ES nouns seed fell below 200: add real words, never placeholders"
ES_NOUNS_RAW = ES_NOUNS_RAW[:220]

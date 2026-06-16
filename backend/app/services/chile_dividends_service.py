"""
Servicio de dividendos Chile: solo TradingView (BCS - Bolsa de Chile).
TV cubre acciones locales, internacionales CL y fondos CFI.
Moneda base: CLP. Dividendos USD se convierten con TC USDCLP=X.
"""
import os
import datetime
import requests as http
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from tradingview_scraper.symbols.cal import CalendarScraper
from tradingview_scraper.symbols.overview import Overview

SUPABASE_URL         = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY         = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
TABLE                = "dividendos_chile"
BATCH                = 50


def _norm(t: str) -> str:
    """Normaliza un ticker: mayúsculas, sin espacios extremos,
    guiones y espacios → '_', puntos eliminados.
    Así EMBONOR-A, embonor_a y 'EMBONOR A' se comparan igual."""
    return t.strip().upper().replace("-", "_").replace(" ", "_").replace(".", "")


# Whitelist de tickers permitidos para Chile (BCS).
# Todos los valores están pre-normalizados con _norm().
# TV usa '_' donde la Bolsa usa '-' o espacios (EMBONOR_A, SQM_A, AZUL_AZUL).
# Sufijo CL para internacionales (GOOGLCL, MSFTCL...); la red de seguridad
# en _in_whitelist lo maneja si TV omite el sufijo.
_RAW_WHITELIST = [
    "MMMCL", "HABITAT", "CUPRUM", "ABTCL", "AAISA", "AESANDES", "PLANVITAL",
    "AGUAS-B", "AGUAS-A", "ALMENDRAL", "GOOGLCL", "GOOGCL", "AMZNCL", "AXPCL",
    "CFIAMDHY-A", "CFIADGHI", "CFIADGHC", "CFIAMDDA-E", "CFIAMDDI-E",
    "CFIAMDVACA", "CFIAMDVACB", "CFIAMDVACC", "CFIAMDVACI", "CFIAMDVACM",
    "CFIAMDVATA", "CFIAMDVAMC", "CFIAMDVAMA", "CFIAMDVASC", "CFIASPCP-E",
    "CFIASPLP-E", "CFIASSCP-E", "CFIASSLP-E", "ANTARCHILE", "AAPLCL",
    "AQUACHILE", "AZUL AZUL", "CHILE", "BCI", "BSANTANDER", "BANCOLOMCL",
    "BAC", "BACCL", "BANVIDA", "CFIBCISCBC", "BESALCO", "CFIBDEUDAI",
    "BICECORP", "BIIBCL", "COLO COLO", "BLUMAR", "BOLSASTGO", "BKNGCL",
    "CFIBTGRRA", "CFIBTGCYFA", "CFIBTGDAPA", "CFIBPDCCHA", "CFIDLDA-E",
    "CFIBPDPA-E", "CFIBTGFGIA", "CFIBTGRCA", "CFISCCH", "CAP", "CATCL",
    "CEMARGOSCL", "CEMENTOS", "CENCOSUD", "CENCOMALLS", "CFINASDAQ",
    "NTGCLGAS", "CVXCL", "CFIMCITI", "CINTAC", "CSCOCL", "CCL",
    "LAS CONDES", "EMBONOR-A", "EMBONOR-B", "COLBUN", "CCU", "CAMANCHACA",
    "VAPORES", "CIC", "CFICOMDPB", "CFICGGLOEB", "COSTCL", "CRISTALES",
    "CRUZADOS", "DAVIVIENCL", "CONDES-OSA", "HITES-OSA", "NITRA-OSA",
    "NORTE-OSA", "OROBCO-OSA", "EBAYCL", "EISA", "ANDINA-A", "ANDINA-B",
    "EDELMAG", "PEHUENCHE", "NUEVAPOLAR", "ENTEL", "CMPC", "COPEC",
    "HITES", "LIPIGAS", "TRICOT", "ENAEX", "ENELAM", "ENELCHILE",
    "ENELDXCH", "ENELGXCH", "ECL", "ENJOY", "CFISP500", "XOMCL",
    "CFIAFESA", "FBCL", "FALABELLA", "CFIBCLATCP", "CFIETFLP", "CFIETFIPSA",
    "CFMDIVO", "CFIDHS1", "CFIDHS2-A", "CFIAMDDC-E", "CFIBCDALTP",
    "CFICARVA-E", "CFIBCHBLEN", "CFIAMDVAMD", "CFIIMSCLI", "CFIBCHDALT",
    "CFIBCHDECH", "CFIBCHDEGB", "CFIBEDRA-E", "CFIBCHEMEQ", "CFIETFCC",
    "CFIETFCD", "CFIGC", "CFIETFGE", "CFIUSREIT", "CFIBCHUETA",
    "CFIFALCFIW", "CFIFALCEQA", "CFIFALCGLA", "CFIFALCTAC", "CFIBGRESTA",
    "CFINRENTAS", "CFILVFA-L", "CFILVCOR-I", "CFILVCOR-O", "CFILVCOR-A",
    "CFILVDPU-E", "CFILVPARI1", "CFIBCHLCHY", "CFIBACHLAT", "CFIBMPEM-E",
    "CFIBCHMPUS", "CFIBMPEU-E", "CFIBCHMPGB", "CFINVDPR-E", "CFISANDCHA",
    "CFISANTDCA", "CFISANTDLA", "CFISANRVGA", "CFISANTSCA", "CFILEASA",
    "CFIPROYA", "CFITACTI-A", "CFISUAUSE", "CFISUDCHE", "CFIBCHUETA",
    "CFMITNIPSA", "CFMESGIPSA", "PASUR", "FORUS", "FCXCL", "CFIFTRLPP",
    "GASCO", "GECL", "GILDCL", "GRPARGOSCL", "NAVIERA", "NUTRESACL",
    "SECURITY", "HALCL", "HDCL", "HONCL", "HF", "IANSA", "INGEVEC",
    "MANQUEHUE", "INDISA", "INTCCL", "IBMCL", "INVERCAP", "IAM", "ILC",
    "TRICAHUE", "SGOVCL", "TLT CL", "IBB CL", "IBITCL", "DGRO CL",
    "IYMCL", "IYKCL", "IYCCL", "IYECL", "ITBCL", "IYJCL", "IDUCL",
    "IYRCL", "IYZCL", "FXICL", "ICLNCL", "IAUCL", "HDV CL", "HYGCL",
    "LQDCL", "EMB CL", "ACWICL", "AAXJCL", "EPUCL", "EWACL", "EWZCL",
    "ECHCL", "MCHICL", "EFACL", "EEMCL", "EZUCL", "EWQCL", "EWGCL",
    "EWHCL", "INDA CL", "EWICL", "EWJCL", "EWWCL", "EPPCL", "ERUSCL",
    "EWYCL", "EWPCL", "EWTCL", "EWUCL", "IVWCL", "IVVCL", "ILFCL",
    "DVY CL", "IYG CL", "IYFCL", "IYH CL", "IYWCL", "ITAUCL", "JNJCL",
    "JPMCL", "LTM", "MASISA", "CFIMBILA-A", "CFIMBIDA-A", "CFIMBIRF-A",
    "CFIMBDPA-E", "CFIMBIDT-B", "CFIMBIGL-A", "CFIMBIRFUS", "MCDCL",
    "MRKCL", "MSFTCL", "MINERA", "CFIMDCHA", "CFIMDLATAE", "CFIMDCHD",
    "CFIMDCHE", "CFIMDCHI", "CFIMDLIG-A", "CFIMLDLAE", "CFIMLDL-B",
    "CFIMDLIG-I", "CFIIMDLAT", "CFIMLE-A", "CFIMLE-B", "CFIMLDL",
    "CFIMRCLPR", "CFIMRCLP", "CFIMRFIHYA", "CFIMRFIHYB", "CFIMRFHYBE",
    "CFIMRFIIGA", "CFIMRVCHA", "CFIMRBCHAE", "CFIMRVCHAE", "CFIMRVCHE",
    "CFIMRVCHI", "CFIMRVEA", "CFIMRVEC", "CFIMRVIA", "CFIMRVIB",
    "CFIMRVUSAA", "CFIMRVUSAC", "CFIMSC", "CFIMSCAE", "MSCL", "MULTI X",
    "NEMCL", "NKECL", "NITRATOS", "NORTEGRAN", "NUAM", "NVDACL",
    "RENTAS-OSA", "ORCLCL", "ORCL", "PARAUCO", "PAZ", "PEPCL", "PFECL",
    "CFIPIONERO", "CFIPIONAE", "MPLAZA-OSA", "MALLPLAZA", "FROWARD",
    "potasios-a", "potasios-b", "PGCL", "PROVIDA", "VENTANAS", "QCOMCL",
    "CFIQAC", "CFIQRGA", "QUINENCO", "RIPLEY", "SALFACORP", "SALMOCAM",
    "SCHWAGER", "SK", "CFIMSIGLO", "SMU", "ORO BLANCO", "SMSAAM",
    "PUCOBRE", "SQM-A", "SQM-B", "SOCOVESA", "SONDA", "SOQUICOM",
    "SBUXCL", "SURACL", "CFITACPI-E", "CFITACP2-E", "TGTCL", "BACL",
    "KOCL", "DISCL", "UPSCL", "XCL", "UNHCL", "CONCHATORO", "VCL",
    "WALMARTCL", "WATTS", "WFCCL", "ZOFRI",
]

CHILE_TICKER_WHITELIST: frozenset[str] = frozenset(_norm(t) for t in _RAW_WHITELIST)

# Nombres completos por ticker (fuente: whitelist oficial).
# Las claves se pre-normalizan con _norm() para que coincidan con lo que devuelve TV.
_RAW_NOMBRES_CHILE = [
    ("MMMCL",        "3M Company"),
    ("HABITAT",      "A.F.P Habitat S.A"),
    ("CUPRUM",       "A.F.P. Cuprum S.A."),
    ("ABTCL",        "Abbott Laboratories"),
    ("AAISA",        "Administradora Americana de Inversiones"),
    ("AESANDES",     "AES Andes S.A."),
    ("PLANVITAL",    "AFP Planvital"),
    ("AGUAS-B",      "Aguas Andinas"),
    ("AGUAS-A",      "Aguas Andinas S.A."),
    ("ALMENDRAL",    "Almendral S.A"),
    ("GOOGLCL",      "Alphabet Inc. Class A"),
    ("GOOGCL",       "Alphabet Inc. Class C (Google)"),
    ("AMZNCL",       "Amazon.com Inc."),
    ("AXPCL",        "American Express Company"),
    ("CFIAMDHY-A",   "Ameris Deuda Chile Fondo de Inversión, Serie A"),
    ("CFIADGHI",     "Ameris Deuda con Garantía Hipotecaria FI, Serie I"),
    ("CFIADGHC",     "Ameris Deuda con Garantía Hipotecaria FI, Serie C"),
    ("CFIAMDDA-E",   "Ameris Deuda Directa Fondo de Inversión, Serie A"),
    ("CFIAMDDI-E",   "Ameris Deuda Directa Fondo de Inversión, Serie I"),
    ("CFIAMDVACA",   "Ameris DVA All CAP Chile FI, Serie A"),
    ("CFIAMDVACB",   "Ameris DVA All CAP Chile FI, Serie B"),
    ("CFIAMDVACC",   "Ameris DVA All CAP Chile FI, Serie C"),
    ("CFIAMDVACI",   "Ameris DVA All CAP Chile FI, Serie I"),
    ("CFIAMDVACM",   "Ameris DVA All CAP Chile FI, Serie M"),
    ("CFIAMDVATA",   "Ameris DVA Medtech Fund FI, Serie A"),
    ("CFIAMDVAMC",   "Ameris DVA Multiaxis FI, Serie C"),
    ("CFIAMDVAMA",   "Ameris DVA Multiaxis FI, Serie A"),
    ("CFIAMDVASC",   "Ameris DVA Silicon FI, Serie C"),
    ("CFIASPCP-E",   "Ameris Financiamiento Corto Plazo FI, Serie SPCP"),
    ("CFIASPLP-E",   "Ameris Financiamiento Corto Plazo FI, Serie SPLP"),
    ("CFIASSCP-E",   "Ameris Financiamiento Corto Plazo FI, Serie SSCP"),
    ("CFIASSLP-E",   "Ameris Financiamiento Corto Plazo FI, Serie SSLP"),
    ("ANTARCHILE",   "Antarchile S.A"),
    ("AAPLCL",       "Apple Inc"),
    ("AQUACHILE",    "AquaChile"),
    ("AZUL AZUL",    "Azul Azul S.A."),
    ("CHILE",        "Banco de Chile"),
    ("BCI",          "Banco de Crédito e Inversiones"),
    ("BSANTANDER",   "Banco Santander - Chile"),
    ("BANCOLOMCL",   "Bancolombia SA"),
    ("BAC",          "Bank Of America Corp"),
    ("BACCL",        "Bank of America Corp."),
    ("BANVIDA",      "Banvida S.A."),
    ("CFIBCISCBC",   "BCI Small Cap Chile FI, Serie BCI"),
    ("BESALCO",      "Besalco S.A"),
    ("CFIBDEUDAI",   "BICE Deuda Nacional FI, Serie I"),
    ("BICECORP",     "BICECORP S.A."),
    ("BIIBCL",       "Biogen Idec Inc."),
    ("COLO COLO",    "Blanco y Negro S.A."),
    ("BLUMAR",       "Blumar S.A"),
    ("BOLSASTGO",    "Bolsa De Comercio De Santiago"),
    ("BKNGCL",       "Booking Holdings"),
    ("CFIBTGRRA",    "BTG Pactual Renta Residencial FI, Serie A"),
    ("CFIBTGCYFA",   "BTG Pactual Crédito y Facturas FI"),
    ("CFIBTGDAPA",   "BTG Pactual Deuda Activa Plus FI, Serie A"),
    ("CFIBPDCCHA",   "BTG Pactual Deuda Corporativa Chile FI"),
    ("CFIDLDA-E",    "BTG Pactual Deuda Latam Dólar FI, Serie A"),
    ("CFIBPDPA-E",   "BTG Pactual Deuda Privada FI"),
    ("CFIBTGFGIA",   "BTG Pactual Financiamiento con Garantías Inmobiliarias FI, Serie A"),
    ("CFIBTGRCA",    "BTG Pactual Renta Comercial FI"),
    ("CFISCCH",      "BTG Pactual Small Cap Chile FI"),
    ("CAP",          "Cap S.A."),
    ("CATCL",        "Caterpillar Inc."),
    ("CEMARGOSCL",   "Cementos Argos S.A."),
    ("CEMENTOS",     "Cementos Bio-bio S.A."),
    ("CENCOSUD",     "Cencosud S.A."),
    ("CENCOMALLS",   "Cencosud Shopping S.A."),
    ("CFINASDAQ",    "CFI ETF Singular Nasdaq 100"),
    ("NTGCLGAS",     "CGE Gas Natural S.A"),
    ("CVXCL",        "Chevron Corporation"),
    ("CFIMCITI",     "Chile FI Small Cap, Serie P1"),
    ("CINTAC",       "Cintac S.A"),
    ("CSCOCL",       "Cisco Systems, Inc."),
    ("CCL",          "Citigroup, Inc."),
    ("LAS CONDES",   "Clínica Las Condes S.A"),
    ("EMBONOR-A",    "Coca-Cola Embonor S.A."),
    ("EMBONOR-B",    "Coca-Cola Embonor S.A."),
    ("COLBUN",       "Colbun S.A."),
    ("CCU",          "Compañía Cervecería Unidas S.A."),
    ("CAMANCHACA",   "Compañía Pesquera Camanchaca S.A"),
    ("VAPORES",      "Compañía Sud Americana de Vapores S.A."),
    ("CIC",          "Compañías CIC S.A."),
    ("CFICOMDPB",    "Compass Deuda Plus FI, Serie B"),
    ("CFICGGLOEB",   "Compass Global Equity FI, Serie B"),
    ("COSTCL",       "Costco Wholesale Corporation"),
    ("CRISTALES",    "Cristalerias de Chile S.A"),
    ("CRUZADOS",     "Cruzados SADP"),
    ("DAVIVIENCL",   "Davivienda"),
    ("CONDES-OSA",   "Derechos Pref. Clínica las Condes"),
    ("HITES-OSA",    "Derechos Pref. Empresas Hites S.A"),
    ("NITRA-OSA",    "Derechos Pref. Nitratos"),
    ("NORTE-OSA",    "Derechos Pref. Norte Grande S.A"),
    ("OROBCO-OSA",   "Derechos Pref. Oro Blanco"),
    ("EBAYCL",       "Ebay Inc."),
    ("EISA",         "Echeverria, Izquierda S.A"),
    ("ANDINA-A",     "Embotelladora Andina S.A."),
    ("ANDINA-B",     "Embotelladora Andina S.A."),
    ("EDELMAG",      "Empresa Electrica de Magallanes SA"),
    ("PEHUENCHE",    "Empresa Eléctrica Pehuenche S.A"),
    ("NUEVAPOLAR",   "Empresa La Polar S.A."),
    ("ENTEL",        "Empresa Nacional de Telecomunicaciones SA"),
    ("CMPC",         "Empresas CMPC S.A."),
    ("COPEC",        "Empresas COPEC S.A."),
    ("HITES",        "Empresas Hites S.A"),
    ("LIPIGAS",      "Empresas Lipigas S.A."),
    ("TRICOT",       "Empresas Tricot S.A."),
    ("ENAEX",        "Enaex S.A"),
    ("ENELAM",       "Enel Americas S.A."),
    ("ENELCHILE",    "Enel Chile"),
    ("ENELDXCH",     "Enel Distribucion Chile S.A."),
    ("ENELGXCH",     "Enelgxch SI Equity"),
    ("ECL",          "Engie Energia Chile S.A."),
    ("ENJOY",        "Enjoy S.A."),
    ("CFISP500",     "ETF Singular S&P 500"),
    ("XOMCL",        "Exxon Mobil Corporation"),
    ("CFIAFESA",     "F.I Activa FIN. Estructurado, Serie A"),
    ("FBCL",         "Facebook Inc"),
    ("FALABELLA",    "Falabella S.A."),
    ("CFIBCLATCP",   "FI Banchile Deuda Latam Corto Plazo, Serie A"),
    ("CFIETFLP",     "FI ETF Singular Chile Largo Plazo"),
    ("CFIETFIPSA",   "FI ETF Singular IPSA, Serie única"),
    ("CFMDIVO",      "FM ETF It Now S&P/CLX Chile Dividend IND"),
    ("CFIDHS1",      "FI Activa Deuda Hipotecaria con Subsidio Habitacional I"),
    ("CFIDHS2-A",    "FI Activa Deuda Hipotecaria con Subsidio Habitacional II, A"),
    ("CFIAMDDC-E",   "FI Ameris Deuda Directa, Serie C"),
    ("CFIBCDALTP",   "FI Banchile Deuda Alto Rendimiento, Serie P"),
    ("CFICARVA-E",   "FI Capital Advisors Renta Variable Global"),
    ("CFIBCHBLEN",   "FI Chile Blend"),
    ("CFIAMDVAMD",   "FI Compass DVA Multiaxis"),
    ("CFIIMSCLI",    "FI Credicorp Capital Spread Corporativo Local, Serie I"),
    ("CFIBCHDALT",   "FI Deuda Alto Rendimiento"),
    ("CFIBCHDECH",   "FI Deuda Chilena"),
    ("CFIBCHDEGB",   "FI Deuda Global"),
    ("CFIBEDRA-E",   "FI EDR Fund Emerging Credit, Serie A"),
    ("CFIBCHEMEQ",   "FI Emerging Equity, Serie A"),
    ("CFIETFCC",     "FI ETF Singular Chile Corporativo"),
    ("CFIETFCD",     "FI ETF Singular Chile Corta Duración"),
    ("CFIGC",        "FI ETF Singular Global Corporates, Serie I"),
    ("CFIETFGE",     "FI ETF Singular Global Equities"),
    ("CFIUSREIT",    "FI ETF Singular US Real Estate"),
    ("CFIBCHUETA",   "FI USA Equity"),
    ("CFIFALCFIW",   "FI Falcom Chilean Fixed Income, Serie W"),
    ("CFIFALCEQA",   "FI Falcom Global Equity Fund, Serie A"),
    ("CFIFALCGLA",   "FI Falcom Global Strategy Fund, Serie A"),
    ("CFIFALCTAC",   "FI Falcom Tactical Chilean Equities"),
    ("CFIBGRESTA",   "FI Global Real Estate"),
    ("CFINRENTAS",   "FI Independencia Rentas Inmobiliarias"),
    ("CFILVFA-L",    "FI Larrain Vial Facturas"),
    ("CFILVCOR-I",   "FI LarraínVial Deuda Chile, Serie I"),
    ("CFILVCOR-O",   "FI LarraínVial Deuda Chile, Serie O"),
    ("CFILVCOR-A",   "FI LarraínVial Deuda Corporativa"),
    ("CFILVDPU-E",   "FI LarraínVial Deuda Privada"),
    ("CFILVPARI1",   "FI LarraínVial Patio Renta Inmobiliaria"),
    ("CFIBCHLCHY",   "FI Latam Corporate High Yield, Serie A"),
    ("CFIBACHLAT",   "FI Latam Small - Mid Cap"),
    ("CFIBMPEM-E",   "FI Marketplus Emergente"),
    ("CFIBCHMPUS",   "FI Marketplus Estados Unidos"),
    ("CFIBMPEU-E",   "FI Marketplus Europa"),
    ("CFIBCHMPGB",   "FI Marketplus Global"),
    ("CFINVDPR-E",   "FI Nevesa Deuda Privada, Serie R"),
    ("CFISANDCHA",   "FI Santander Deuda Chile, Serie A"),
    ("CFISANTDCA",   "FI Santander Deuda Corporativa Chile, Serie A"),
    ("CFISANTDLA",   "FI Santander Deuda Latam, Serie A"),
    ("CFISANRVGA",   "FI Santander Renta Variable Global, Serie A"),
    ("CFISANTSCA",   "FI Santander Small Cap, Serie A"),
    ("CFILEASA",     "FI Sartor Leasing, Serie A"),
    ("CFIPROYA",     "FI Sartor Proyección, Serie A"),
    ("CFITACTI-A",   "FI Sartor Táctico"),
    ("CFISUAUSE",    "FI SURA Acciones Estados Unidos, Serie E"),
    ("CFISUDCHE",    "FI SURA Deuda Chile Largo Plazo, Serie E"),
    ("CFMITNIPSA",   "Fondo Mutuo ETF IT Now S&P IPSA"),
    ("CFMESGIPSA",   "Fondo Mutuo ETF It Now S&P IPSA ESG"),
    ("PASUR",        "Forestal Constructora y Comercial del Pacifico Sur S.A."),
    ("FORUS",        "Forus S.A"),
    ("FCXCL",        "Freeport-McMoRan Copper & Gold Inc."),
    ("CFIFTRLPP",    "Frontal Trust Cordada Rendimiento C/ LIQ FIP"),
    ("GASCO",        "Gasco S.A"),
    ("GECL",         "General Electric Company"),
    ("GILDCL",       "Gilead Sciences Inc."),
    ("GRPARGOSCL",   "Grupo Argos"),
    ("NAVIERA",      "Grupo Empresas Navieras S.A."),
    ("NUTRESACL",    "Grupo Nutresa S.A."),
    ("SECURITY",     "Grupo Security S.A."),
    ("HALCL",        "Halliburton Company"),
    ("HDCL",         "Home Depot, Inc."),
    ("HONCL",        "Honeywell International Inc."),
    ("HF",           "Hortifrut S.A"),
    ("IANSA",        "Industria Azucarera Nacional"),
    ("INGEVEC",      "Ingevec S.A"),
    ("MANQUEHUE",    "Inmobiliaria Manquehue S.A."),
    ("INDISA",       "Instituto de Diagnostico S.A"),
    ("INTCCL",       "Intel Corporation"),
    ("IBMCL",        "International Business Machines Corporation"),
    ("INVERCAP",     "Invercap S.A"),
    ("IAM",          "Inversiones Aguas Metropolitanas S.A"),
    ("ILC",          "Inversiones La Construcción S.A"),
    ("TRICAHUE",     "Inversiones Tricahue S.A."),
    ("SGOVCL",       "iShares 0-3 Month Treasury Bond ETF"),
    ("TLT CL",       "iShares 20+ Year Treasury Bond ETF"),
    ("IBB CL",       "iShares Biotechnology ETF"),
    ("IBITCL",       "iShares Bitcoin Trust"),
    ("DGRO CL",      "iShares Core Dividend Growth ETF"),
    ("IYMCL",        "iShares Dow Jones U.S. Basic Materials Sector Index Fund"),
    ("IYKCL",        "iShares Dow Jones U.S. Consumer Goods Sector Index Fund"),
    ("IYCCL",        "iShares Dow Jones U.S. Consumer Services Sector Index Fund"),
    ("IYECL",        "iShares Dow Jones U.S. Energy Sector Index Fund ETF"),
    ("ITBCL",        "iShares Dow Jones U.S. Home Construction Index Fund"),
    ("IYJCL",        "iShares Dow Jones U.S. Industrial Sector Index Fund"),
    ("IDUCL",        "iShares Dow Jones U.S. Utilities Sector Index Fund"),
    ("IYRCL",        "iShares Dow Jones US Real Estate ETF"),
    ("IYZCL",        "iShares Dow Jones US Telecommunications Sector ETF"),
    ("FXICL",        "iShares FTSE/Xinhua China 25 Index ETF"),
    ("ICLNCL",       "iShares Global Clean Energy ETF"),
    ("IAUCL",        "iShares Gold Trust ETF"),
    ("HDV CL",       "iShares High Dividend ETF"),
    ("HYGCL",        "iShares iBoxx $ High Yield Corporate Bond ETF"),
    ("LQDCL",        "iShares iBoxx $ Investment Grade Corporate Bond ETF"),
    ("EMB CL",       "iShares J.P. Morgan USD Emerging Markets Bond ETF"),
    ("ACWICL",       "iShares MSCI ACWI ETF"),
    ("AAXJCL",       "iShares MSCI All Country Asia Ex Japan Index Fund ETF"),
    ("EPUCL",        "iShares MSCI All Peru Capped ETF"),
    ("EWACL",        "iShares MSCI Australia ETF"),
    ("EWZCL",        "iShares MSCI Brazil Capped ETF"),
    ("ECHCL",        "iShares MSCI Chile Investable Market Index Fund ETF"),
    ("MCHICL",       "iShares MSCI China ETF"),
    ("EFACL",        "iShares MSCI EAFE ETF"),
    ("EEMCL",        "iShares MSCI Emerging Markets Index ETF"),
    ("EZUCL",        "iShares MSCI EMU ETF"),
    ("EWQCL",        "iShares MSCI France ETF"),
    ("EWGCL",        "iShares MSCI Germany ETF"),
    ("EWHCL",        "iShares MSCI Hong Kong ETF"),
    ("INDA CL",      "iShares MSCI India ETF"),
    ("EWICL",        "iShares MSCI Italy Capped ETF"),
    ("EWJCL",        "iShares MSCI Japan ETF"),
    ("EWWCL",        "iShares MSCI Mexico Capped ETF"),
    ("EPPCL",        "iShares MSCI Pacific ex-Japan ETF"),
    ("ERUSCL",       "iShares MSCI Russia Capped ETF"),
    ("EWYCL",        "iShares MSCI South Korea Capped ETF"),
    ("EWPCL",        "iShares MSCI Spain Capped ETF"),
    ("EWTCL",        "iShares MSCI Taiwan ETF"),
    ("EWUCL",        "iShares MSCI United Kingdom ETF"),
    ("IVWCL",        "iShares S&P 500 Growth ETF"),
    ("IVVCL",        "iShares S&P 500 Index Fund ETF"),
    ("ILFCL",        "iShares S&P Latin America 40 Index ETF"),
    ("DVY CL",       "iShares Select Dividend ETF"),
    ("IYG CL",       "iShares U.S. Financial Services ETF"),
    ("IYFCL",        "iShares U.S. Financials ETF"),
    ("IYH CL",       "iShares U.S. Healthcare ETF"),
    ("IYWCL",        "iShares US Technology ETF"),
    ("ITAUCL",       "Itaú CorpBanca"),
    ("JNJCL",        "Johnson & Johnson"),
    ("JPMCL",        "JPMorgan Chase & Co."),
    ("LTM",          "Latam"),
    ("MASISA",       "Masisa S.A"),
    ("CFIMBILA-A",   "MBI Best Ideas Latam FI, Serie U"),
    ("CFIMBIDA-A",   "MBI Deuda Alternativa FI, Serie A"),
    ("CFIMBIRF-A",   "MBI Deuda Plus FI, Serie U"),
    ("CFIMBDPA-E",   "MBI Deuda Privada FI, Serie A"),
    ("CFIMBIDT-B",   "MBI Deuda Total FI, Serie B"),
    ("CFIMBIGL-A",   "MBI Global FI, Serie U"),
    ("CFIMBIRFUS",   "MBI Renta Fija Plus Dólar FI, Serie U"),
    ("MCDCL",        "McDonald's Corp."),
    ("MRKCL",        "Merck & Co"),
    ("MSFTCL",       "Microsoft"),
    ("MINERA",       "Minera Valparaiso"),
    ("CFIMDCHA",     "Moneda Deuda Chile FI"),
    ("CFIMDLATAE",   "Moneda Deuda Chile FI, Serie AE"),
    ("CFIMDCHD",     "Moneda Deuda Chile FI, Serie D"),
    ("CFIMDCHE",     "Moneda Deuda Chile FI, Serie E"),
    ("CFIMDCHI",     "Moneda Deuda Chile FI, Serie I"),
    ("CFIMDLIG-A",   "Moneda Deuda Latam Investment Grade FI, Serie A"),
    ("CFIMLDLAE",    "Moneda Deuda Latam Investment Grade FI, Serie AE"),
    ("CFIMLDL-B",    "Moneda Deuda Latam Investment Grade FI, Serie B"),
    ("CFIMDLIG-I",   "Moneda Deuda Latam Investment Grade FI, Serie I"),
    ("CFIIMDLAT",    "Moneda Deuda Latinoamericana FI Moneda"),
    ("CFIMLE-A",     "Moneda Latam Equity FI, Serie A"),
    ("CFIMLE-B",     "Moneda Latam Equity FI, Serie B"),
    ("CFIMLDL",      "Moneda Latinoamérica Deuda Local FI"),
    ("CFIMRCLPR",    "Moneda Renta CLP FI"),
    ("CFIMRCLP",     "Moneda Renta CLP FI, Serie A"),
    ("CFIMRFIHYA",   "Moneda Renta Fija Internacional High-Yield FI, Serie A"),
    ("CFIMRFIHYB",   "Moneda Renta Fija Internacional High-Yield FI, Serie B"),
    ("CFIMRFHYBE",   "Moneda Renta Fija Internacional High-Yield FI, Serie BE"),
    ("CFIMRFIIGA",   "Moneda Renta Fija Internacional Investment Grade FI, Serie A"),
    ("CFIMRVCHA",    "Moneda Renta Variable Chile FI, Serie A"),
    ("CFIMRBCHAE",   "Moneda Renta Variable Chile FI, Serie AE"),
    ("CFIMRVCHAE",   "Moneda Renta Variable Chile FI, Serie AE"),
    ("CFIMRVCHE",    "Moneda Renta Variable Chile FI, Serie E"),
    ("CFIMRVCHI",    "Moneda Renta Variable Chile FI, Serie I"),
    ("CFIMRVEA",     "Moneda Renta Variable Emergente FI"),
    ("CFIMRVEC",     "Moneda Renta Variable Emergente FI, Serie C"),
    ("CFIMRVIA",     "Moneda Renta Variable Internacional FI"),
    ("CFIMRVIB",     "Moneda Renta Variable Internacional FI, Serie B"),
    ("CFIMRVUSAA",   "Moneda Renta Variable USA FI, Serie A"),
    ("CFIMRVUSAC",   "Moneda Renta Variable USA FI, Serie C"),
    ("CFIMSC",       "Moneda Small Cap Latinoamérica Feeder FI, Serie A"),
    ("CFIMSCAE",     "Moneda Small Cap Latinoamérica FI, Serie AE"),
    ("MSCL",         "Morgan Stanley"),
    ("MULTI X",      "Multiexport Foods S.A"),
    ("NEMCL",        "Newmont Mining Corporation"),
    ("NKECL",        "Nike"),
    ("NITRATOS",     "Nitratos de Chile S.A."),
    ("NORTEGRAN",    "Norte Grande S.A."),
    ("NUAM",         "Nuam Exchange"),
    ("NVDACL",       "Nvidia Corporation"),
    ("RENTAS-OSA",   "Opción Preferente - FI Independencia Rentas Inmobiliarias"),
    ("ORCLCL",       "Oracle"),
    ("ORCL",         "Oracle"),
    ("PARAUCO",      "Parque Arauco S.A."),
    ("PAZ",          "Paz Corp S.A."),
    ("PEPCL",        "Pepsico, Inc."),
    ("PFECL",        "Pfizer Inc."),
    ("CFIPIONERO",   "Pionero Fondo de Inversión"),
    ("CFIPIONAE",    "Pionero Fondo de Inversión, Serie AE"),
    ("MPLAZA-OSA",   "Plaza S.A Derechos Preferentes"),
    ("MALLPLAZA",    "Plazas S.A"),
    ("FROWARD",      "Portuaria Cabo Froward S.A."),
    ("potasios-a",   "Potasios de Chile S.A. Clase A"),
    ("potasios-b",   "Potasios de Chile S.A. Clase B"),
    ("PGCL",         "Procter & Gamble Co."),
    ("PROVIDA",      "ProVida AFP"),
    ("VENTANAS",     "Puerto Ventanas S.A."),
    ("QCOMCL",       "QUALCOMM Incorporated"),
    ("CFIQAC",       "Quest Acciones Chile FI, Serie A"),
    ("CFIQRGA",      "Quest Renta Global FI, Serie A"),
    ("QUINENCO",     "Quinenco S.A"),
    ("RIPLEY",       "Ripley Corp S.A."),
    ("SALFACORP",    "SalfaCorp"),
    ("SALMOCAM",     "Salmones Camanchaca S.A."),
    ("SCHWAGER",     "Schwager S.A."),
    ("SK",           "Sigdo Koppers S.A."),
    ("CFIMSIGLO",    "Siglo XXI Fondo de Inversión"),
    ("SMU",          "Smu S.A."),
    ("ORO BLANCO",   "Sociedad de Inversiones Oro Blanco S.A."),
    ("SMSAAM",       "Sociedad Matriz Saam S.A."),
    ("PUCOBRE",      "Sociedad Punta del Cobre S.A."),
    ("SQM-A",        "Sociedad Química y Minera de Chile, Serie A"),
    ("SQM-B",        "Sociedad Química y Minera de Chile, Serie B"),
    ("SOCOVESA",     "Socovesa S.A."),
    ("SONDA",        "Sonda S.A."),
    ("SOQUICOM",     "Soquimich Comercial S.A"),
    ("SBUXCL",       "Starbucks Corporation"),
    ("SURACL",       "Sura CL"),
    ("CFITACPI-E",   "TAM UBP Private Debt FI"),
    ("CFITACP2-E",   "TAM UBP Private Debt II FI"),
    ("TGTCL",        "Target Corp."),
    ("BACL",         "The Boeing Company"),
    ("KOCL",         "The Coca-Cola Company"),
    ("DISCL",        "The Walt Disney Company"),
    ("UPSCL",        "United Parcel Service"),
    ("XCL",          "United States Steel Corp."),
    ("UNHCL",        "UnitedHealth Group Incorporated"),
    ("CONCHATORO",   "Vina Concha y Toro S.A"),
    ("VCL",          "Visa Inc."),
    ("WALMARTCL",    "Walmart CL"),
    ("WATTS",        "Watts S.A."),
    ("WFCCL",        "Wells Fargo & Company"),
    ("ZOFRI",        "Zona Franca de Iquique S.A."),
]

NOMBRES_CHILE: dict[str, str] = {_norm(k): v for k, v in _RAW_NOMBRES_CHILE}


def _get_nombre_chile(ticker: str) -> str | None:
    """Nombre desde dict estático. Normaliza con _norm().
    Si el ticker termina en 'CL', prueba también sin el sufijo."""
    t = _norm(ticker)
    if t in NOMBRES_CHILE:
        return NOMBRES_CHILE[t]
    if len(t) > 2 and t.endswith("CL") and t[:-2] in NOMBRES_CHILE:
        return NOMBRES_CHILE[t[:-2]]
    return None


# ── Helpers ───────────────────────────────────────────────────────────────────
def _in_whitelist(ticker: str) -> bool:
    """Verifica si un ticker BCS está en la whitelist de Chile.
    Normaliza guiones/espacios a '_' y elimina puntos.
    Red de seguridad: si el ticker termina en 'CL', prueba sin el sufijo.
    """
    t = _norm(ticker)
    if t in CHILE_TICKER_WHITELIST:
        return True
    if len(t) > 2 and t.endswith("CL") and t[:-2] in CHILE_TICKER_WHITELIST:
        return True
    return False


def _ts_to_date(ts) -> str | None:
    if not ts:
        return None
    return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime("%Y-%m-%d")


def _to_clp(amount, currency, tc) -> float | None:
    if amount is None:
        return None
    return round(amount * tc, 2) if currency == "USD" else round(amount, 2)


def get_tc_usdclp() -> float:
    return round(yf.Ticker("USDCLP=X").fast_info["last_price"], 2)


# ── Precios BCS via TradingView Overview ──────────────────────────────────────
def _get_bcs_prices(symbols: list[str]) -> dict[str, float | None]:
    """Precio actual en CLP para stocks BCS sin yield en TV."""
    if not symbols:
        return {}

    overview = Overview()

    def _fetch(sym: str):
        try:
            result = overview.get_symbol_overview(symbol=f"BCS:{sym}")
            if result.get("status") == "success":
                price = result["data"].get("close")
                if price:
                    return sym, float(price)
        except Exception:
            pass
        return sym, None

    with ThreadPoolExecutor(max_workers=8) as ex:
        return dict(ex.map(_fetch, symbols))


# ── Fetch TradingView Chile ───────────────────────────────────────────────────
def fetch_tv_chile(tc: float) -> list[dict]:
    now   = datetime.datetime.now(tz=datetime.timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    ts_from = int((today - datetime.timedelta(weeks=4)).timestamp())
    ts_to   = int((today + datetime.timedelta(weeks=8, seconds=86399)).timestamp())

    raw = CalendarScraper().scrape_dividends(
        timestamp_from=ts_from,
        timestamp_to=ts_to,
        markets=["chile"],
    )

    seen: dict[tuple, dict] = {}
    for ev in raw:
        ex_date = _ts_to_date(ev.get("dividend_ex_date_upcoming")) or \
                  _ts_to_date(ev.get("dividend_ex_date_recent"))
        if not ex_date:
            continue
        full_sym = ev.get("full_symbol", "")
        ticker   = full_sym.split(":")[-1]
        if not _in_whitelist(ticker):
            continue
        key = (full_sym, ex_date)
        if key in seen:
            continue
        amount    = ev.get("dividend_amount_upcoming") or ev.get("dividend_amount_recent")
        currency  = ev.get("fundamental_currency_code", "USD")
        monto_clp = _to_clp(amount, currency, tc)
        seen[key] = {
            "symbol"         : full_sym,
            "nombre"         : _get_nombre_chile(ticker) or ev.get("name") or ev.get("description"),
            "fuente"         : "TV",
            "fecha_corte"    : ex_date,
            "fecha_pago"     : _ts_to_date(ev.get("dividend_payment_date_upcoming")) or
                               _ts_to_date(ev.get("dividend_payment_date_recent")),
            "monto_original" : amount,
            "moneda_original": currency,
            "tc_usdclp"      : tc if currency == "USD" else None,
            "monto_clp"      : monto_clp,
            "tipo"           : "efectivo",
            "en_partes"      : False,
            "concepto"       : None,
            "yield_tv_pct"   : ev.get("dividends_yield"),
        }
    rows = list(seen.values())

    # Para los sin yield en TV, calcular con precio CLP de Overview
    sin_yield = [
        r["symbol"].split(":")[-1]
        for r in rows
        if r["yield_tv_pct"] is None and r["monto_clp"]
    ]
    if sin_yield:
        precios = _get_bcs_prices(sin_yield)
        for r in rows:
            if r["yield_tv_pct"] is None and r["monto_clp"]:
                sym_short = r["symbol"].split(":")[-1]
                precio = precios.get(sym_short)
                if precio and precio > 0:
                    r["yield_tv_pct"] = round(r["monto_clp"] / precio * 100, 6)

    return rows


# ── Preview ───────────────────────────────────────────────────────────────────
def get_preview() -> dict:
    tc  = get_tc_usdclp()
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    rows = fetch_tv_chile(tc)

    return {
        "fecha_preview" : now.strftime("%Y-%m-%d %H:%M UTC"),
        "tc_usdclp"     : tc,
        "ventana_tv"    : {
            "desde": (now - datetime.timedelta(weeks=4)).strftime("%Y-%m-%d"),
            "hasta": (now + datetime.timedelta(weeks=8)).strftime("%Y-%m-%d"),
        },
        "resumen": {
            "tv_total"  : len(rows),
            "con_yield" : sum(1 for r in rows if r["yield_tv_pct"] is not None),
            "sin_yield" : sum(1 for r in rows if r["yield_tv_pct"] is None),
        },
        "dividendos": rows,
    }


# ── Sync a Supabase ───────────────────────────────────────────────────────────
def _supabase_headers():
    key = SUPABASE_SERVICE_KEY or SUPABASE_KEY
    return {
        "apikey"       : key,
        "Authorization": f"Bearer {key}",
        "Content-Type" : "application/json",
        "Prefer"       : "resolution=merge-duplicates,return=minimal",
    }


def sync_to_supabase(rows: list[dict]) -> dict:
    if not SUPABASE_URL or not (SUPABASE_SERVICE_KEY or SUPABASE_KEY):
        raise RuntimeError("Faltan credenciales Supabase en .env")

    url     = f"{SUPABASE_URL}/rest/v1/{TABLE}"
    results = {"guardados": 0, "errores": []}

    for i in range(0, len(rows), BATCH):
        batch = rows[i:i + BATCH]
        r = http.post(url, json=batch, headers=_supabase_headers(), timeout=30)
        if r.status_code in (200, 201, 204):
            results["guardados"] += len(batch)
        else:
            results["errores"].append(
                f"batch {i//BATCH+1}: {r.status_code} {r.text[:100]}"
            )
    return results

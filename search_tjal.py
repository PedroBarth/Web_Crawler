from bs4 import BeautifulSoup
from datetime import datetime
from unidecode import unidecode

def build_url(input):
    url = f'https://www2.tjal.jus.br/cpopg/show.do?processo.codigo=01000I1FT0000&processo.foro=1&processo.numero={input}&uuidCaptcha=sajcaptcha_110a0e085c804c6892ff9d67fa79fffd'
    return url

build_headers= {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
    'Connection': 'keep-alive',
    'Host': 'www2.tjal.jus.br',
    'Referer': 'https://www2.tjal.jus.br/cpopg/open.do',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
}

def crawler(response):
    try:
        soup = BeautifulSoup(response.body, 'html.parser')
    except:
        print("Erro ao buscar dados")


    return {
        
        "uf": "AL",
        "area": _search_area(soup),
        "juiz": _search_judge(soup),
        "partes": _search_parties(soup),        
        "sistema": "ESAJ-TJAL",
        "segmento": "JUSTICA ESTADUAL",
        "tribunal": "TJ-AL",
        "movimentos": _search_movimentacoes(soup),
        "valorCausa": _search_value(soup),
        "assuntosCNJ": _search_subjects(soup),        
        "urlProcesso": response.url,        
        "grauProcesso": _search_degree(soup),
        "orgaoJulgador": _search_organ(soup),
        "unidadeOrigem": _search_origin(soup),
        "classeProcessual": _search_class(soup),
        "dataDistribuicao": _search_data_dist(soup),
        "eProcessoDigital": True,
        "statusObservacao": _search_status(soup),
        "numeroProcessoUnico": _search_num_process(soup)
        
    }

def _search_area(soup):
    area = soup.find("div", id="areaProcesso").text.strip().upper()

    if area is None:
        return 'Não há dados'
    else:
        area = unidecode(area)
        return area

def _search_judge(soup):
    juiz = soup.find("span", id="juizProcesso")

    if juiz is None:
        return 'Não há dados'
    else:
        juiz = juiz.text.strip().upper()
        return juiz

def _search_parties(soup):
    todasPartes = soup.find("table", id="tableTodasPartes").findAll("tr", class_="fundoClaro")

    partes = []

    for part in todasPartes:
        nome = part.find("td", class_="nomeParteEAdvogado").contents[0].strip()

        tipo = part.find("span", class_="tipoDeParticipacao").text.strip()      


        if tipo == 'Testemunha':   
            partes.append({
                "nome" : unidecode(nome.upper()),
                "tipo": unidecode(tipo.upper()) 
            })
        else:
            partes.append({
                "nome" : unidecode(nome.upper()),
                "tipo": unidecode(tipo.upper()) 
            })
    
    if partes is None:
        return 'Não há dados'
    else:   
        return partes

def _search_movimentacoes(soup):
    tabelaMovimentacoes = soup.find('tbody', id="tabelaTodasMovimentacoes").find_all("tr")

    indice = len(tabelaMovimentacoes) - 1

    movimentos = []

    for movimentacao in tabelaMovimentacoes:
        data = movimentacao.find("td").text.strip()
        date = datetime.strptime(data, '%d/%m/%Y').strftime("%Y-%m-%dT%H:%M:%S")

        nomeOriginal = movimentacao.find("td", class_="descricaoMovimentacao").contents[0].strip()

        if nomeOriginal=='':
            nomeOriginal = movimentacao.find("td", class_="descricaoMovimentacao").find("a").text.strip()

        descricao = movimentacao.find("td", class_="descricaoMovimentacao").find("span").text.strip()
        descricao = descricao.replace('\r\n',' ')

        if descricao=='':
            movimentos.append({
                "data": date,
                "indice": indice,
                "eMovimento": True,
                "nomeOriginal":[
                    unidecode(nomeOriginal).upper()
                ]
            })
        else:
            movimentos.append({
                "data": date,
                "indice": indice,
                "descricao": unidecode(descricao).upper(),
                "eMovimento": True,
                "nomeOriginal":[
                    unidecode(nomeOriginal).upper()
                ]
            })

        indice-=1

    if movimentos is None:
        return 'Não há dados'
    else:
        return movimentos

def _search_value(soup):

    valorCausa = []

    moeda = soup.find("div", id="valorAcaoProcesso").text.split()[0]
    valor = soup.find("div", id="valorAcaoProcesso").text.split()[1]

    valorCausa.append({
        'moeda': moeda,
        'valor': float(valor.replace('.','').replace(',','.'))
    })
    
    if valorCausa is None:
        return 'Não há dados'
    else:
        return valorCausa

def _search_subjects(soup):

    assuntos = []

    assuntosPrincipais = soup.find('span', id="assuntoProcesso").text

    outrosAssuntos = soup.find('span', title="Dano Moral,Inclusão Indevida em Cadastro de Inadimplentes").text.split(",")

    assuntos.append({
        'titulo': unidecode(assuntosPrincipais.upper())
    })
    
    for sub in outrosAssuntos:
        assuntos.append({'titulo': unidecode(sub.upper())})

    if assuntos is None:
        return 'Não há dados'
    else:
        return assuntos

def _search_degree(soup):

    grau = soup.find('h1', class_="header__navbar__title").text.split()

    if grau is None:
        return 'Não há dados'
    else:
        grau = grau[6].replace('º', '')
        return int(grau)

def _search_organ(soup):

    orgao = soup.find('span', id="varaProcesso").text.strip().upper()

    if orgao is None:
        return 'Não há dados'
    else:
        orgao = unidecode(orgao.upper())
        return orgao

def _search_origin(soup):

    origin = soup.find('span', id="foroProcesso").text.strip().upper()

    if origin is None:
        return 'Não há dados'
    else:
        origin = unidecode(origin)
        return origin

def _search_class(soup):

    classeProcesso = soup.find('span', id="classeProcesso").text.strip().upper()

    if classeProcesso is None:
        return 'Não há dados'
    else:
        classeProcesso = unidecode(classeProcesso)
        return {'nome' : classeProcesso}

def _search_data_dist(soup):

    data = soup.find('div', id="dataHoraDistribuicaoProcesso").text.replace('às', '').split()

    if data is None:
        return 'Não há dados'
    else:
        dd = data[0] + ' ' + data[1] + ':00'

        dtTime = (datetime.strptime(dd, "%d/%m/%Y %H:%M:%S")
            .date()
            .strftime("%Y-%m-%dT%H:%M:%S")
        )

        return dtTime

def _search_status(soup):

    status = soup.find('span', id="labelSituacaoProcesso").text.strip()

    if status is None:
        return 'Não há dados'
    else:
        status = unidecode(status.upper())
        return status

def _search_num_process(soup):

    processID = soup.find('span', id="numeroProcesso").text.strip()

    if processID is None:
        return 'Não há dados'
    else:
        processID = processID.replace('-', '').replace('.', '')
        return processID
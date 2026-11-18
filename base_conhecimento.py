from orientacao import Orientacao
campos = ["id", "categoria", "titulo", "palavras_chave", "resposta","documentos", "onde", "fonte", "verificado_em"]
ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e","í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}

PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1
LIMITE_ALTA = 6
LIMITE_MEDIA = 3


def normalizar(texto):
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []   # lista de objetos Orientacao

    def carregar(self):
        self.orientacoes = []
        ignoradas = 0
        try:
            with open(self.caminho, "r") as arquivo:
                for linha in arquivo:
                    linha = linha.strip()
                    dados = linha.split(";")
                    if linha == "" or dados[0].endswith("id"):
                        pass    # linha em branco ou cabeçalho: não é erro
                    elif len(dados) != len(campos) or not dados[0].isdigit():
                        ignoradas += 1
                    else:
                        registro = {}
                        for i in range(len(campos)):
                            registro[campos[i]] = dados[i].strip()
                        if registro["titulo"] == "" or registro["categoria"] == "":
                            ignoradas += 1
                        else:
                            palavras = registro["palavras_chave"].split("|")
                            documentos = registro["documentos"].split("|")
                            orientacao = Orientacao(
                                registro["id"], registro["categoria"],
                                registro["titulo"], palavras, registro["resposta"],
                                documentos, registro["onde"], registro["fonte"],
                                registro["verificado_em"])
                            self.orientacoes.append(orientacao)
        except (OSError, UnicodeDecodeError):
            print("Aviso: não foi possível ler a base de conhecimento em '" + self.caminho + "'.")
            self.orientacoes = []
            return self.orientacoes
        if ignoradas > 0:
            print("Aviso: " + str(ignoradas) + " linha(s) inválida(s) da base foram ignoradas.")
        return self.orientacoes

    def categorias(self):
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria == categoria:
                lista.append(orientacao)
        return lista

    def pontuar(self, orientacao, pergunta):
        pontos = 0
        # +3 por palavra-chave que aparece na pergunta
        for palavra in orientacao.palavras_chave:
            chave = normalizar(palavra)
            if chave.strip() != "" and chave in pergunta:
                pontos += PONTOS_PALAVRA_CHAVE
        # +1 por palavra da pergunta (4+ letras) que aparece no título
        titulo = normalizar(orientacao.titulo)
        vistas = []
        for palavra in pergunta.split():
            if len(palavra) >= 4 and palavra not in vistas:
                vistas.append(palavra)
                if " " + palavra + " " in titulo:
                    pontos += PONTOS_TITULO
        return pontos

    def buscar(self, pergunta):
        pergunta = normalizar(pergunta)
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(orientacao, pergunta)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        for i in range(len(resultados)):
            for j in range(len(resultados) - 1 - i):
                if resultados[j][0] < resultados[j + 1][0]:
                    resultados[j], resultados[j + 1] = resultados[j + 1], resultados[j]
        return resultados

    def confianca(self, pontos):
        if pontos >= LIMITE_ALTA:
            return "ALTA"
        if pontos >= LIMITE_MEDIA:
            return "MÉDIA"
        return "NENHUMA"
cabecalho = "num;origem;pergunta;id_orientacao;encontrou;ajudou;tentativas;passos"

class Assistente:
    def __init__(self, nome, base):
        self.nome = nome
        self.base = base          
        self.historico = []       
        self.notas = []
        self.passos = 0           
        self.arq_hist = "data/historico.csv"
        self.arq_export = "data/atendimentos.csv"

    def ler(self, texto, padrao="0"):
        self.passos += 1
        return input(texto).strip()

    def ler_numero(self, texto, maximo):
        while True:
            v = self.ler(texto)
            if v.isdigit() and int(v) <= maximo:
                return int(v)
            print("Opção inválida (0 a " + str(maximo) + ").")

    def ler_sn(self, texto):
        while True:
            v = self.ler(texto, "n").lower()
            if v in ("s", "sim", "n", "nao", "não"):
                return "s" if v[0] == "s" else "n"
            print("Digite s ou n.")

    def tem_dado_pessoal(self, texto):
        return sum(1 for c in texto if c.isdigit()) >= 8 or "@" in texto
    def perguntar(self):
        if not self.base.orientacoes:
            print("Base de conhecimento vazia.")
            return
        marca, tentativas, ultima, ultimo_id, achou = self.passos, 0, "", 0, "n"
        while True:
            texto = self.ler("\nDigite sua dúvida (0 para voltar): ")
            if texto == "0":
                if tentativas:   
                    self.registrar("pergunta", ultima, ultimo_id, achou, "n", tentativas, marca)
                return
            elif texto == "":
                print("Digite algo ou 0 para voltar.")
            elif self.tem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
            else:
                tentativas += 1
                ultima = texto
                res = self.base.buscar(texto)             
                if not res or res[0][0] < 3:
                    achou, ultimo_id = "n", 0
                    print("Não encontrei. Tente outras palavras ou use as categorias: " + ", ".join(self.base.categorias()))
                else:
                    pontos, melhor = res[0]
                    achou, ultimo_id = "s", melhor.id
                    print("\nConfiança: " + self.base.confianca(pontos) + " (" + str(pontos) + " pontos)")
                    melhor.exibir()
                    alt = [t for t in res[1:] if t[0] >= 3][:2]
                    if alt:
                        print("\nVeja também: " + " | ".join(o.titulo + " (" + str(p) + ")" for p, o in alt))
                    if self.ler_sn("\nRespondeu sua dúvida? (s/n): ") == "s":
                        print("Que bom!")
                        self.registrar("pergunta", texto, melhor.id, "s", "s", tentativas, marca)
                        marca, tentativas, ultima, ultimo_id, achou = self.passos, 0, "", 0, "n"
                    else:
                        print("Reescreva com outras palavras ou digite 0 para voltar.")

    def navegar(self):
        categoria = self.base.categorias()
        while categoria:
            print("\nCategorias:")
            for i, c in enumerate(categoria, 1):
                print("  " + str(i) + ". " + c)
            op = self.ler_numero("Escolha (0 para voltar): ", len(categoria))
            if op == 0:
                return
            lista = self.base.por_categoria(categoria[op - 1])
            while True:
                marca = self.passos
                print("\n" + categoria[op - 1] + ":")
                for i, o in enumerate(lista, 1):
                    print("  " + str(i) + ". " + o.titulo)
                esc = self.ler_numero("Escolha (0 para voltar): ", len(lista))
                if esc == 0:
                    break
                lista[esc - 1].exibir()
                ajudou = self.ler_sn("\nRespondeu sua dúvida? (s/n): ")
                self.registrar("categoria", lista[esc - 1].titulo, lista[esc - 1].id,"s", ajudou, 1, marca)
        if not categoria:
            print("Base de conhecimento vazia.")

    def linha(self, r):
        return ";".join([str(r["num"]), r["origem"], r["pergunta"], str(r["id"]), r["encontrou"],
                         r["ajudou"], str(r["tentativas"]), str(r["passos"])])

    def registrar(self, origem, pergunta, id_o, encontrou, ajudou, tentativas, marca):
        r = {"num": len(self.historico) + 1, "origem": origem,
             "pergunta": pergunta.replace(";", ",").replace("\n", " "), "id": id_o,
             "encontrou": encontrou, "ajudou": ajudou, "tentativas": tentativas,
             "passos": self.passos - marca}
        self.historico.append(r)
        try:
            with open(self.arq_hist, "a", encoding="utf-8") as f:
                if f.tell() == 0:
                    f.write(cabecalho + "\n")
                f.write(self.linha(r) + "\n")
        except OSError:
            print("Aviso: não consegui gravar o histórico.")

    def indicadores(self):
        h = self.historico
        print("\n=== Indicadores ===")
        if not h:
            print("Sem atendimentos registrados.")
            return
        n = len(h)
        achados = [r for r in h if r["encontrou"] == "s"]
        ajudou = [r for r in h if r["ajudou"] == "s"]
        sem = []
        for r in h:
            if r["ajudou"] == "n" and r["pergunta"] not in sem:
                sem.append(r["pergunta"])
        tempo = sum(r["passos"] for r in achados) / len(achados) if achados else 0
        nota = str(round(sum(self.notas) / len(self.notas), 1)) if self.notas else "sem nota"
        print("Atendimentos: " + str(n))
        print("Resposta encontrada: " + str(round(100 * len(achados) / n, 1)) + "%")
        print("Taxa de acerto: " + str(round(100 * len(ajudou) / n, 1)) + "%")
        print("Passos médios para encontrar (sem relógio, no lugar do tempo): " + str(round(tempo, 1)))
        print("Tentativas por atendimento: " + str(round(sum(r["tentativas"] for r in h) / n, 1)))
        print("Facilidade de uso (1 a 5): " + nota)
        print("Dúvidas sem solução: " + (" | ".join(sem) if sem else "nenhuma"))

    def exportar_csv(self):
        titulos = {o.id: o.titulo for o in self.base.orientacoes}
        try:
            with open(self.arq_export, "w") as arquivo:
                arquivo.write(cabecalho + ";titulo_orientacao\n")
                for r in self.historico:
                    arquivo.write(self.linha(r) + ";" + titulos.get(r["id"], "-") + "\n")
            print("Exportado em " + self.arq_export)
        except OSError:
            print("Aviso: não consegui exportar o CSV.")

    def menu(self):
        print("=== " + self.nome + " === (orientações sobre a CIN; não é canal oficial)")
        while True:
            print("\n1. Perguntar  2. Categorias  3. Indicadores  0. Sair")
            opcao = self.ler_numero("opção: ", 3)
            if opcao == 1:
                self.perguntar()
            elif opcao == 2:
                self.navegar()
            elif opcao == 3:
                self.indicadores()
            else:
                nota = self.ler_numero("Nota de facilidade 1 a 5 (0 pula): ", 5)
                if nota:
                    self.notas.append(nota)
                self.indicadores()
                self.exportar_csv()
                return
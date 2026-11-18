# Citizen Assist AI

Assistente digital de orientação ao cidadão, executado no terminal, feito em **Python puro (sem bibliotecas externas)**.
Ele responde dúvidas sobre a **Carteira de Identidade Nacional (CIN)** a partir de uma base de conhecimento em CSV, usando uma busca por pontuação. Toda resposta mostra a **fonte oficial**, a **data de verificação** e o aviso de que o assistente **não é um canal oficial**. O programa **nunca pede nem registra dados pessoais**.

Projeto da Global Solution 2026.2 – Pensamento Computacional e Automação com Python (desafio CitizenTech).

---

## Integrantes

| Nome | RM | Turma |
|---|---|---|
| Andre Shiguematsu | 569158 | 1CCPJ |
| Guilherme Belo | 570079 | 1CCPJ |

---

## Público e problema escolhidos

**Público:** cidadãos que precisam emitir, substituir ou usar a Carteira de Identidade Nacional (CIN).

**Problema:** a informação sobre a CIN existe, mas está espalhada, em linguagem técnica e misturada com páginas que parecem oficiais e não são. O cidadão perde tempo para descobrir onde pedir, o que levar, se é gratuito e como obter a versão digital.

**Solução:** um assistente que responde em linguagem simples, mostra de onde veio a informação e quando ela foi conferida, e orienta a confirmar os detalhes no órgão emissor do estado, já que os procedimentos variam por unidade federativa.

---

## ODS relacionados

- **ODS 16 – Paz, justiça e instituições eficazes:** acesso à informação e a serviços públicos de forma transparente.
- **ODS 10 – Redução das desigualdades:** informação simples e gratuita para quem tem dificuldade de acessar canais oficiais.

---

## Como executar

Requisito: Python 3.8 ou superior. Não é preciso instalar nada.

```bash
cd gs_python
python main.py
```

Execute sempre **de dentro da pasta do projeto**, porque os caminhos `data/...` são relativos. Se o arquivo da base não for encontrado, o programa avisa e continua abrindo (sem derrubar).

### Menu principal

```
1. Perguntar   2. Categorias   3. Indicadores   0. Sair
```

- **1 – Perguntar:** digite a dúvida em texto livre. `0` volta ao menu.
- **2 – Categorias:** navegue por categoria e por orientação numerada. `0` volta em todas as telas.
- **3 – Indicadores:** mostra os indicadores calculados até agora.
- **0 – Sair:** pede a nota de facilidade (1 a 5), mostra os indicadores e exporta os atendimentos.

### Exemplo de execução

```
Digite sua dúvida (0 para voltar): Como faço a segunda via da CIN?

Confiança: ALTA (7 pontos)

>> Onde solicitar a segunda via da CIN [Documentação]
A orientação federal informa que a segunda via da CIN pode ser solicitada ...
Documentos necessários:
  - Confirme no órgão escolhido
Onde: Órgão de identificação civil de qualquer estado ou do Distrito Federal
Fonte: https://www.gov.br/governodigital/pt-br/identidade/cin/perguntas-frequentes-sobre-a-cin (verificado em 2026-11-06)
Aviso: este assistente NÃO é um canal oficial.

Veja também: Onde solicitar a Carteira de Identidade Nacional (3)

Respondeu sua dúvida? (s/n): s

Digite sua dúvida (0 para voltar): meu cpf é 123.456.789-00
Atenção: não digite CPF, telefone ou e-mail. Reescreva.
```

---

## Estrutura do projeto

```
gs_python/
├── README.md
├── main.py
├── orientacao.py
├── base_conhecimento.py
├── assistente.py
└── data/
    ├── base_conhecimento.csv
    ├── historico.csv
    └── atendimentos.csv
```

| Arquivo | Função |
|---|---|
| `main.py` | Cria a base, chama `carregar()`, cria o `Assistente` e inicia o menu. |
| `orientacao.py` | Classe `Orientacao`: guarda os dados de uma orientação e a exibe na tela. |
| `base_conhecimento.py` | Função `normalizar()` e classe `BaseConhecimento`: lê o CSV, lista categorias e busca a melhor orientação. |
| `assistente.py` | Classe `Assistente`: faz o atendimento, guarda o histórico e calcula os indicadores. |
| `data/base_conhecimento.csv` | Base de conhecimento (10 orientações). |
| `data/historico.csv` | Um atendimento por linha, gravado na hora. |
| `data/atendimentos.csv` | Exportação completa dos atendimentos ao sair. |

---

## Base de conhecimento (CSV)

Arquivo `data/base_conhecimento.csv`, separado por `;`, com **10 orientações**, **3 categorias** (Serviços públicos, Documentação e Agendamento) e **pelo menos 3 palavras-chave por orientação**. Toda orientação tem fonte oficial (gov.br) e a data em que a equipe conferiu a informação (2026-11-06).

Cabeçalho:

```
id;categoria;titulo;palavras_chave;resposta;documentos;onde;fonte;verificado_em
```

Regras do formato:

- Uma orientação por linha, 9 campos separados por `;`.
- Campos com vários itens (`palavras_chave` e `documentos`) usam `|` como separador.
- Não se usa `;` dentro do texto dos campos.
- O `id` é numérico.

Linha em branco, cabeçalho ou linha com formato inválido **não derrubam o programa**: a linha inválida é ignorada e o programa mostra qual foi.

**Para melhorar a busca**, basta acrescentar uma palavra-chave (separada por `|`) à linha da orientação no CSV, sem alterar o código.

---

## Orientação a objetos

As três classes se encaixam por **composição**:

```
Assistente
 └── base: BaseConhecimento
      └── orientacoes: [Orientacao, Orientacao, ...]
```

| Classe | Atributos | Métodos |
|---|---|---|
| `Orientacao` | id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em | `exibir()` |
| `BaseConhecimento` | caminho, orientacoes | `carregar()`, `categorias()`, `por_categoria()`, `pontuar()`, `buscar()`, `confianca()` |
| `Assistente` | nome, base, historico | `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()`, `menu()` |

**Como o CSV vira objetos:** `carregar()` lê o arquivo com `open()` e `for`, separa cada linha com `split(";")`, monta um **dicionário** (campo → valor), separa os itens múltiplos com `split("|")` e cria um objeto `Orientacao` que é guardado na lista `orientacoes`.

---

## Regra de pontuação (busca por regras)

A pergunta é comparada com cada orientação, que recebe pontos. A de maior pontuação é exibida.

**1. Normalização:** pergunta, palavras-chave e título são comparados em minúsculas, sem acentos e sem pontuação (`normalizar()`), com um espaço no começo e no fim do texto. Assim, a palavra `sus` só casa com a palavra inteira e não com um pedaço de outra.

**2. Pontos:**

| Regra | Pontos |
|---|---|
| Palavra-chave da orientação que aparece na pergunta | +3 |
| Palavra da pergunta (4 letras ou mais) que aparece no título | +1 |

**3. Confiança:**

| Melhor pontuação | Resultado |
|---|---|
| 6 pontos ou mais | Confiança **ALTA** |
| 3 a 5 pontos | Confiança **MÉDIA** |
| Menos de 3 pontos | "Não encontrei": sugere outras palavras e mostra as categorias |

**4. Resultado:** `buscar()` devolve uma **lista de tuplas** `(pontos, orientacao)`, ordenada da maior para a menor pontuação (ordenação por troca de vizinhos, sem usar `sort`). O assistente mostra a melhor orientação e até duas alternativas com 3 pontos ou mais.

**Exemplo:** na pergunta "Como faço a segunda via da CIN?", a orientação 7 recebe +3 por `segunda via`, +3 por `segunda via da cin` e +1 porque `segunda` está no título: **7 pontos, confiança ALTA**.

Os pesos e limites estão em constantes no início de `base_conhecimento.py` e podem ser ajustados.

---

## Regras de atendimento

- **Navegação por categorias:** lista categorias e orientações numeradas, com `0` para voltar em todas as telas.
- **Entradas inválidas:** opção fora da faixa, letras, resposta vazia ou `s/n` inválido nunca encerram o programa; o assistente avisa e pede de novo.
- **Dados pessoais:** o assistente nunca pede nome, CPF, telefone ou e-mail. Pergunta com **8 ou mais dígitos** ou com **@** é recusada e **não é registrada**.
- **Transparência:** toda resposta mostra fonte, data de verificação e o aviso "este assistente NÃO é um canal oficial".
- **Arquivos:** arquivo da base ausente ou com formato inválido não interrompe o programa.

---

## Histórico, indicadores e exportação

Cada atendimento é gravado em `data/historico.csv` (modo `"a"` do `open()`) com os campos:

```
num;origem;pergunta;id_orientacao;encontrou;ajudou;tentativas;passos
```

- `origem`: `pergunta` (texto livre) ou `categoria` (navegação).
- `id_orientacao`: id da orientação mostrada (`0` quando não encontrou).
- `encontrou` e `ajudou`: `s` ou `n`.
- `tentativas`: quantas perguntas foram feitas até resolver.
- `passos`: quantas vezes a pessoa digitou algo durante o atendimento.

Ao sair, o assistente pede uma **nota de facilidade de 1 a 5**, mostra os indicadores e **exporta todos os atendimentos** para `data/atendimentos.csv` com `open()` e `write()`, um registro por linha, campos separados por `;`, incluindo o título da orientação.

**Indicadores calculados:**

| Indicador | Como é calculado |
|---|---|
| Resposta encontrada (%) | atendimentos com `encontrou = s` ÷ total |
| Taxa de acerto (%) | atendimentos com `ajudou = s` ÷ total |
| Passos médios para encontrar | média de `passos` nos atendimentos em que encontrou |
| Tentativas por atendimento | média de `tentativas` |
| Facilidade de uso (1 a 5) | média das notas dadas ao sair |
| Dúvidas sem solução | lista das perguntas com `ajudou = n` |

> **Decisão técnica sobre o tempo:** como o projeto não usa nenhuma biblioteca (nem `time`), não há relógio para medir segundos. Em vez do tempo, medimos os **passos** (quantas vezes o usuário digitou algo no atendimento), que mostra o esforço para chegar à resposta. Para medir segundos, bastaria importar `time` e usar `time.time()` no início e no fim do atendimento.

---

## Integrações com outras disciplinas

Nenhuma. O projeto usa apenas o que foi visto em Pensamento Computacional e Automação com Python.

---

## Fontes consultadas

Páginas oficiais do governo federal sobre a CIN, verificadas em **2026-06-11**:

- https://www.gov.br/governodigital/pt-br/identidade/cin/duvidas-frequentes-sobre-a-cin-campanha
- https://www.gov.br/governodigital/pt-br/identidade/cin/perguntas-frequentes-sobre-a-cin
- https://www.gov.br/gestao/pt-br/assuntos/editoria-2013-defeso-eleitoral/carteira-de-identidade-nacional-veja-como-emitir-o-novo-documento

O link de cada orientação está na coluna `fonte` do `data/base_conhecimento.csv`.

---

## Teste com usuários


#	Pergunta para o testador	
1	Onde eu tiro a identidade nova?	
2	O que preciso levar para pedir a CIN?	
3	Como marcar horário para fazer a identidade?	
4	A primeira CIN é de graça?	
5	Meu RG antigo ainda vale?	
6	Como ter a identidade no celular, pelo aplicativo?	
7	Perdi minha identidade, o que eu faço?	
8	Meu nome está errado no documento, como corrigir?	
9	Meu filho de 10 anos pode ter a CIN?
10 Quero a carteirinha de plástico, quanto custa?

| Item | Resultado |
|---|---|
| Pessoas testadas | 3 |
| Atendimentos registrados | 10 |
| Resposta encontrada (%) | 90 |
| Taxa de acerto (%) | 90 |
| Passos médios para encontrar | 2.0|
| Tentativas por atendimento | 1.0 |
| Facilidade de uso (1 a 5) | 4 |

**Dúvidas sem solução:** _ Quero a carteirinha de plástico, quanto custa?

**Melhoria feita a partir do teste:** foram adicionadas palavras-chave no data/base_conhecimento.csv: orientação 2 (levar, o que levar, preciso levar), 4 (de graca, graca), 6 (celular, no celular), 7 (perdi minha identidade) e 10 (plastico, custa, quanto custa). Depois disso, as 10 perguntas passaram a mostrar a orientação certa.

---

## Limitações

- A base cobre **apenas a CIN** e tem 10 orientações.
- A busca compara **palavras exatas**: não entende sinônimos, plural ou erro de digitação. Cada variação precisa entrar como palavra-chave no CSV.
- Os procedimentos, documentos e custos **variam por estado**, por isso as respostas sempre orientam a confirmar no órgão emissor. Em várias orientações, o campo "documentos" pede essa confirmação, porque a fonte oficial federal não lista tudo.
- Não há medição de tempo em segundos (veja a decisão técnica acima).
- O assistente **não é um canal oficial** e não substitui o atendimento do órgão de identificação.

---

## Vídeo técnico

Link do YouTube (não listado): https://www.youtube.com/watch?v=irudMFYGW7I

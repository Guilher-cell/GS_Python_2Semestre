from base_conhecimento import BaseConhecimento
from assistente import Assistente

base = BaseConhecimento("data/base_conhecimento.csv")
base.carregar()    

assistente = Assistente("Citizen Assist AI", base)
try:
    assistente.menu()
except KeyboardInterrupt:
    print("Programa encerrado.")

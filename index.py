#from fastapi import FastAPI

#from api.v1.api import api_router 


#app = FastAPI(title='API - Nota Fiscal')
#app.include_router(api_router)


#if __name__ == '__main__':
#    import uvicorn
#   uvicorn.run("main:app", host="0.0.0.0", port=8000,
#                log_level='info', reload=True)


from flask import Flask
from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
from api.v1.Util import Expense
import ssl
import certifi

app = Flask(__name__)

url = 'https://www.sefaz.rs.gov.br/ASP/AAE_ROOT/NFE/SAT-WEB-NFE-NFC_QRCODE_1.asp?p=43211193015006000113651140006396901026593587%7C2%7C1%7C1%7C373BE30B0BD593FAF55E1D6F76F52AAC78F5F441'

@app.route('/')
def hello():
    page = urlopen(url,context=ssl.create_default_context(cafile=certifi.where()))
    html = page.read()
    soup = BeautifulSoup(html, "html.parser")
    local = soup.find_all(class_ = 'NFCCabecalho_SubTitulo')
    nome = local[0].string
    dadosNota = local[2].string.split(": ")
    numNota = [int(s) for s in dadosNota[1].split() if s.isdigit()] [0]
    serieNota = [int(s) for s in dadosNota[2].split() if s.isdigit()] [0]
    dataNota = dadosNota[len(dadosNota)-1]
    local = { 'nome': nome, 'numero_nota': numNota, 'nota_serie':serieNota, 'data':dataNota }
    
    resumo = soup.find_all( class_ = "NFCDetalhe_Item" )
    resumo = resumo[len(resumo)-9:len(resumo)]

    enum =0 
    vTotal = 0
    vDesconto = 0
    formPagament = ''
    vPago = 0

    resumoNota = {} 
    for index,i in enumerate(resumo):
        print(index,i, enum)     
        if enum == 1: 
            vTotal = i.string.replace(',','.')
        if enum == 3: 
            vDesconto = i.string.replace(',','.')
        if enum == 6: 
            formPagament = i.string
        if enum == 7: 
            vPago = i.string.replace(',','.')
            
        enum = enum + 1
        
        if  float(vPago) > 0.0:
            resumoNota =  {'total': vTotal, 'desconto':vDesconto,'formaPagamento':formPagament,'pago':vPago}
            break
        
    resumoNota

    mm = soup.find_all( class_ = "NFCDetalhe_Item" )

    enum =0 
    codigo = ''
    nome = ''
    quantidade = 0
    tipo = ''
    valor = 0
    valorPorProduto = 0 

    itens = [] 
    for index,i in enumerate(mm[5:len(mm)-9]):
        #print(index,i, enum)     
        if enum == 0: 
            codigo = i.string
        if enum == 1: 
            nome = i.string
        if enum == 2: 
            quantidade = i.string
        if enum == 3: 
            tipo = i.string
            
        enum = enum + 1
        if enum == 6 :
            enum = 0
            itens.append({'codigo': codigo, 'nome':nome,'quantidade':quantidade,'tipo':tipo})
        
    exp2 = Expense()
    exp2.itens = itens
    exp2.resumo = resumoNota
    exp2.local = local
    
    return exp2.toJSON().replace('\n','')
    #return 'Hello, World!'

# main driver function
if __name__ == '__main__':
 
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()
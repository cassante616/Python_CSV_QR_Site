from flask import Flask, request, render_template, send_file, after_this_request
import os
import csv
from time import sleep
import qrcode as qr

# Cria a aplicação Flask
app = Flask(__name__)

# Configuração do diretório para salvar os arquivo CSV para criação dos QRcodes
UPLOAD_FOLDER = "/home/vitorsup/Projects_Python/Python_Server/CSV_QRcodes/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# path para criar os QRcodes
path_qrcodes = "/home/vitorsup/Projects_Python/Python_Server/QRcodes/QRcode/"

# Caminho para criar o arquivo CSV dos ramais
path = "/home/vitorsup/Projects_Python/Python_Server/CSV/ramaiscloud10.csv"

path_zip = "/home/vitorsup/Projects_Python/Python_Server/QRcodes/QR_codes"

# Gera o HTML na página principal
@app.route("/")
def home():
    return render_template("index.html")

# Recebe os dados do "form" HTML para retornar o arquivo CSV
@app.route("/csv", methods=["POST"])
def form_csv():

    # Cabeçalho padrão do arquivo CSV
    header = ['Tipo do ramal', 'Número do Ramal', 'Usuário de autenticação', 'Senha Sip', 'Nome do ramal',
              'Grupo de Ramais',
              'Caller ID', 'Centro de Custo', 'Plano de Discagem', 'Grupo música de espera', 'Puxar Chamadas',
              'Habilitar Timer?', 'Habilitar BLF?', 'Escutar chamadas?', 'Gravar Chamada?', 'Bloquear Ramal?',
              'Codigo de Área']

    # Template das linhas a serem adicionadas
    rows = ['PABX', '10', '', '', 'Ramal 10', 'PRINCIPAL', '1121580985', '', 'padrao', '',
            'Puxar chamadas do mesmo Grupo',
            'não', 'Sim', 'não', 'Sim', 'não', '11']

    faixa_ramal = request.form["faixa"]
    did_ramais = request.form["did"].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
    quant_ramais = request.form["quantidade"]

    # Verifica se o usuário não alterou a estrutura do formulário para enviar os dados
    if len(faixa_ramal) > 4 or len(did_ramais) > 10 or len(quant_ramais) > 3:
        return render_template("index2.html")
    else:

        rows[6] = did_ramais
        rows[-1] = did_ramais[0:2]

        # Verifica se o campo "faixa" do input HTML foi preenchido
        if faixa_ramal == "":
            faixa_ramal = 10

        with open(path, "w", encoding="utf-8") as file:

            # Abre o arquivo como CSV para ser escrito
            csv_file = csv.writer(file, delimiter=",")

            # Insere o cabeçalho no arquivo
            csv_file.writerow(header)

            # Insere as informações nas linhas a partir dos inputs
            i = 0
            while i < int(quant_ramais):
                numero_ramal = int(faixa_ramal) + i
                ramal = f"Ramal {str(numero_ramal)}"
                rows[4] = ramal
                rows[1] = str(numero_ramal)
                csv_file.writerow(rows)
                i += 1

        # Use a função send_file para enviar o arquivo
        return send_file(path, as_attachment=True)

# Recebe os dados do "form" HTML para retornar o QRcode em PNG
@app.route("/qrcode", methods=["POST"])
def form_qrcode():

    login_ramal = request.form["login"]
    senha_ramal = request.form["senha"]

    meu_qrcode = qr.make(f"csc:{login_ramal}:{senha_ramal}@BALDUSSI_TELECOM")
    meu_qrcode.save(path_qrcodes + login_ramal + ".png")

    # Executa esse bloco depois de enviar os arquivos de volta para o cliente
    @after_this_request
    def remove_qrcode(response):
        sleep(1)
        os.remove(path_qrcodes + login_ramal + ".png")
        return response

    return send_file(path_qrcodes + login_ramal + ".png", as_attachment=True)

# Recebe o arquivo CSV do cliente para retornar os QRcodes em PNG
@app.route("/qrcode_csv", methods=["POST"])
def form_qrcode_csv():
    from werkzeug.utils import secure_filename
    import shutil
    
    # Recebe o arquivo do fomulário
    arquivo_csv = request.files["arquivo"]
    
    # Salva o arquivo no diretório especificado 
    filename = secure_filename(arquivo_csv.filename)
    arquivo_csv.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    file_csv_ramais = os.listdir(UPLOAD_FOLDER)
    path_csv_ramais = UPLOAD_FOLDER + file_csv_ramais[0]

    # Executa esse bloco depois de enviar os arquivos de volta para o cliente
    @after_this_request
    def remove_qrcode(response):
        os.remove(path_csv_ramais)
        os.remove(path_zip + ".zip")
        for file in os.listdir(path_qrcodes):
            os.remove(path_qrcodes + file)
        return response

    csv_type = path_csv_ramais[len(path_csv_ramais) - 4:len(path_csv_ramais)]

    # Valida se o arquivo for
    if csv_type != ".csv":
        return render_template("index2.html")
    else:

        # Gera os QRcodes baseado nos dados do arquivo CSV
        with open(path_csv_ramais, "r") as file:
            csv_file = csv.reader(file, delimiter=";")
            
            next(csv_file)

            for linha in csv_file:
                ramal_login = linha[2]
                ramal_pass = linha[3]

                meu_qrcode = qr.make(f"csc:{ramal_login}:{ramal_pass}@BALDUSSI_TELECOM")
                meu_qrcode.save(path_qrcodes + ramal_login + ".png")

        # Zipa os arquivos os QRcodes em PNG para serem retornados ao cliente
        shutil.make_archive(path_zip, "zip", path_qrcodes)
        
        return send_file(path_zip + ".zip")

# Inicia o servidor na porta 8000 em todas as interfaces de rede disponíveis
if __name__ == "__main__":
    app.run(port=8000, debug=True, host='0.0.0.0')

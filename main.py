pip install openai

from pathlib import Path
import streamlit as st

import openai
from dotenv import find_dotenv, load_dotenv

# Para fazer com que seja "encontrável" a variável que contem a Key da API da OPENAI:
_=load_dotenv(find_dotenv())

# Aqui é para efetivamente abrir a API criada pela OPENAI:
cliente = openai.OpenAI()

# Comando feito para a API da OPENAI:
comando = """
Faça o resumo de um texto que está delimitado por ####
O texto é a transcrição de uma reunião
O resumo deve contar com todos os assuntos abordados
O resumo deve ter no máximo 400 caracteres
Caso não seja possível criar um resumo de 500 caracteres abordando todos os assuntos, crie um resumo de até 400 caracteres abordando os principais assuntos
O resumo deve estar em texto corrido
Abaixo do resumo deve ser apresentado no formato de bullet points todos os tópicos abordados na reunião

O formato final que eu desejo é algo assim:

Resumo reunião:
- Escrever aqui o resumo da reunião conforme instruções acima

Tópicos abordados na reunião:
- Tópico 1:
- Tópico 2:
- Tópico 3:
- Tópico n:

texto: ####{}####
"""

# Função para transcrever o arquivo de áudio usando a API da OPENAI
def transcrever_arquivo (arquivo, idioma = "pt", formato = "text"): 
    with open(arquivo, "rb") as arquivo_audio:
        transcrição = cliente.audio.transcriptions.create(
            model = "whisper-1",
            language = idioma,
            response_format = formato,
            file = arquivo_audio
        )
    return transcrição

# Função para conversar com o ChatGPT e pedir para que ele faça algo via API da OPENAI:
def resumir_texto (mensagens, modelo = "gpt-3.5-turbo-0125", temperatura = 0, stream = False):
    resposta = cliente.chat.completions.create(
        model = modelo,
        messages = mensagens,
        temperature = temperatura,
        stream = stream
        )
    return resposta.choices[0].message.content

st.title("Trascrição e Resumo de Áudio")

# Criar a pasta e colocar no mesmo diretório do programa para armazenar os arquivos de áudio
custom_path = Path.cwd() / "Arquivos de Audio"

# No caso de a pasta já existir, criar uma iteração para excluir dessa pasta os arquivos
if custom_path.exists() == False:
    custom_path.mkdir(exist_ok=True)
else:
    for arquivo in custom_path.glob("*"):
        arquivo.unlink()

# Carregar o arquivo no Streamlit:
arquivo_para_transcrever = st.file_uploader(label="Carregue seu áudio em formato .mp3",
                            type=['mp3'],
                            accept_multiple_files=False)

# Salvar o arquivo dentro do diretório:
if arquivo_para_transcrever != None:
    
    caminho_completo = Path(f'{custom_path}/{arquivo_para_transcrever.name}')
    
    with open (caminho_completo, "wb") as f:
        f.write(arquivo_para_transcrever.getbuffer())        

    if st.button("Transcrever áudio"):
        # Transcrição feita com a API da OPENAI
        texto_transcrito = transcrever_arquivo(caminho_completo)

        # Resumo feito com a API da OPENAI
        mensagem = [{'role': 'user', 'content': comando.format(texto_transcrito)}]
        texto_resumido = resumir_texto(mensagens=mensagem)    

        # Criar o botão para transcrever o áudio:
        st.divider()
        st.write("Abaixo o resumo por tópicos do áudio:")   
        texto_resumido

        st.divider()
        st.write("Abaixo a transcrição do áudio:")
        texto_transcrito

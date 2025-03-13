import streamlit as st
import requests
from googletrans import Translator  # Biblioteca para tradução
import json

st.sidebar.header("Respostas de Imagens")
st.sidebar.write("""
- Carregue uma imagem e escolha um tom de resposta.

- Caso tenha alguma idéia para publicarmos, envie uma mensagem para: 11-990000425 (Willian)
- Contribua com qualquer valor para mantermos a pagina no ar. PIX (wpyagami@gmail.com)
""")


# Recupera as chaves de acesso dos segredos do Streamlit
hf_key = st.secrets["hungging"]
qwen_key = st.secrets["qwen_key"]
API_URL_HF = "https://router.huggingface.co/hf-inference/models/Salesforce/blip-image-captioning-base"
API_URL_QWEN = "https://openrouter.ai/api/v1/chat/completions"
headers_hf = {"Authorization": f"Bearer {hf_key}"}
headers_qwen = {
    "Authorization": f"Bearer {qwen_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://seu-dominio.com",
    "X-Title": "RimaBot",
}

def query(file):
    # Garante que o ponteiro do arquivo esteja no início e envia a imagem para a API
    file.seek(0)
    data = file.read()
    response = requests.post(API_URL_HF, headers=headers_hf, data=data)
    return response.json()

def traduzir_legenda(texto):
    """Traduz o texto gerado de inglês para português."""
    translator = Translator()
    traducao = translator.translate(texto, src='en', dest='pt')
    return traducao.text

def extrair_legenda(result):
    """
    Extrai a legenda gerada a partir da resposta JSON e a traduz para o português.
    """
    if isinstance(result, list) and len(result) > 0:
        legenda_en = result[0].get("generated_text", "Nenhuma legenda encontrada.")
        if legenda_en == "Nenhuma legenda encontrada.":
            return legenda_en
        return traduzir_legenda(legenda_en)
    return "Formato de resultado inesperado."

def gerar_resposta_em_rima(mensagem, tom):
    """Gera uma resposta em rima usando a API do Qwen com o tom especificado."""
    response = requests.post(
        url=API_URL_QWEN,
        headers=headers_qwen,
        data=json.dumps({
            "model": "qwen/qwen2.5-vl-72b-instruct:free",
            "messages": [
                {"role": "system", "content": f"Responda em um tom {tom}."},
                {"role": "user", "content": mensagem},
            ],
        })
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def main():
    st.title("Respostas de Imagens")
    st.write("Faça o upload de uma imagem para obter uma legenda traduzida automaticamente!")

    # Seção de upload de imagem
    uploaded_file = st.file_uploader("Selecione uma imagem", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Imagem selecionada", use_column_width=True)
        
        # Geração automática da legenda
        with st.spinner("Processando e traduzindo..."):
            result = query(uploaded_file)
            legenda = extrair_legenda(result)
        #st.success("Legenda gerada e traduzida:")
        #st.write(legenda)

    # Seção de mensagem para resposta em rima
    #st.subheader("Envie uma mensagem!")
    
    # Opções de tom para a resposta
    tons = ["engraçado", "poético", "amoroso", "emotivo", "pessimista", "sarcástico", "inspirador","nervoso","desafiador","com rima","sensacionalista","medroso","alegre","otimista"]
    tom_selecionado = st.selectbox("Escolha o tom da resposta:", tons)
    
    if st.button("Gerar Resposta"):
            with st.spinner("Gerando resposta ..."):
                resposta = gerar_resposta_em_rima(legenda, tom_selecionado)
            st.success("Resposta:")
            st.write(resposta)

if __name__ == "__main__":
    main()
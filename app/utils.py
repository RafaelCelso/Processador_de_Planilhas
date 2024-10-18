import os
import pandas as pd
from googletrans import Translator, LANGUAGES
import openai
import logging
import traceback
from flask import current_app

logging.basicConfig(level=logging.INFO)

# Adicione isso no início do arquivo, após as importações
# os.environ['OPENAI_API_KEY'] = "sk-u_t_QNRp012GehqrfaC68_QNg7Ywg8u_xfh_pkaodT3B1bkFJVOhZkSEPQoBmZYeQ_Miz7oQrp2J_FZXYp5SOMkYEIA"

def process_excel(filename):
    try:
        logging.info(f"Lendo arquivo Excel: {filename}")
        df = pd.read_excel(filename)
        processed_file = os.path.join(os.path.dirname(filename), 'processed_' + os.path.basename(filename))
        df.to_excel(processed_file, index=False)
        logging.info(f"Arquivo processado: {processed_file}")
        return processed_file
    except Exception as e:
        logging.error(f"Erro ao processar o arquivo: {str(e)}")
        logging.error(traceback.format_exc())
        raise

def translate_excel(filename):
    try:
        logging.info(f"Iniciando tradução do arquivo: {filename}")
        df = pd.read_excel(filename)
        translator = Translator()
        
        # Traduzir os cabeçalhos das colunas
        translated_columns = [translator.translate(col, dest='en').text for col in df.columns]
        df.columns = translated_columns
        
        # Traduzir o conteúdo das células
        for column in df.columns:
            df[column] = df[column].apply(lambda x: translator.translate(str(x), dest='en').text if pd.notna(x) else x)
        
        translated_file = os.path.join(os.path.dirname(filename), 'translated_' + os.path.basename(filename))
        df.to_excel(translated_file, index=False)
        logging.info(f"Arquivo traduzido: {translated_file}")
        return translated_file
    except Exception as e:
        logging.error(f"Erro ao traduzir o arquivo: {str(e)}")
        logging.error(traceback.format_exc())
        raise

def generate_summary(filename):
    try:
        logging.info(f"Gerando resumo para o arquivo: {filename}")
        df = pd.read_excel(filename)
        content = df.to_string(index=False)
        
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY não está definida no ambiente")
        
        logging.info(f"Usando chave API: {openai.api_key[:5]}...") # Mostra apenas os primeiros 5 caracteres por segurança
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes Excel data."},
                    {"role": "user", "content": f"Summarize the following Excel data:\n\n{content}"}
                ],
                max_tokens=150
            )
            
            summary = response.choices[0].message['content'].strip()
            logging.info("Resumo gerado com sucesso")
        except openai.error.RateLimitError:
            logging.error("Cota da API OpenAI excedida")
            summary = "Não foi possível gerar o resumo devido a limitações da API. Por favor, tente novamente mais tarde."
        
        return summary
    except Exception as e:
        logging.error(f"Erro ao gerar o resumo: {str(e)}")
        logging.error(traceback.format_exc())
        raise

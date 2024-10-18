from flask import render_template, request, jsonify, send_file, current_app, Response
from app import app
from app.utils import process_excel, translate_excel, generate_summary
import os
import logging
import traceback
import json
import tempfile

# Substitua a definição de UPLOAD_FOLDER por:
UPLOAD_FOLDER = tempfile.gettempdir()
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    app.logger.info("Acessando a rota raiz")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    app.logger.info("Iniciando upload de arquivo")
    try:
        if 'file' not in request.files:
            app.logger.error("Nenhum arquivo enviado")
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            app.logger.error("Nenhum arquivo selecionado")
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if file and file.filename.endswith('.xlsx'):
            app.logger.info(f"Processando arquivo: {file.filename}")
            filename = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filename)
            app.logger.info(f"Arquivo salvo em: {filename}")
            
            def generate():
                app.logger.info("Iniciando geração de resposta")
                yield json.dumps({"progress": 10, "status": "Arquivo recebido"}) + '\n'
                
                app.logger.info("Iniciando processamento do Excel")
                processed_file = process_excel(filename)
                app.logger.info(f"Arquivo processado: {processed_file}")
                yield json.dumps({"progress": 40, "status": "Arquivo processado"}) + '\n'
                
                app.logger.info("Iniciando tradução do Excel")
                translated_file = translate_excel(processed_file)
                app.logger.info(f"Arquivo traduzido: {translated_file}")
                yield json.dumps({"progress": 70, "status": "Arquivo traduzido"}) + '\n'
                
                app.logger.info("Gerando resumo")
                try:
                    summary = generate_summary(translated_file)
                    app.logger.info("Resumo gerado com sucesso")
                except Exception as e:
                    app.logger.error(f"Erro ao gerar resumo: {str(e)}")
                    summary = "Não foi possível gerar o resumo. Por favor, tente novamente mais tarde."
                
                final_response = {
                    "progress": 100,
                    "status": "Concluído",
                    "message": 'Arquivo processado com sucesso',
                    "summary": summary,
                    "translated_file": os.path.basename(translated_file)
                }
                yield json.dumps(final_response) + '\n'
            
            return Response(generate(), mimetype='application/json')
        else:
            app.logger.error("Tipo de arquivo não suportado")
            return jsonify({'error': 'Tipo de arquivo não suportado'}), 400
    except Exception as e:
        app.logger.error(f"Erro durante o processamento: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            current_app.logger.error(f"Arquivo não encontrado: {file_path}")
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        current_app.logger.error(f"Erro ao baixar o arquivo: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Erro ao baixar o arquivo'}), 500

@app.route('/generate_summary', methods=['POST'])
def generate_summary_route():
    data = request.json
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'Nome do arquivo não fornecido'}), 400
    
    try:
        summary = generate_summary(filename)
        return jsonify({'summary': summary})
    except Exception as e:
        logging.error(f"Erro ao gerar resumo: {str(e)}")
        return jsonify({'error': str(e)}), 500

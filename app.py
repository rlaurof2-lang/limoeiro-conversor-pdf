import hmac
import os
import subprocess
import tempfile
from pathlib import Path
from flask import Flask, jsonify, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
MAX_MB = 25
app.config['MAX_CONTENT_LENGTH'] = MAX_MB * 1024 * 1024
ALLOWED = {'.pptx', '.ppt', '.docx', '.doc', '.xlsx', '.xls', '.odt', '.odp', '.ods'}

@app.get('/health')
def health():
    return jsonify(status='ok', converter='libreoffice')

@app.post('/convert')
def convert():
    expected = os.environ.get('CONVERTER_API_KEY', '')
    provided = request.headers.get('X-API-Key', '')
    if not expected:
        return jsonify(error='Servidor não configurado: CONVERTER_API_KEY ausente'), 503
    if not hmac.compare_digest(provided, expected):
        return jsonify(error='Não autorizado'), 401
    uploaded = request.files.get('file')
    if uploaded is None or not uploaded.filename:
        return jsonify(error='Envie um arquivo no campo file'), 400
    suffix = Path(uploaded.filename).suffix.lower()
    if suffix not in ALLOWED:
        return jsonify(error='Formato não suportado'), 400
    with tempfile.TemporaryDirectory(prefix='limoeiro-') as directory:
        folder = Path(directory)
        filename = secure_filename(uploaded.filename) or f'documento{suffix}'
        if Path(filename).suffix.lower() != suffix:
            filename = f'documento{suffix}'
        source = folder / filename
        uploaded.save(source)
        out = folder / 'output'
        out.mkdir()
        profile = folder / 'lo-profile'
        try:
            result = subprocess.run(
                ['libreoffice', f'-env:UserInstallation=file://{profile}', '--headless',
                 '--convert-to', 'pdf', '--outdir', str(out), str(source)],
                capture_output=True, text=True, timeout=90,
            )
        except subprocess.TimeoutExpired:
            return jsonify(error='Tempo de conversão excedido'), 504
        pdf = out / f'{source.stem}.pdf'
        if result.returncode != 0 or not pdf.is_file():
            return jsonify(error='Não foi possível converter este documento'), 422
        data = pdf.read_bytes()
        from io import BytesIO
        return send_file(BytesIO(data), mimetype='application/pdf', as_attachment=True,
                         download_name=f'{source.stem}.pdf')

@app.errorhandler(413)
def too_large(_):
    return jsonify(error=f'Arquivo excede {MAX_MB} MB'), 413

if __name__ == '__main__':
    from gunicorn.app.base import BaseApplication
    class Server(BaseApplication):
        def load_config(self):
            self.cfg.set('bind', f'0.0.0.0:{int(os.environ.get("PORT", "10000"))}')
            self.cfg.set('workers', 1)
            self.cfg.set('timeout', 120)
        def load(self):
            return app
    Server().run()

# LIMOEIRO APRESENTA — Conversor PDF

Serviço de conversão de documentos para PDF com LibreOffice, Flask e Docker.

## Hospedagem no Render

1. Publique os arquivos deste repositório no GitHub.
2. No Render, escolha **New > Web Service** e conecte este repositório.
3. Escolha **Docker** como ambiente, caso não seja detectado automaticamente.
4. Em **Environment**, crie `CONVERTER_API_KEY` com uma senha aleatória forte (não a publique no GitHub).
5. Escolha o plano gratuito **se estiver disponível e for suficiente**. O LibreOffice pode ultrapassar os limites de memória do plano gratuito; confirme antes de depender dele.
6. Aguarde a implantação e abra `https://SEU-SERVICO.onrender.com/health`. Deve retornar `{"status":"ok","converter":"libreoffice"}`.

## API

`POST /convert` com `multipart/form-data`, campo `file`, e cabeçalho `X-API-Key` com o segredo configurado. Retorna um PDF (`application/pdf`).

Formatos: PPTX, PPT, DOCX, DOC, XLSX, XLS, ODT, ODP, ODS. Limite: 25 MB; timeout de conversão: 90 segundos.

**Segurança:** nunca coloque a chave da API no código do navegador. A integração com o Base44 deverá chamar este serviço exclusivamente por uma função backend com segredo armazenado no servidor. O endpoint `/health` é público; `/convert` exige autenticação. Não hospede apresentações confidenciais em serviços de terceiros sem autorização.

## Observações

A aparência dos documentos convertidos depende das fontes instaladas e da compatibilidade do LibreOffice. Animações PowerPoint não são mantidas no PDF. Este projeto não altera nenhum arquivo original armazenado no Base44.

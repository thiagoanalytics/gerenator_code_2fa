# TOTP Project — README

Este repositório contém scripts para **gerar códigos TOTP (2FA)** e **extrair a secret de um QR code** para uso com `pyotp`. O objetivo é permitir que você gere automaticamente o código de autenticação (o mesmo que apareceria no Microsoft/Google Authenticator) e o utilize em automações (por exemplo, com Selenium).

---

## Conteúdo do repositório

- `code_generator.py` — script simples que carrega a `TOTP_SECRET` (de `.env` ou variável de ambiente) e imprime o código atual e o tempo restante.
- `read_qrcode.py` — script que lê uma imagem de QR code (ex.: `qrcode.png`), decodifica a URI `otpauth://...` e extrai a `secret` Base32.
- `.sample-env` — exemplo de arquivo `.env` com a variável `TOTP_SECRET` (não comite seu `.env` real).
- `requirements.txt` — lista de dependências do projeto.

---

## Bibliotecas usadas

As principais bibliotecas utilizadas são:

- `pyotp` — gera e verifica códigos TOTP/HOTP.
- `python-dotenv` — carrega variáveis de ambiente a partir de um arquivo `.env` (opcional).
- `pillow` (PIL) — manipulação básica de imagens (usado pelo leitor de QR).
- `pyzbar` — decodificador de códigos de barra/QR para imagens.


Exemplo de `requirements.txt`:

```
pyotp
python-dotenv
pillow
pyzbar

```

> Observação: em algumas plataformas, `pyzbar` precisa de bibliotecas do sistema (por exemplo, `libzbar` no Linux). Consulte a documentação de `pyzbar` para instruções específicas do seu sistema.

---

## 1) `code_generator.py` — explicação do script

### Objetivo
Gerar o código TOTP atual a partir de uma chave secreta (Base32) e exibir quanto tempo falta para expirar.

### Como funciona (resumo)
1. Carrega a `TOTP_SECRET` da variável de ambiente ou do `.env` (se presente).
2. Cria um objeto `pyotp.TOTP(secret)`.
3. Gera o código com `totp.now()` e calcula o tempo restante até o próximo ciclo com `totp.interval`.
4. Exibe o código e o tempo restante. Opcionalmente copia o código para a área de transferência com `pyperclip`.

### Uso
1. Crie um arquivo `.env` (ou defina a variável de ambiente):

```
TOTP_SECRET=JBSWY3DPEHPK3PXP
```

2. Execute:

```bash
python code_generator.py
```

Saída esperada:

```
Código: 492039  (expira em 22s)
```

---

## 2) `read_qrcode.py` — explicação do script

### Objetivo
Ler uma imagem de QR code que contenha uma URI `otpauth://...` (o padrão usado por apps autenticadores) e extrair a `secret` Base32.

### Como funciona (resumo)
1. Abre a imagem do QR com `PIL`.
2. Usa `pyzbar.decode()` para extrair o texto do QR.
3. Procura o parâmetro `secret=` na URI e o retorna.
4. (Opcional) imprime a URI completa e copia a `secret` para a área de transferência.

### Uso
1. Capture ou salve a imagem do QR (ex.: `qrcode.png`).
2. Execute:

```bash
python read_qrcode.py qrcode.png
```

Saída esperada:

```
URI encontrada: otpauth://totp/MinhaEmpresa:usuario@example.com?secret=JBSWY3DPEHPK3PXP&issuer=MinhaEmpresa
Secret extraída: JBSWY3DPEHPK3PXP
```

---

## 3) Como conseguir a `TOTP_SECRET` (opções)

A `TOTP_SECRET` é a única informação que você precisa para gerar os códigos TOTP com `pyotp`. Abaixo estão as formas que você pode obtê-la:

### Opção A — QR code (mais comum)
- Ao configurar 2FA no site, ele normalmente mostra um QR code.
- Salve a imagem do QR e rode `read_qrcode.py` para extrair a `secret`.

### Opção B — Link `otpauth://...` (direto)
- Alguns sites mostram a URI `otpauth://...` ou um link clicável. Basta copiar o link e extrair `secret=` da query string.
- Exemplo:
  - `otpauth://totp/Issuer:email?secret=JBSWY3DPEHPK3PXP&issuer=Issuer`

### Opção C — Chave manual (Base32)
- Alguns portais liberam a chave em texto (Base32) para digitar manualmente no app. Copie esse texto diretamente para a variável `TOTP_SECRET`.

### Opção D — Links redirecionadores (ex.: aka.ms/...)
- Links curtos/redirecionadores podem abrir o app do autenticador e não conter a `secret` visível.
- Nesse caso, você tem 2 alternativas:
  1. Capturar o QR gerado pelo fluxo (usando print da tela ou automatização com Selenium) e decodificá-lo com `read_qrcode.py`.
  2. Se o fluxo exigir login antes do QR, automatize com Selenium para chegar à tela que mostra o QR e salve a imagem do QR para decodificação.

### Opção E — Quando o serviço não usa TOTP (push only)
- Alguns serviços oferecem *apenas* autenticação por push (aprovado no app). Isso **não** é compatível com `pyotp`.
- Nesses casos, verifique se há opção para configurar "Outro app autenticador" ou chave manual. Caso contrário, não será possível usar TOTP.

---

## 4) Boas práticas e segurança

- **NUNCA** compartilhe sua `TOTP_SECRET`. Quem tiver a secret pode gerar os códigos 2FA da sua conta.
- Não comite arquivos `.env` com secrets em repositórios públicos.
- Para produção, use um **secret manager** (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault) ou o `keyring` do sistema.
- Registre uso e auditoria, mas **nunca** logue a secret nem os códigos TOTP em texto plano.
- Sincronize o relógio do seu sistema (NTP) para evitar problemas de validade dos códigos.

---

## 5) Exemplos de código (resumidos)

### `code_generator.py` (exemplo minimal):

```python
import os
import time
import pyotp
from dotenv import load_dotenv

load_dotenv()
secret = os.getenv("TOTP_SECRET")
if not secret:
    raise SystemExit("TOTP_SECRET não encontrada. Defina a variável de ambiente ou .env")

totp = pyotp.TOTP(secret)
code = totp.now()
interval = totp.interval
remaining = interval - (int(time.time()) % interval)
print(f"Código: {code}  (expira em {remaining}s)")
```

### `read_qrcode.py` (exemplo minimal):

```python
import sys
from PIL import Image
from pyzbar.pyzbar import decode
import re

img_path = sys.argv[1]
img = Image.open(img_path)
decoded = decode(img)
if not decoded:
    raise SystemExit("Nenhum QR code encontrado na imagem")

text = decoded[0].data.decode()
print("URI encontrada:", text)

m = re.search(r"secret=([A-Z2-7]+)", text)
if m:
    secret = m.group(1)
    print("Secret extraída:", secret)
else:
    print("Secret não encontrada na URI")
```

> Observação: o regex acima assume Base32 (`A-Z2-7`). Ajuste se necessário.

---

## 6) Instalação rápida

1. Crie e ative um ambiente virtual (recomendado):

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows PowerShell
```

2. Instale dependências:

```bash
pip install -r requirements.txt
```

3. Configure seu `.env` com `TOTP_SECRET` ou defina a variável de ambiente.

---

## 7) Próximos passos / extras

- Integrar `code_generator.py` ao seu fluxo Selenium para preencher automaticamente o campo 2FA.
- Persistir e reutilizar cookies do Selenium para reduzir necessidade de 2FA em execuções repetidas.
- Adicionar suporte a múltiplas contas (arquivo JSON/CSV com secrets por usuário).

---

Se quiser, eu adapto este README para um formato específico (por exemplo, README.md com badges, ou versão em inglês) ou gero o `requirements.txt` e os scripts prontos no repositório. É só me dizer o que prefere.


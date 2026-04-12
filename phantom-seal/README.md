# phantom-seal

POC educacional — Q-Trust: prova de integridade temporal pós-quântica para arquivos de
Saúde e Segurança do Trabalho (SST), com selagem em blockchain de teste (Sepolia).

> **Este repositório NÃO é código de produção.**

---

## O que faz

```
Arquivo (ASO, PCMSO, …)
        │
        ▼
  SHA3-256 hash (32 bytes)
        │
        ├──► Assinatura Dilithium3 (PQC, via liboqs)
        │
        └──► calldata = QTST ‖ hash  →  tx Sepolia (imutável, com timestamp de bloco)
                                │
                         evidence/
                           bundle_<ts>_<txid>.json   ← tudo para verificar depois
                           laudo_<ts>.md             ← laudo humano legível
```

## Estrutura

```
phantom-seal/
├── .env.example              # variáveis necessárias
├── requirements.txt
├── logs/
│   └── sample_aso.pdf        # arquivo de entrada (coloque o PDF real aqui)
├── scripts/
│   ├── seal.py               # pipeline completo: hash → assinar → ancorar → laudo
│   └── verify.py             # 3 camadas: hash local, on-chain, assinatura PQC
└── evidence/
    ├── laudo_template.md     # template preenchido pelo seal.py
    ├── bundle_<ts>_<tx>.json # gerado após cada selagem
    └── laudo_<ts>.md         # gerado após cada selagem
```

## Configuração

```bash
pip install -r requirements.txt

cp .env.example .env
# edite .env com suas credenciais:
#   RPC_URL_SEPOLIA=https://sepolia.infura.io/v3/<PROJECT_ID>
#   WALLET_PRIVATE_KEY=0x<CHAVE_PRIVADA_TESTNET>
```

> Use uma carteira **exclusiva para testnet** — nunca exponha chaves de produção.

## Uso

### Selar um arquivo

```bash
python scripts/seal.py logs/sample_aso.pdf
```

Saída:
```
[1/4] Computing SHA3-256 …
[2/4] Signing with Dilithium3 (post-quantum) …
[3/4] Anchoring to Sepolia (calldata=36 bytes) …
      tx   : 0xabc123…
      block: 7654321
[4/4] Writing evidence …
      bundle : bundle_2026-04-12_10-30-00_abc123.json
      laudo  : laudo_2026-04-12_10-30-00.md
```

### Verificar integridade

```bash
python scripts/verify.py logs/sample_aso.pdf evidence/bundle_<...>.json
```

Resultado:
```
[1/3] SHA3-256 hash   : PASS
[2/3] On-chain anchor : PASS
[3/3] Dilithium3 sig  : PASS

RESULT: INTEGRITY CONFIRMED — file is identical to the sealed original.
```

## Formato do calldata

```
bytes[0:4]   = 0x51545354  ("QTST" — Q-Trust Seal Token)
bytes[4:36]  = SHA3-256(arquivo)  (32 bytes)
```

Simples e auditável: qualquer cliente Ethereum pode inspecionar a transação sem
dependência de contratos ou infraestrutura proprietária.

## Dependências principais

| Biblioteca | Função |
|---|---|
| `oqs-python` | Dilithium3 via liboqs (NIST PQC Round 3) |
| `web3.py` | Submissão e consulta na Sepolia |
| `cryptography` | Suporte a primitivas criptográficas auxiliares |
| `python-dotenv` | Carregamento seguro de credenciais |

## Limitações desta POC

- A chave privada Dilithium3 é **ephemeral**: gerada na memória e descartada.
  O `bundle.json` guarda apenas a chave **pública** e a assinatura.
- Não há contrato inteligente: o proof-of-existence é a própria transação Sepolia.
- Para produção seria necessário: gestão de chaves (HSM/KMS), contrato de registro,
  e integração com e-SOCIAL / eSocial para ASOs.

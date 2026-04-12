# PRODUCT_REQUIREMENTS_PHANTOMSEAL

## 1. Visão do Produto

O PhantomSeal deve evoluir de utilitário técnico isolado para capacidade nativa do Lumina, atuando como módulo de confiança para prova técnica de integridade, autoria criptográfica e ancoragem pública verificável de documentos digitais sensíveis.

No contexto do Lumina, o produto deve servir como infraestrutura de prova para documentos clínicos, documentos de SST/NR-1, registros de compliance e decisões sensíveis que exijam rastreabilidade, auditabilidade e possibilidade de verificação independente.

O módulo não deve ser tratado como ferramenta promocional de blockchain. Seu papel de produto é institucional: registrar, preservar e permitir a revalidação posterior de evidências técnicas associadas a documentos relevantes para saúde, governança e compliance.

---

## 2. Problema que o Produto Resolve

Em ambientes sensíveis, não basta emitir, armazenar ou circular um documento. É necessário demonstrar, posteriormente:

- qual documento foi efetivamente usado;
- se o conteúdo apresentado depois é o mesmo que existia no momento da decisão;
- qual identidade criptográfica o assinou;
- se houve ou não ancoragem pública;
- se um terceiro independente consegue revalidar a prova.

O Lumina já descreve, em seu README, uma camada de auditoria em que saídas de IA são registradas, timestampadas e explicáveis. O PhantomSeal é a evolução operacional dessa lógica para documentos e artefatos críticos: um mecanismo de prova técnica de integridade, assinatura e eventual ancoragem pública.

---

## 3. Proposta de Valor

O PhantomSeal deve oferecer ao Lumina uma capacidade nativa de:

- selar documentos sensíveis;
- produzir evidência técnica estruturada;
- permitir verificação independente;
- reforçar trilha probatória institucional;
- sustentar auditoria interna, compliance e defesa técnica.

A proposta de valor não é “assinar em blockchain”.

A proposta de valor é: **provar, depois, que determinado documento existia naquela forma, foi associado a uma assinatura específica e pode ser revalidado tecnicamente por terceiros.**

---

## 4. Casos de Uso Prioritários

### 4.1 Saúde / Lumina

- congelamento de versão de parecer clínico sensível;
- prova de integridade de relatório de risco psicossocial;
- trilha auditável de decisão assistencial relevante;
- prova técnica complementar de anexos críticos.

### 4.2 SST / NR-1

- preservação de versões de documentos de risco psicossocial;
- reforço de prova de diligência documental;
- registro técnico de documentos utilizados em avaliação ocupacional.

### 4.3 Compliance e Governança

- preservação de decisões internas sensíveis;
- registro verificável de anexos de auditoria;
- reforço de trilha de integridade para documentos internos.

### 4.4 Contencioso e Perícia

- produção de pacote técnico para auditoria;
- verificação independente de integridade e assinatura;
- reforço probatório complementar em discussão judicial ou administrativa.

---

## 5. Superfícies de Produto

O produto deve ser exposto em três superfícies principais.

### 5.1 Seal Console

Interface para:

- enviar documento;
- calcular hash;
- mostrar prévia da prova;
- selecionar modo (`dry-run` ou `on-chain`);
- gerar evidência.

### 5.2 Verify Console

Interface para:

- carregar documento e JSON de evidência;
- revalidar hash;
- revalidar assinatura;
- verificar transação on-chain, quando houver;
- exibir resultado consolidado de verificação.

### 5.3 Evidence Registry

Registro consultável de evidências geradas, com filtros por:

- hash;
- tx_hash;
- data;
- tipo de documento;
- status de verificação;
- endereço do signatário;
- identificador de caso ou referência interna.

---

## 6. Fluxo de Produto

Fluxo mínimo viável:

1. usuário seleciona o documento;
2. sistema calcula o hash SHA3-256;
3. sistema exibe resumo do documento e do hash;
4. usuário confirma o modo de operação (`dry-run` ou `on-chain`);
5. sistema assina a mensagem derivada do hash;
6. sistema gera payload QTST;
7. sistema, se aplicável, ancora em Sepolia;
8. sistema gera JSON de evidência;
9. sistema registra os metadados em índice interno;
10. sistema disponibiliza revalidação posterior via Verify Console.

---

## 7. Estrutura de Dados de Produto

Além do JSON bruto, o produto deve indexar, no mínimo:

- `document_hash`
- `document_name`
- `document_type`
- `size_bytes`
- `signer_address`
- `timestamp_utc`
- `dry_run`
- `tx_hash`
- `chain_id`
- `network`
- `status_verification`
- `evidence_path`
- `case_id` ou `reference_id`, quando aplicável

Em ambiente de saúde, qualquer associação com paciente ou caso deve obedecer à governança adequada de acesso e minimização de exposição.

---

## 8. Requisitos Funcionais

### RF-01 — Selagem de documento

O sistema deve aceitar um arquivo e calcular seu SHA3-256.

### RF-02 — Assinatura criptográfica

O sistema deve gerar assinatura ECDSA da mensagem `PHANTOM-SEAL::<hash>`.

### RF-03 — Geração de payload QTST

O sistema deve construir payload com prefixo QTST e hash do documento.

### RF-04 — Operação em dry-run

O sistema deve permitir gerar evidência sem envio on-chain.

### RF-05 — Ancoragem em Sepolia

O sistema deve permitir envio opcional de transação para Sepolia.

### RF-06 — Persistência da evidência

O sistema deve gerar e armazenar JSON de evidência.

### RF-07 — Verificação independente

O sistema deve oferecer fluxo para revalidar hash, assinatura e ancoragem.

### RF-08 — Registro interno

O sistema deve indexar as evidências geradas para posterior consulta.

### RF-09 — Exportação de pacote probatório

O sistema deve permitir exportar documento + evidência + dados de verificação.

---

## 9. Requisitos Não Funcionais

### RNF-01 — Segurança

Chaves privadas não devem ser expostas em interface de usuário.

### RNF-02 — Auditabilidade

Todo evento relevante deve gerar registro de auditoria.

### RNF-03 — Integridade de evidência

A evidência deve poder ser revalidada independentemente.

### RNF-04 — Segregação de funções

O produto deve suportar separação entre quem sela, quem verifica e quem audita.

### RNF-05 — Retenção

O produto deve prever retenção configurável de evidências.

### RNF-06 — Escalabilidade operacional

O módulo deve operar como serviço interno do Lumina, não apenas como script manual.

---

## 10. Segurança do Produto

Requisitos mínimos:

- chave nunca exposta à interface;
- execução em ambiente segregado;
- logs imutáveis ou fortemente controlados;
- trilha de auditoria de acesso;
- retenção configurável;
- proteção de evidências críticas;
- evolução futura para KMS/HSM.

Riscos conhecidos:

- vazamento de chave privada;
- adulteração do JSON de evidência;
- uso indevido do módulo por operador autorizado além do necessário;
- evidência técnica correta associada a documento materialmente falso.

---

## 11. MVP do Produto

O MVP real do PhantomSeal como produto deve incluir:

- módulo `Seal`;
- módulo `Verify`;
- painel simples de evidências;
- exportação de pacote probatório;
- `dry-run` como padrão;
- Sepolia como ambiente de validação.

---

## 12. Roadmap de Produto

### Curto prazo

- integrar signer/verify ao backend do Lumina;
- registrar evidências em banco;
- criar tela de consulta;
- corrigir CI;
- consolidar documentação.

### Médio prazo

- workflow institucional de aprovação;
- integração com documentos clínicos e SST;
- relatórios de verificação;
- trilha de diligência organizacional.

### Longo prazo

- chaves em KMS/HSM;
- assinatura híbrida ECDSA + pós-quântica;
- ambiente de produção;
- carimbo do tempo externo;
- integração com camadas jurídicas formais.

---

## 13. Tese do Produto

A tese central do PhantomSeal como produto é:

> Em ambientes sensíveis, não basta decidir.
> É preciso provar, depois, o que foi decidido, sobre qual documento, com qual integridade e sob qual responsabilidade técnica.

O PhantomSeal deve ser o mecanismo institucional do Lumina para transformar essa necessidade em capacidade operacional.

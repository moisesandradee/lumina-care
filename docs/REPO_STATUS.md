# REPO_STATUS

## Objetivo deste documento

Este arquivo descreve o estado operacional real do repositório `lumina-care`, separando com clareza o que é conceito, o que já é executável e o que ainda está em transição.

---

## 1. Estado Geral do Repositório

O repositório combina duas naturezas:

1. **Camada conceitual / estratégica**
   - visão de produto
   - arquitetura proposta
   - documentação de ideação
   - materiais de roadmap, ética e posicionamento

2. **Camada operacional / executável**
   - workflows GitHub Actions
   - módulo `phantom-seal/`
   - partes da estrutura `src/` com caráter ilustrativo e parcial

A regra prática é:

- nem todo arquivo deste repositório representa software pronto para produção;
- parte relevante do repositório é proposicional, não operacional.

---

## 2. O que hoje é predominantemente conceitual

Os seguintes elementos devem ser lidos principalmente como artefatos de proposta:

- `README.md` (visão geral do produto e tese)
- documentação em `docs/` relacionada a visão, roadmap e estratégia
- materiais em `pitch/`, `demo/`, `research/`, `ethics/` e `prompts/`
- partes da estrutura `src/` descritas como ilustrativas

Esses conteúdos são úteis para:
- posicionamento
- entendimento da arquitetura pretendida
- comunicação de produto
- alinhamento estratégico

Eles **não devem ser interpretados automaticamente como implementação validada em produção**.

---

## 3. O que hoje é operacional ou quase operacional

### 3.1 PhantomSeal

O módulo `phantom-seal/` é hoje o principal trilho operacional do repositório.

Arquivos relevantes:
- `phantom-seal/signer.py`
- `phantom-seal/verify.py`
- `phantom-seal/requirements.txt`

Capacidades pretendidas e parcialmente materializadas:
- hashing SHA3-256
- assinatura ECDSA
- geração de evidência JSON
- fluxo de verificação
- execução em `DRY_RUN=true`

### 3.2 GitHub Actions

O workflow ligado ao PhantomSeal é o principal mecanismo de validação executável do repositório neste momento.

Arquivo relevante:
- `.github/workflows/python-app.yml`

Objetivo atual do workflow:
- instalar dependências mínimas
- criar documento de teste
- rodar `signer.py`
- validar a evidência com `verify.py`

---

## 4. Trilhos de CI atualmente existentes

### 4.1 PhantomSeal CI

Escopo desejado:
- validar apenas o fluxo do PhantomSeal
- não depender de frontend, Next.js ou TypeScript
- falhar apenas quando houver erro real no fluxo Python

### 4.2 Validate / Code Quality

Esse trilho deve ser tratado como independente do PhantomSeal.

Ele pode envolver:
- frontend
- lint/format
- estrutura TypeScript/Next.js
- documentos formatados por Prettier

Regra de governança:
- **não misturar correções do Validate com correções do PhantomSeal no mesmo PR**.

---

## 5. O que ainda está pendente

Itens ainda em aberto ou em transição:
- estabilização final do workflow do PhantomSeal
- revisão de documentação própria do módulo `phantom-seal/`
- integração formal do PhantomSeal com backend FastAPI
- padronização de branches e PRs de agentes automáticos
- proteção de branch e governança mínima

---

## 6. Leitura correta do repositório

A interpretação correta hoje é:

- **Lumina** = repositório-âncora de tese + produto + estrutura parcial
- **PhantomSeal** = componente mais próximo de validação operacional real
- **CI** = principal sinal de maturidade técnica de curto prazo

Em termos práticos:
- a confiabilidade do repositório depende mais da estabilidade dos workflows do que da quantidade de documentação já escrita;
- a evolução saudável exige separar claramente mudanças de conceito, mudanças de produto e mudanças de infraestrutura.

---

## 7. Próximos passos recomendados

1. estabilizar definitivamente o `phantom-seal CI`
2. revisar `phantom-seal/README.md`
3. explicitar no `README.md` principal a diferença entre partes conceituais e executáveis
4. criar padrão mínimo para branches, PRs e mudanças de agentes
5. evoluir integração backend apenas depois da estabilidade operacional mínima

---

## 8. Resumo executivo

Hoje, o `lumina-care` deve ser entendido como:

- um repositório forte em visão e arquitetura proposta;
- parcialmente operacional no eixo PhantomSeal;
- ainda em processo de saneamento de CI, escopo e governança.

Esse enquadramento evita falsa percepção de produção pronta e aumenta a confiabilidade institucional do projeto.

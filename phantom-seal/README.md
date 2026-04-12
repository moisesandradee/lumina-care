# phantom-seal

Experimento demonstrativo da tese Q-Trust: prova de integridade temporal pós-quântica
para arquivos de Saúde e Segurança do Trabalho (SST), com selagem em blockchain de teste.

Este repositório NÃO é código de produção. É uma POC educacional para:
- Gerar hash (SHA-3) de um arquivo sensível (ex: ASO).
- Assinar o hash com algoritmo de assinatura digital pós-quântica (via liboqs).
- Ancorar o resultado em uma blockchain de teste (Sepolia) para obter carimbo de tempo imutável.

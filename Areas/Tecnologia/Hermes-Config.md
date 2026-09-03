---
name: hermes-config
description: Configuração e uso do Hermes Agent como ferramenta de automação e renda
metadata:
  type: reference
---

# ⚙️ Hermes Agent - Config

## Status do Sistema
- **Hermes:** ✅ Instalado e funcionando
- **Vault Obsidian:** ✅ Conectado (`Meu-Vault`)
- **Git:** ✅ Configurado (vault versionado)
- **MCP Obsidian:** ✅ Detectado (`.obsidian-mcp/`)

## O que o Hermes pode fazer
- ✅ Criar, ler, editar e pesquisar notas no Obsidian
- ✅ Automatizar tarefas repetitivas
- ✅ Gerar conteúdo com IA
- ✅ Pesquisar na web
- ✅ Executar código e scripts
- ✅ Gerenciar tarefas e projetos
- ✅ Criar e gerenciar cron jobs
- ✅ Browser automation
- ✅ Processar documentos

## Integração com Obsidian
- Acesso via skill `obsidian` (filesystem-first)
- Vault path: `C:\Users\familia gidelu\Documents\Meu-Vault`
- MCP disponível para operações complexas

## Automações Configuráveis
1. **Diário automático** — criar nota diária todo dia
2. **Backup Git** — commit automático do vault
3. **Monitor de ideias** — capturar ideias rapidamente
4. **Relatório semanal** — gerar resumo de produtividade
5. **Research** — pesquisar oportunidades e salvar no vault

## Comandos Úteis
```bash
# Status do vault
hermes vault status

# Criar nota
hermes vault create "Nome da Nota"

# Buscar no vault
hermes vault search "termo"
```

## Segurança
- Dados ficam locais em `~/.hermes/`
- Zero telemetry
- Vault versionado com Git

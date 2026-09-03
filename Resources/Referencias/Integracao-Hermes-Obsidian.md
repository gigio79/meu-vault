---
name: integracao-hermes-obsidian
description: Documento completo de integração Hermes Agent com Obsidian - guia de referência
metadata:
  type: reference
---

# Integração Hermes Agent + Obsidian

> Documento de referência para a integração completa entre Hermes e Obsidian.

## Resumo Executivo
Integrar Hermes com Obsidian permite criar, organizar e sincronizar notas de forma inteligente. Metas: tomada de notas avançada, sincronização, automação e execução de tarefas.

## Componentes
- **Hermes Agent** — agente de IA open-source (Nous Research)
- **Obsidian** — editor Markdown com vaults
- **Plugins:** Templater, Dataview, Obsidian Git, Advanced URI, Local REST API

## Plugins Necessários
| Plugin | Função | Status |
|--------|--------|--------|
| Templater | Templates dinâmicos com JS | ⬜ Instalar |
| Dataview | Consultas inteligentes | ⬜ Instalar |
| Obsidian Git | Backup/sync via Git | ⬜ Instalar |
| Advanced URI | Controle via URIs | ⬜ Instalar |
| Local REST API | Acesso REST ao vault | ⬜ Instalar |

## Como Funciona
```
Hermes → CLI/Shell → Obsidian App → Vault
Hermes → REST API (localhost:27124) → Vault
Hermes → URI (obsidian://) → Obsidian App
```

## Segurança
- Hermes: zero telemetry, dados locais
- Obsidian Sync: AES-256 end-to-end
- Local REST API: chave API + HTTPS local

## Comandos Úteis
```bash
# Via CLI
obsidian create name="Nota" content="# Conteúdo"

# Via REST API
curl -k -H "Authorization: Bearer $API_KEY" https://127.0.0.1:27124/vault/

# Via URI
open "obsidian://adv-uri?filepath=Nota.md&mode=edit"
```

## Status da Configuração
- [x] Obsidian instalado
- [x] Vault criado
- [x] Git configurado
- [ ] Obsidian CLI habilitado (manual)
- [ ] Templater instalado (manual)
- [ ] Dataview instalado (manual)
- [ ] Obsidian Git instalado (manual)
- [ ] Advanced URI instalado (manual)
- [ ] Local REST API instalado (manual)

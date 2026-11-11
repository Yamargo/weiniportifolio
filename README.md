# Portfólio · Vinícius Flórido

Site estático trilíngue (PT / EN / 中文) com tema vermelho e dourado.

## Estrutura
- `site/` — o site pronto (abra `site/index.html` por um servidor estático, ex.: `python3 -m http.server -d site`).
  - `css/` tokens, base e componentes · `js/` módulos ES (router, i18n, lightbox, moedas, vídeo, reveal)
  - `i18n/` traduções `pt.json`, `en.json`, `zh.json` · `assets/` imagens WebP, bandeiras SVG, vídeos, documentos
- `tools/` — scripts que geram `site/index.html` e `site/i18n/*.json` a partir de um único modelo de conteúdo e otimizam as imagens.

## Regenerar
`python3 tools/build_site.py` (ajuste os caminhos no topo do script se mover as pastas).

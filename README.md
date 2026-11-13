# Portfólio · Vinícius

Site trilíngue (PT / EN / 中文) em Go: um único binário com todo o conteúdo embutido, sem dependências externas (só a biblioteca padrão).

```
cmd/portfolio/        ponto de entrada (serve | build)
internal/site/
  site.go             template + dicionários, validação de chaves entre idiomas
  server.go           HTTP: /{lang}/ renderizado no servidor, cabeçalhos de segurança, cache, /healthz
  build.go            gerador estático (GitHub Pages)
  templates/          index.gohtml (HTML semântico; textos vêm de {{t "chave"}})
  static/             css/ js/ (módulos ES) i18n/*.json assets/ (WebP, SVG, vídeo, documentos)
tools/legacy/         scripts Python usados na geração inicial (referência)
docs/                 saída estática gerada (make build)
```

## Uso
```bash
make run          # http://localhost:8080  (/ redireciona pelo Accept-Language)
make test         # vet + testes (renderiza os 3 idiomas, confere chaves)
make build        # gera docs/ para GitHub Pages
docker build -t portfolio . && docker run -p 8080:8080 portfolio
```

Para editar um texto: altere a chave nos três arquivos `internal/site/static/i18n/*.json` (o build falha se um idioma ficar sem a chave).
Páginas: `/pt/`, `/en/`, `/zh/`. O JavaScript cuida da navegação entre abas (#home, #laos, …) e da troca de idioma sem recarregar.

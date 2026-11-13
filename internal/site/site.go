// Package site renders the portfolio: one HTML template, one JSON dictionary per
// language, and a set of embedded static assets. It is used both by the HTTP
// server (serve) and by the static generator (build, for GitHub Pages).
package site

import (
	"bytes"
	"embed"
	"encoding/json"
	"fmt"
	"html/template"
	"io/fs"
	"sort"
)

//go:embed all:static templates/index.gohtml
var content embed.FS

// Lang describes one supported language.
type Lang struct {
	Code     string // URL segment and <html data-lang>
	HTMLLang string // BCP-47 tag for <html lang>
}

// Languages in display order. The first one is the default.
var Languages = []Lang{
	{"pt", "pt-BR"},
	{"en", "en"},
	{"zh", "zh-Hans"},
}

// Site holds the parsed template and dictionaries.
type Site struct {
	tmpl  *template.Template
	dicts map[string]map[string]string
}

// PageData is the data passed to the template.
type PageData struct {
	Lang     string
	HTMLLang string
	Root     string // relative prefix to the site root ("", "../")
	Fixed    bool   // language fixed by the URL (disables client-side auto-detection)
}

// Static returns the embedded static file tree (css, js, i18n, assets...).
func Static() fs.FS {
	sub, err := fs.Sub(content, "static")
	if err != nil {
		panic(err) // embed layout is a compile-time invariant
	}
	return sub
}

// New parses the template and loads every dictionary, failing fast if the
// dictionaries disagree on their keys.
func New() (*Site, error) {
	s := &Site{dicts: map[string]map[string]string{}}
	for _, l := range Languages {
		b, err := content.ReadFile("static/i18n/" + l.Code + ".json")
		if err != nil {
			return nil, err
		}
		d := map[string]string{}
		if err := json.Unmarshal(b, &d); err != nil {
			return nil, fmt.Errorf("i18n %s: %w", l.Code, err)
		}
		s.dicts[l.Code] = d
	}
	if err := s.checkKeys(); err != nil {
		return nil, err
	}
	raw, err := content.ReadFile("templates/index.gohtml")
	if err != nil {
		return nil, err
	}
	// Funcs are bound per render (they close over the language); parse once with placeholders.
	s.tmpl, err = template.New("index").Funcs(template.FuncMap{
		"t":  func(string) string { return "" },
		"th": func(string) template.HTML { return "" },
	}).Parse(string(raw))
	return s, err
}

func (s *Site) checkKeys() error {
	base := s.dicts[Languages[0].Code]
	for _, l := range Languages[1:] {
		d := s.dicts[l.Code]
		var missing []string
		for k := range base {
			if _, ok := d[k]; !ok {
				missing = append(missing, k)
			}
		}
		for k := range d {
			if _, ok := base[k]; !ok {
				missing = append(missing, "+"+k)
			}
		}
		if len(missing) > 0 {
			sort.Strings(missing)
			return fmt.Errorf("i18n %s differs from %s: %v", l.Code, Languages[0].Code, missing)
		}
	}
	return nil
}

// Render produces the full HTML document for a language.
func (s *Site) Render(lang, root string, fixed bool) ([]byte, error) {
	dict, ok := s.dicts[lang]
	if !ok {
		return nil, fmt.Errorf("unknown language %q", lang)
	}
	var htmlLang string
	for _, l := range Languages {
		if l.Code == lang {
			htmlLang = l.HTMLLang
		}
	}
	var missing []string
	look := func(k string) string {
		v, ok := dict[k]
		if !ok {
			missing = append(missing, k)
		}
		return v
	}
	t, err := s.tmpl.Clone()
	if err != nil {
		return nil, err
	}
	t = t.Funcs(template.FuncMap{
		"t":  look,
		"th": func(k string) template.HTML { return template.HTML(look(k)) }, // dictionaries are trusted, first-party content
	})
	var buf bytes.Buffer
	if err := t.Execute(&buf, PageData{Lang: lang, HTMLLang: htmlLang, Root: root, Fixed: fixed}); err != nil {
		return nil, err
	}
	if len(missing) > 0 {
		return nil, fmt.Errorf("template uses undefined keys: %v", missing)
	}
	return buf.Bytes(), nil
}

package site

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestRenderAllLanguages(t *testing.T) {
	s, err := New()
	if err != nil {
		t.Fatal(err)
	}
	for _, l := range Languages {
		b, err := s.Render(l.Code, "../", true)
		if err != nil {
			t.Fatalf("%s: %v", l.Code, err)
		}
		out := string(b)
		if strings.Contains(out, "{{") || strings.Contains(out, "ZgotmplZ") {
			t.Errorf("%s: unrendered template output", l.Code)
		}
		if !strings.Contains(out, `lang="`+l.HTMLLang+`"`) {
			t.Errorf("%s: wrong html lang", l.Code)
		}
		if strings.Contains(out, "Flórido") {
			t.Errorf("%s: full name leaked", l.Code)
		}
	}
}

func TestHandler(t *testing.T) {
	s, err := New()
	if err != nil {
		t.Fatal(err)
	}
	h := s.Handler()
	cases := []struct {
		path, accept string
		status       int
		location     string
	}{
		{"/", "zh-CN,zh;q=0.9", http.StatusFound, "/zh/"},
		{"/", "pt-BR,pt;q=0.9", http.StatusFound, "/pt/"},
		{"/", "fr", http.StatusFound, "/en/"},
		{"/en/", "", http.StatusOK, ""},
		{"/css/tokens.css", "", http.StatusOK, ""},
		{"/healthz", "", http.StatusOK, ""},
		{"/nope", "", http.StatusNotFound, ""},
	}
	for _, c := range cases {
		req := httptest.NewRequest("GET", c.path, nil)
		if c.accept != "" {
			req.Header.Set("Accept-Language", c.accept)
		}
		rec := httptest.NewRecorder()
		h.ServeHTTP(rec, req)
		if rec.Code != c.status {
			t.Errorf("%s (%s): status %d, want %d", c.path, c.accept, rec.Code, c.status)
		}
		if c.location != "" && rec.Header().Get("Location") != c.location {
			t.Errorf("%s: location %q, want %q", c.path, rec.Header().Get("Location"), c.location)
		}
	}
}

package site

import (
	"context"
	"errors"
	"log/slog"
	"net/http"
	"strings"
	"time"
)

// Handler returns the HTTP handler for the site:
//
//	/            → 302 to the best language (Accept-Language)
//	/{lang}/     → server-rendered page
//	/css, /js, /i18n, /assets, /favicon.svg → embedded static files
//	/healthz     → liveness probe
func (s *Site) Handler() http.Handler {
	mux := http.NewServeMux()
	static := http.FileServerFS(Static())

	mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "text/plain; charset=utf-8")
		_, _ = w.Write([]byte("ok\n"))
	})
	mux.HandleFunc("GET /{$}", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Add("Vary", "Accept-Language")
		http.Redirect(w, r, "/"+negotiate(r.Header.Get("Accept-Language"))+"/", http.StatusFound)
	})
	for _, l := range Languages {
		code := l.Code
		mux.HandleFunc("GET /"+code+"/{$}", func(w http.ResponseWriter, _ *http.Request) {
			b, err := s.Render(code, "../", true)
			if err != nil {
				slog.Error("render", "lang", code, "err", err)
				http.Error(w, "internal error", http.StatusInternalServerError)
				return
			}
			w.Header().Set("Content-Type", "text/html; charset=utf-8")
			w.Header().Set("Cache-Control", "no-cache")
			_, _ = w.Write(b)
		})
	}
	mux.Handle("GET /", cacheStatic(static))
	return secure(logging(mux))
}

// negotiate picks the first supported language from an Accept-Language header.
func negotiate(header string) string {
	for _, part := range strings.Split(header, ",") {
		tag := strings.ToLower(strings.TrimSpace(strings.SplitN(part, ";", 2)[0]))
		if len(tag) < 2 {
			continue
		}
		for _, l := range Languages {
			if strings.HasPrefix(tag, l.Code) {
				return l.Code
			}
		}
	}
	return "en"
}

func cacheStatic(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Cache-Control", "public, max-age=86400")
		next.ServeHTTP(w, r)
	})
}

func secure(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		h := w.Header()
		h.Set("X-Content-Type-Options", "nosniff")
		h.Set("Referrer-Policy", "strict-origin-when-cross-origin")
		h.Set("X-Frame-Options", "DENY")
		h.Set("Content-Security-Policy",
			"default-src 'self'; img-src 'self' data:; media-src 'self'; "+
				"style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "+
				"script-src 'self'; connect-src 'self'; base-uri 'self'; frame-ancestors 'none'")
		next.ServeHTTP(w, r)
	})
}

type statusWriter struct {
	http.ResponseWriter
	code int
}

func (w *statusWriter) WriteHeader(c int) { w.code = c; w.ResponseWriter.WriteHeader(c) }

func logging(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		sw := &statusWriter{ResponseWriter: w, code: http.StatusOK}
		next.ServeHTTP(sw, r)
		slog.Info("request", "method", r.Method, "path", r.URL.Path, "status", sw.code, "dur", time.Since(start).Round(time.Microsecond))
	})
}

// Serve runs the site until ctx is cancelled, then shuts down gracefully.
func Serve(ctx context.Context, addr string, h http.Handler) error {
	srv := &http.Server{
		Addr:              addr,
		Handler:           h,
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       15 * time.Second,
		WriteTimeout:      60 * time.Second, // large video files
		IdleTimeout:       60 * time.Second,
	}
	errc := make(chan error, 1)
	go func() { errc <- srv.ListenAndServe() }()
	slog.Info("listening", "addr", addr)
	select {
	case err := <-errc:
		return err
	case <-ctx.Done():
		shutdown, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		if err := srv.Shutdown(shutdown); err != nil && !errors.Is(err, context.Canceled) {
			return err
		}
		return nil
	}
}

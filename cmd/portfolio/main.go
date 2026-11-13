// Command portfolio serves or builds the portfolio site.
//
//	portfolio serve [-addr :8080]
//	portfolio build [-out docs]
package main

import (
	"context"
	"flag"
	"fmt"
	"log/slog"
	"os"
	"os/signal"
	"syscall"

	"github.com/Yamargo/weiniportifolio/internal/site"
)

func main() {
	if len(os.Args) < 2 {
		usage()
	}
	s, err := site.New()
	if err != nil {
		fatal(err)
	}
	switch os.Args[1] {
	case "serve":
		fs := flag.NewFlagSet("serve", flag.ExitOnError)
		addr := fs.String("addr", envOr("ADDR", ":8080"), "listen address")
		_ = fs.Parse(os.Args[2:])
		ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
		defer stop()
		if err := site.Serve(ctx, *addr, s.Handler()); err != nil {
			fatal(err)
		}
	case "build":
		fs := flag.NewFlagSet("build", flag.ExitOnError)
		out := fs.String("out", "docs", "output directory")
		_ = fs.Parse(os.Args[2:])
		if err := s.Build(*out); err != nil {
			fatal(err)
		}
	default:
		usage()
	}
}

func usage() {
	fmt.Fprintln(os.Stderr, "usage: portfolio serve [-addr :8080] | portfolio build [-out docs]")
	os.Exit(2)
}

func fatal(err error) {
	slog.Error("fatal", "err", err)
	os.Exit(1)
}

func envOr(k, def string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return def
}

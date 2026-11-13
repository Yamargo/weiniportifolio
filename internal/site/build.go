package site

import (
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
)

// Build writes a static copy of the site into out (for GitHub Pages and other
// static hosts): /index.html (auto-detecting), /{lang}/index.html and all assets.
func (s *Site) Build(out string) error {
	if err := os.RemoveAll(out); err != nil {
		return err
	}
	err := fs.WalkDir(Static(), ".", func(p string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		dst := filepath.Join(out, filepath.FromSlash(p))
		if d.IsDir() {
			return os.MkdirAll(dst, 0o755)
		}
		b, err := fs.ReadFile(Static(), p)
		if err != nil {
			return err
		}
		return os.WriteFile(dst, b, 0o644)
	})
	if err != nil {
		return err
	}
	// Default page: Portuguese, client-side language auto-detection stays on.
	b, err := s.Render(Languages[0].Code, "", false)
	if err != nil {
		return err
	}
	if err := os.WriteFile(filepath.Join(out, "index.html"), b, 0o644); err != nil {
		return err
	}
	for _, l := range Languages {
		b, err := s.Render(l.Code, "../", true)
		if err != nil {
			return err
		}
		dir := filepath.Join(out, l.Code)
		if err := os.MkdirAll(dir, 0o755); err != nil {
			return err
		}
		if err := os.WriteFile(filepath.Join(dir, "index.html"), b, 0o644); err != nil {
			return err
		}
	}
	// Pages must not run Jekyll over our files.
	if err := os.WriteFile(filepath.Join(out, ".nojekyll"), nil, 0o644); err != nil {
		return err
	}
	fmt.Println("built", out)
	return nil
}

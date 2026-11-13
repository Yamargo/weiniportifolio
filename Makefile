.PHONY: run test build docker
run:    ## serve on :8080
	go run ./cmd/portfolio serve
test:
	go vet ./... && go test ./...
build:  ## static copy for GitHub Pages (docs/)
	go run ./cmd/portfolio build -out docs
docker:
	docker build -t portfolio .

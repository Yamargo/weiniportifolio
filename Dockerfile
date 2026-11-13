FROM golang:1.24 AS build
WORKDIR /src
COPY go.mod ./
COPY . .
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /portfolio ./cmd/portfolio

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /portfolio /portfolio
EXPOSE 8080
ENTRYPOINT ["/portfolio", "serve"]

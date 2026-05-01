FROM rust:1.87-slim-bookworm AS builder

RUN apt-get update && apt-get install -y curl pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*

RUN rustup target add wasm32-unknown-unknown
RUN cargo install cargo-leptos --locked

WORKDIR /app

COPY Cargo.toml Cargo.lock ./
COPY src ./src
COPY input.css ./

RUN cargo leptos build --release

FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/target/server/release/ml-frontend ./ml-frontend
COPY --from=builder /app/target/site ./target/site

ENV LEPTOS_OUTPUT_NAME=ml-frontend
ENV LEPTOS_SITE_ROOT=target/site
ENV LEPTOS_SITE_ADDR=0.0.0.0:3000

EXPOSE 3000

CMD ["./ml-frontend"]

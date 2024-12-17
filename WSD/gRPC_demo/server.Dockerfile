FROM golang:1.23

RUN apt update
RUN apt install protobuf-compiler -y

ENV GOPATH=/go
ENV PATH=$PATH:$GOPATH/bin
WORKDIR /grpc_demo

RUN go mod init go-grpc-server
RUN go get google.golang.org/grpc
RUN go get google.golang.org/protobuf
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
RUN go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

COPY service.proto server.go ./
RUN protoc --go_out=. --go-grpc_out=. service.proto
RUN go build -o grpc_server .
EXPOSE 50051
CMD ["./grpc_server"]

#CMD ["tail", "-f", "/dev/null"]
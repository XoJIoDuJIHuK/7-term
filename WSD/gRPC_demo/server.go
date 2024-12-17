package main

import (
	"context"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"log"
	"net"
	"time"

	pb "go-grpc-server/generated"
	"google.golang.org/grpc"
)

type server struct {
	pb.UnimplementedGreeterServer
}

func (s *server) Add(ctx context.Context, req *pb.Parm2Request) (*pb.Parm2Result, error) {
	result := req.X + req.Y
	return &pb.Parm2Result{X: req.X, Y: req.Y, Z: result}, nil
}

func (s *server) Sub(ctx context.Context, req *pb.Parm2Request) (*pb.Parm2Result, error) {
	result := req.X - req.Y
	return &pb.Parm2Result{X: req.X, Y: req.Y, Z: result}, nil
}

func (s *server) Mul(ctx context.Context, req *pb.Parm2Request) (*pb.Parm2Result, error) {
	result := req.X * req.Y
	return &pb.Parm2Result{X: req.X, Y: req.Y, Z: result}, nil
}

func (s *server) Div(ctx context.Context, req *pb.Parm2Request) (*pb.Parm2Result, error) {
	if req.Y == 0 {
		return nil, status.Errorf(codes.InvalidArgument, "division by zero")
	}
	result := req.X / req.Y
	return &pb.Parm2Result{X: req.X, Y: req.Y, Z: result}, nil
}

func (s *server) Pow2(ctx context.Context, req *pb.Parm1Request) (*pb.Parm1Result, error) {
	result := req.X * req.X
	return &pb.Parm1Result{X: req.X, Z: result}, nil
}

func (s *server) ReallyHeavyFunction(ctx context.Context, req *pb.Parm2Request) (*pb.Parm1Result, error) {
	done := make(chan struct{})
	go func() {
		time.Sleep(time.Duration(req.X) * time.Second)
		close(done)
		log.Println("Function ended")
	}()
	select {
	case <-done:
		log.Println("Calculation is done")
		return &pb.Parm1Result{X: req.X, Z: 1337}, nil
	case <-ctx.Done():
		err := ctx.Err()
		log.Printf("Response will not be sent: %s", err)
		return nil, err
	}
}

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer()
	pb.RegisterGreeterServer(s, &server{})
	log.Println("Server is running on port :50051")
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}

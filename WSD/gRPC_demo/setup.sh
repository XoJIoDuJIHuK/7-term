go get google.golang.org/grpc
go get google.golang.org/protobuf
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

protoc --go_out=. --go-grpc_out=. service.proto

pip install grpcio grpcio-tools
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. --pyi_out=. service.proto

go run server.go

# реализация метода FromString на строчке 188 descriptor_pool.py неизвестным образом вычисляется в рантайме
# (отладчик внутрь AddSerializedFile в принципе не заходит)

# структуры запросов и ответов хранятся в словаре DESCRIPTOR.message_types_by_name
# по имени можно получить полное название, объекты полей (fields_by_name) и прочие данные
# DESCRIPTOR.message_types_by_name['Parm2Request'].fields_by_name['x'] эквивалентно
# тому, что снизу: все типы для c++ и grpc, название поля, тип поля, значение по умолчанию,
# порядковый номер и т.д.

# вызывать на строчке 43 builder.py в функции BuildMessageAndEnumDescriptors
# msg_des.fields_by_name['x']
# получится структура типа

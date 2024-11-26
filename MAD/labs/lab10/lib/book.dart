import 'package:hive/hive.dart';
import 'package:json_annotation/json_annotation.dart';

part 'book.g.dart';

@JsonSerializable()
@HiveType(typeId: 0) // Assign a unique type ID
class Book extends HiveObject {
  @HiveField(0)
  String id;

  @HiveField(1)
  String name;

  @HiveField(2)
  String description;

  @HiveField(3)
  double price;

  Book() :
    id = '1',
    name = 'xd',
    description = 'lmao',
    price = 0.0;

  Book.xd({
    required this.id,
    required this.name,
    required this.description,
    required this.price
  });

  factory Book.fromJson(Map<String,dynamic> json) => Book.xd(id: json['id'], name: json['name'], description: json['description'], price: json['price']);
  Map<String, dynamic> toJson() => {'id': id, 'name': name, 'description': description, 'price': price};
}

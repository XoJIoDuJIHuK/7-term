// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'book.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Book _$BookFromJson(Map<String, dynamic> json) => Book()
  ..id = (json['id'] as num).toInt()
  ..name = json['name'] as String
  ..description = json['description'] as String
  ..price = (json['price'] as num).toDouble()
  ..isFavourite = json['isFavourite'] as bool;

Map<String, dynamic> _$BookToJson(Book instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'price': instance.price,
      'isFavourite': instance.isFavourite,
    };

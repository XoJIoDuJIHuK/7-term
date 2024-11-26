import 'dart:io';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:cloud_firestore/cloud_firestore.dart';


Future<bool> isOnline() async {
  try {
    final result = await InternetAddress.lookup('example.com');
    if (result.isNotEmpty && result[0].rawAddress.isNotEmpty) {
      Hive.box('connectivity').put('isOnline', true);
      return true;
    }
    Hive.box('connectivity').put('isOnline', false);
    return false;
  } on SocketException catch (_) {
    Hive.box('connectivity').put('isOnline', false);
    return false;
  }
}

bool wasOnline() => Hive.box('connectivity').get('isOnline');

Future<List<Map<String, dynamic>>> getFavourites(String userId) async {
  FirebaseFirestore firestore = FirebaseFirestore.instance;
  QuerySnapshot snapshot = await firestore.collection('favourites').where('userId', isEqualTo: userId).get();
  List<Map<String, dynamic>> favourites = snapshot.docs.map(
    (doc) {
      final dict = doc.data() as Map<String, dynamic>;
      dict['id'] = doc.id;
      return dict;
    }
  ).toList();
  return favourites;
}

Future<Map<String, dynamic>?> getUser(String email) async {
  FirebaseFirestore firestore = FirebaseFirestore.instance;
  QuerySnapshot snapshot = await firestore.collection('users').where('email', isEqualTo: email).get();
  if (snapshot.docs.isEmpty) return null;
  final doc = snapshot.docs.first;
  final data = doc.data() as Map<String, dynamic>;
  data['id'] = doc.id;
  return data;
}

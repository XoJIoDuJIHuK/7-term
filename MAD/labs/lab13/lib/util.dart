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

Future<bool> userExists(String email) async {
  final snapshot = await FirebaseFirestore.instance.collection('users').where('email', isEqualTo: email).get();
  return (snapshot).docs.isNotEmpty;
}

Future<Map<String, dynamic>> authenticateUser(_auth, email, password) async {
  var user = null;
  if (await userExists(email)) {
    var signedUser = await _auth.signInWithEmailAndPassword(
      email: email,
      password: password,
    );
    var existingUser = await getUser(signedUser.user!.email!);
    var user = {
      'id': existingUser!['id'],
      'displayName': signedUser.user!.email,
      'email': signedUser.user!.email,
      'isAdmin': existingUser['isAdmin']
    };
  } else {
    final signedUser = await _auth.createUserWithEmailAndPassword(
      email: email,
      password: password,
    );
    var user = {
      'email': email,
      'name': email,
      'isAdmin': false
    };
    final addedUser = await FirebaseFirestore.instance.collection('users').add(user);
    user.remove('name');
    user['id'] = addedUser.id;
    user['displayName'] = email;
  }
  return user;
}
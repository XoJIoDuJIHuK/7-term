import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';

class UserNotifierModel extends ChangeNotifier {
  final Map<String, dynamic> _value = Map.from(Hive.box('users').get(0));

  Map<String, dynamic> get selectedUser => _value;

  void setSelectedUser(Map<String, dynamic> user) {
    // _value = user;
    _value.clear();
    _value.addAll(user);
    notifyListeners();
  }
}

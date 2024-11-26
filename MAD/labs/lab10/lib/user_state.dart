import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import './util.dart';

class UserNotifierModel extends ChangeNotifier {
  final Map<String, dynamic> _value = Map.from(Hive.box('users').get(0));

  Map<String, dynamic> get selectedUser => _value;

  void setSelectedUser(Map<String, dynamic> user) {
    _value.clear();
    _value.addAll(user);
    notifyListeners();
  }
}


class UserCubit extends Cubit<Map<String, dynamic>?> {
  UserCubit() : super(null);

  void set(Map<String, dynamic>? newUser) async {
    final box = Hive.box('favourites');
    box.clear();
    if (newUser != null) {
      final favourites = await getFavourites(newUser['id']);
      box.addAll(favourites);

      emit({
        'id': newUser['id'],
        'name': newUser['displayName'],
        'isAdmin': newUser['isAdmin'],
      });
    } else {
      emit(null);
    }
  }
}

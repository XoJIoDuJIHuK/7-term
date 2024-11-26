import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'auth.dart';
import 'firebase_options.dart';

import './home.dart';
import './schedule.dart';
import './book_edit.dart';
import './favourites.dart';
import './user_state.dart';


void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  FirebaseFirestore firestore = FirebaseFirestore.instance;

  Hive.init('./');
  await Hive.initFlutter();

  await Hive.openBox('connectivity');
  Hive.box('connectivity').put('isOnline', true);

  await Hive.openBox('users');
  var usersBox = Hive.box('users');
  await usersBox.clear();
  // usersBox.addAll([
  //   Map.from({ 'id': 1, 'name': 'User', 'isAdmin': false }),
  //   Map.from({ 'id': 2, 'name': 'Admin', 'isAdmin': true }),
  //   Map.from({ 'id': 3, 'name': 'User 2', 'isAdmin': false }),
  // ]);

  await Hive.openBox('favourites');
  var favouritesBox = Hive.box('favourites');
  await favouritesBox.clear();

  await Hive.openBox('books');
  var booksBox = Hive.box('books');
  await booksBox.clear();
  QuerySnapshot booksSnapshot = await firestore.collection('books').get();
  List<Map<String, dynamic>> booksData = booksSnapshot.docs.map((doc) {
    var data = doc.data() as Map<String, dynamic>;
    data['id'] = doc.id;
    return data;
  }).toList();
  booksBox.addAll(booksData);
  FirebaseMessaging.instance.onTokenRefresh
  .listen((fcmToken) {
    print('TOKEN REFRESH');
    print(fcmToken);
  })
  .onError((err) {
    print('TOKEN ERROR');
    print(err);
  });

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Input App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: BlocProvider(
        create: (_) => UserCubit(),
        child: const MainScreen(),
      ),
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  _MainScreenState createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;

  bool isAdmin(Map<String, dynamic>? user) {
    return user == null ? false : user['isAdmin'];
  }
  List<Map<String, dynamic>> getUsers() {
    var usersBox = Hive.box('users');
    var ret = List<Map<String, dynamic>>.from(usersBox.keys.map((k) => Map<String, dynamic>.from(usersBox.getAt(k))));
    return ret;
  }


  List<Widget> _screens(Map<String, dynamic>? user) {
    final base = [Home(), SchedulePage()];
    if (user == null) {
      base.add(AuthenticationPage());
    } else if (isAdmin(user)) {
      base.add(ManageBooksPage());
    } else {
      base.addAll([
        BookListPage(),
        FavouritesPage(userId: user['id'])
      ]);
    }
    return base;
  }

  List<BottomNavigationBarItem> _navigationButtons(Map<String, dynamic>? user) {
    final base = [
      const BottomNavigationBarItem(
        icon: Icon(Icons.home),
        label: 'Home',
      ),
      const BottomNavigationBarItem(
        icon: Icon(Icons.schedule),
        label: 'Schedule',
      )
    ];
    if (user == null) {
      base.add(const BottomNavigationBarItem(
        icon: Icon(Icons.login),
        label: 'Login',
      ));
    } else if (isAdmin(user)) {
      base.add(
        const BottomNavigationBarItem(
          icon: Icon(Icons.edit),
          label: 'Manage',
        )
      );
    } else {
      base.addAll([
        const BottomNavigationBarItem(
          icon: Icon(Icons.text_fields),
          label: 'Books',
        ),
        BottomNavigationBarItem(
          icon: const Icon(Icons.favorite),
          label: 'Favourites',
        )
      ]);
    }
    return base;
  }

  List<Widget> _actions(Map<String, dynamic>? user) {
    final users = getUsers();
    final usersItems = getUsers().map((option) {
      return DropdownMenuItem<String>(
        value: option['id'],
        child: Text(option['name']),
      );
    }).toList();
    final List<Widget> base = [];

    if (user != null) {
      base.add(ElevatedButton(onPressed: () async => context.read<UserCubit>().set(null), child: Text('Logout')));
    }

    base.add(
      DropdownButton<String>(
        value: user != null ? user['id'] : null,
        items: usersItems,
        onChanged: (String? newUserId) async {
          if (newUserId != null) {
            for (int i = 0; i < users.length; i++) {
                if (users[i]['id'] != newUserId) continue;
                context.read<UserCubit>().set(users[i]);
                break;
              }
            setState(() {});
          }
        },
      ),
    );

    return base;
  }

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<UserCubit, Map<String, dynamic>?>(
      builder: (context, user) => Scaffold(
        appBar: AppBar(
          title: const Text('Input App'),
          actions: _actions(user),
        ),
        body: _screens(user)[_selectedIndex],
        bottomNavigationBar: BottomNavigationBar(
          currentIndex: _selectedIndex,
          onTap: (int index) => setState(() {_selectedIndex = index;}),
          items: _navigationButtons(user)
        ),
      )
    );
  }
}
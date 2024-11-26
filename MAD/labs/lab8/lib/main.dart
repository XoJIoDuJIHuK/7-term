import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:provider/provider.dart';

import './home.dart';
import './schedule.dart';
import './book_edit.dart';
import './favourites.dart';
import './book.dart';
import './user_state.dart';


void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  Hive.init('./');
  await Hive.initFlutter();

  await Hive.openBox('users');
  var usersBox = Hive.box('users');
  await usersBox.clear();
  usersBox.addAll([
    Map.from({ 'id': 1, 'name': 'User', 'isAdmin': false }),
    Map.from({ 'id': 2, 'name': 'Admin', 'isAdmin': true }),
    Map.from({ 'id': 3, 'name': 'User 2', 'isAdmin': false }),
  ]);

  await Hive.openBox('favourites');
  var favouritesBox = Hive.box('favourites');
  await favouritesBox.clear();
  favouritesBox.addAll([
    Map.from({ 'id': 1, 'userId': 1, 'bookId': 3 }),
    Map.from({ 'id': 2, 'userId': 1, 'bookId': 2 }),
    Map.from({ 'id': 3, 'userId': 3, 'bookId': 1 }),
    Map.from({ 'id': 4, 'userId': 3, 'bookId': 4 }),
  ]);

  await Hive.openBox('books');
  var booksBox = Hive.box('books');
  await booksBox.clear();
  booksBox.addAll([
    Book.xd(id: 1, name: 'Большой Коран', description: 'Церемониальный', price: 13.37, isFavourite: false).toJson(),
    Book.xd(id: 2, name: 'Коран поменбше', description: 'Настольный', price: 9.99, isFavourite: false).toJson(),
    Book.xd(id: 3, name: 'Маленький Коран', description: 'Детский', price: 5.45, isFavourite: false).toJson(),
    Book.xd(id: 4, name: 'Вабще мелкий Коран жестб', description: 'Карманный', price: 4.23, isFavourite: false).toJson(),
    Book.xd(id: 5, name: 'Тора', description: 'Ага угу', price: 12.34, isFavourite: true).toJson(),
  ]);

  runApp(
    ChangeNotifierProvider(
      create: (context) => UserNotifierModel(),
      child: const MyApp(),
    ),
  );
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
      home: const MainScreen(),
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

  bool isAdmin(UserNotifierModel userModel) {
    return userModel.selectedUser['isAdmin'];
  }
  List<Map<String, dynamic>> getUsers() {
    var usersBox = Hive.box('users');
    var ret = List<Map<String, dynamic>>.from(usersBox.keys.map((k) => Map<String, dynamic>.from(usersBox.getAt(k))));
    return ret;
  }


  List<Widget> _screens(UserNotifierModel userModel) {
    return [
      const Home(),
      SchedulePage(
        // transfer_value: _inputValue
      ),
      isAdmin(userModel) ? const ManageBooksPage() : BookListPage(), // Conditional page
      isAdmin(userModel) ? Container() :  FavouritesPage(userId: userModel.selectedUser['id']), // Only for users
    ];
  }


  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    var users = getUsers();
    var usersItems = getUsers().map((option) {
      return DropdownMenuItem<int>(
        value: option['id'],
        child: Text(option['name']),
      );
    }).toList();
    return Consumer<UserNotifierModel>(builder: (context, userModel, child) {
        return Scaffold(
          appBar: AppBar(
            title: const Text('Input App'),
            actions: [
              DropdownButton<int>(
                value: userModel.selectedUser['id'],
                items: usersItems,
                onChanged: (int? newUserId) {
                  // TODO: remove
                  // setState(() {_selectedIndex = 0;});
                  if (newUserId != null) {
                    for (int i = 0; i < users.length; i++) {
                        if (users[i]['id'] != newUserId) continue;
                        userModel.setSelectedUser(users[i]);
                        break;
                      }
                    setState(() {});
                  }
                },
              ),
            ],
          ),
          body: _screens(userModel)[_selectedIndex],
          bottomNavigationBar: BottomNavigationBar(
            currentIndex: _selectedIndex,
            onTap: _onItemTapped,
            items:  <BottomNavigationBarItem>[
              const BottomNavigationBarItem(
                icon: Icon(Icons.input),
                label: 'Input',
              ),
              BottomNavigationBarItem(
                icon: const Icon(Icons.text_fields),
                label: isAdmin(userModel) ? 'Manage Books' : 'Books',
              ),
              const BottomNavigationBarItem(
                icon: Icon(Icons.details),
                label: 'Details', // Placeholder – actual book details will be shown
              ),
              const BottomNavigationBarItem(
                icon: Icon(Icons.favorite),
                label: 'Favourites',
              ),


            ].where((item) => !isAdmin(userModel) || item.label != 'Favourites').toList(), // Filter if admin
              // Dynamically show/hide Favourites based on user role
          ),
        );
      }
    );
  }
}
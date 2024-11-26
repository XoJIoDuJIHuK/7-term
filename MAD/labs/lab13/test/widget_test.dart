import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:bloc_test/bloc_test.dart';
import 'package:hive/hive.dart';
import 'package:lab10/auth.dart';
import 'package:lab10/book_edit.dart';
import 'package:lab10/user_state.dart';
import 'package:lab10/services/bookService.dart';
import 'package:mockito/mockito.dart';
import 'package:firebase_core_platform_interface/firebase_core_platform_interface.dart';

class MockAuth extends Mock implements FirebaseAuth {}
class MockUser extends Mock implements User {}
class MockUserCubit extends MockCubit<Map<String, dynamic>?> implements UserCubit {}
typedef Callback = void Function(MethodCall call);

void setupFirebaseAuthMocks([Callback? customHandlers]) {
  TestWidgetsFlutterBinding.ensureInitialized();
  setupFirebaseCoreMocks();
}

Future<T> neverEndingFuture<T>() async {
  // ignore: literal_only_boolean_expressions
  while (true) {
    await Future.delayed(const Duration(minutes: 5));
  }
}

class MockTask extends Mock {
  void call();
}


void main() {
  late MockUserCubit mockUserCubit;
  setupFirebaseAuthMocks();
  TestWidgetsFlutterBinding.ensureInitialized();
  setupFirebaseCoreMocks();

  setUpAll(() async {
    await Firebase.initializeApp();
  });

  setUp(() async {
    BookService.initLists();
    mockUserCubit = MockUserCubit();
    Hive.init('./');
    await Hive.openBox('books');
    Hive.box('books').clear();
    Hive.box('books').add({'id': '1', 'name': 'Koran', 'description': 'xd', 'price': 12.34});
  });

  setUpAll(() async {
    await BookService.initLists();
    await Firebase.initializeApp();
  });

  group('Edit book tests', () {
    testWidgets('WIDGET: Edit book', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: BlocProvider<UserCubit>(
            create: (context) => mockUserCubit,
            child: ManageBooksPage(),
          ),
        ),
      );
      final editButton = find.byType(IconButton).first;
      final editWindow = find.byType(AlertDialog);

      expect(editButton, findsOneWidget);
      await tester.drag(editButton, Offset.zero);
      await tester.tap(editButton);
      await tester.pumpAndSettle();

      expect(editWindow, findsOneWidget);

      print('Test: should save form data and attempt sign up (successful) - Passed');
    });
  });

  group('Login, SignUp Screen Tests', () {
    testWidgets('WIDGET: LoginScreen form validation - incorrect password', (WidgetTester tester) async {

      await tester.pumpWidget(
        MaterialApp(
          home: BlocProvider<UserCubit>(
            create: (context) => mockUserCubit,
            child: AuthenticationPage(),
          ),
        ),
      );

      final emailField = find.byType(TextField).first;
      final passwordField = find.byType(TextField).at(1);

      await tester.enterText(emailField, 'incorrect_email');
      await tester.enterText(passwordField, '123');
      final loginButton = find.byType(ElevatedButton).first;

      await tester.tap(loginButton);
      await tester.pump();

      expect(find.text('Password must be at least 6 characters'), findsOneWidget);

      print('Test: LoginScreen form validation - incorrect password - Passed');
    });

    testWidgets('WIDGET: LoginScreen form validation - incorrect email', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: BlocProvider<UserCubit>(
            create: (context) => mockUserCubit,
            child: AuthenticationPage(),
          ),
        ),
      );

      final emailField = find.byType(TextField).first;
      final passwordField = find.byType(TextField).at(1);

      await tester.enterText(emailField, 'xd');
      await tester.enterText(passwordField, '123456');
      final loginButton = find.byType(ElevatedButton).first;

      await tester.tap(loginButton);
      await tester.pump();


      expect(find.text('Invalid email'), findsOneWidget);

      print('Test: LoginScreen form validation - incorrect email - Passed');
    });

    testWidgets('WIDGET: Login screen login with empty email', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: BlocProvider<UserCubit>(
            create: (context) => mockUserCubit,
            child: AuthenticationPage(),
          ),
        ),
      );

      final loginButton = find.byType(ElevatedButton).first;

      await tester.tap(loginButton);
      await tester.pumpAndSettle();


      expect(find.text('Enter email'), findsOneWidget);

      print('Login screen login with empty email - Passed');
    });

    testWidgets('WIDGET: Login screen password recovery', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: BlocProvider<UserCubit>(
            create: (context) => mockUserCubit,
            child: AuthenticationPage(),
          ),
        ),
      );

      final passwordResetButton = find.byType(ElevatedButton).at(2);

      await tester.tap(passwordResetButton);
      await tester.pumpAndSettle();


      expect(find.text('Enter email'), findsOneWidget);

      print('Login screen password recovery - Passed');
    });
  });

  group('BookService Tests', () {
    test('UNIT: addbook should add a book to the list', () {
      final book = {'id': '1', 'name': 'Koran', 'description': 'xd', 'price': 12.34};

      BookService.addBook(book);

      expect(BookService.getAllBooks().length, 1);
      expect(BookService.getAllBooks().first['id'], '1');
      expect(BookService.getAllBooks().first['name'], 'Koran');
      expect(BookService.getAllBooks().first['price'], 12.34);

      print('Test: addbook should add a book to the list - Passed');
    });

    test('UNIT: getbookById should return the correct book', () {
      // Arrange
      final book1 = {'id': '1', 'name': 'Koran', 'description': 'xd', 'price': 12.34};
      final book2 = {'id': '2', 'name': 'Small koran', 'description': 'xd', 'price': 10.34};
      BookService.addBook(book1);
      BookService.addBook(book2);

      // Act
      final result = BookService.getBookById('1');

      // Assert
      expect(result?['id'], '1');
      expect(result?['name'], 'Koran');
      expect(result?['price'], 12.34);

      print('Test: getBookById should return the correct book - Passed');
    });

    test('UNIT: updatebookById should update the book details', () {
      // Arrange
      final book = {'id': '1', 'name': 'Koran', 'description': 'xd', 'price': 12.34};
      BookService.addBook(book);
      final updatedbook = {'id': '1', 'name': 'Koran v2.0', 'description': 'xd', 'price': 12.3};

      // Act
      BookService.updateBookById('1', updatedbook);

      // Assert
      final result = BookService.getBookById('1');
      expect(result?['name'], 'Koran v2.0');
      expect(result?['price'], 12.3);

      print('Test: updateBookById should update the book details - Passed');
    });

    test('UNIT: updatebookById should print an error if book not found', () {
      // Arrange
      final updatedbook = {'id': '1', 'name': 'Koran', 'description': 'xd', 'price': 12.34};

      // Act & Assert
      expect(
        () => BookService.updateBookById('999', updatedbook),
        prints('Error: book with id 999 not found.\n')
      );

      print('Test: updateBookById should print an error if book not found - Passed');
    });

    test('UNIT: deletebookById should delete the book', () {
      // Arrange
      final book = {'id': '1', 'name': 'Koran', 'description': 'xd', 'price': 12.34};
      BookService.addBook(book);

      // Act
      BookService.deleteBookById('1');

      // Assert
      expect(BookService.getAllBooks().isEmpty, true);

      print('Test: deleteBookById should delete the book - Passed');
    });
  });
}

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:lab10/util.dart';
import './user_state.dart';
import 'book.dart';
import 'book_details.dart';


class BookListPage extends StatefulWidget {
  const BookListPage({super.key});

  @override
  _BookListPageState createState() => _BookListPageState();
}


class _BookListPageState extends State<BookListPage> {
  bool isFavourite(String bookId, String userId) {
    for (int i = 0; i < Hive.box('favourites').length; i++) {
      var el = Hive.box('favourites').getAt(i);
      if (el['bookId'] == bookId && el['userId'] == userId) {
        return true;
      }
    }
    return false;
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Books')),
      body: ValueListenableBuilder(
        valueListenable: Hive.box('books').listenable(),
        builder: (context, booksBox, _) {
          return ListView.builder(
            itemCount: booksBox.length,
            itemBuilder: (context, index) {
              final element = booksBox.getAt(index)!;
              final book = Book.xd(id: element['id'], name: element['name'], description: element['description'], price: element['price']);
              return ListTile(
                title: Text(book.name),
                subtitle: Text(book.description),
                trailing: BlocBuilder<UserCubit, Map<String, dynamic>?>(builder: (context, user) => IconButton(
                  icon: Icon(isFavourite(book.id, user!['id']) ? Icons.favorite : Icons.favorite_border),
                  onPressed: () {
                    _toggleFavourite(book, index, user['id']);
                  },
                )),
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => BookDetailsPage(book: book),
                    ),
                  );
                },
              );
            }
          );
        },
      )
    );
  }

  void _toggleFavourite(Book book, int index, String userId) async {
    final favouritesBox = Hive.box('favourites');
    FirebaseFirestore firestore = FirebaseFirestore.instance;
    final collection = firestore.collection('favourites');
    final deviceWasOnline = wasOnline();
    final deviceIsOnline = await isOnline();
    if (deviceIsOnline && !deviceWasOnline) {
      final box = Hive.box('favourites');
      box.clear();
      box.addAll(await getFavourites(userId));
    }

    if (isFavourite(book.id, userId)) {
      for (int i = 0; i < favouritesBox.length; i++) {
        var el = favouritesBox.getAt(i);
        if (el['userId'] == userId && el['bookId'] == book.id) {
          favouritesBox.deleteAt(i);
          if (deviceIsOnline) {
            DocumentReference documentReference = collection.doc(el['id']);
            await documentReference.delete();
          }
          break;
        }
      }
    } else {
      var el;
      if (deviceIsOnline) {
        el = await collection.add({
          'userId': userId,
          'bookId': book.id,
        });
      }
      favouritesBox.add({
        'id': el == null ? '1' : el.id,
        'userId': userId,
        'bookId': book.id,
      });
    }

    setState(() {}); // Rebuild to update icon
  }
}



class ManageBooksPage extends StatefulWidget {
  const ManageBooksPage({super.key});

  @override
  _ManageBooksPageState createState() => _ManageBooksPageState();
}


class _ManageBooksPageState extends State<ManageBooksPage> {
  final booksCollection = FirebaseFirestore.instance.collection('books');
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _priceController = TextEditingController();

  void _createOrUpdateBook([Box? booksBox, Book? book, int? index]) async {
    final deviceWasOnline = Hive.box('connectivity').get('isOnline');
    final deviceIsOnline = await isOnline();
    booksBox ??= Hive.box('books');
    if (deviceIsOnline && !deviceWasOnline) {
      booksBox.clear();
      booksBox.addAll((await booksCollection.get()).docs.map((doc) {
        var data = doc.data();
        data['id'] = doc.id;
        return data;
      }));
    }

    if (_formKey.currentState!.validate()) {
      final newBook = {
        'name': _nameController.text,
        'description': _descriptionController.text,
        'price': double.parse(_priceController.text),
      };
      if (book == null || index == null) {
        if (deviceIsOnline) {
          final addedBook = await booksCollection.add(newBook);
          newBook['id'] = addedBook.id;
        } else {
          newBook['id'] = DateTime.now().millisecondsSinceEpoch.toString();
        }
        booksBox.add(newBook);
      } else {
        book.name = _nameController.text;
        book.description = _descriptionController.text;
        book.price = double.parse(_priceController.text);
        if (deviceIsOnline) await booksCollection.doc(book.id).update(book.toJson());
        booksBox.put(index, book.toJson());

      }
      Navigator.of(context).pop(); // Close the dialog
      setState(() {});
    }
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Manage Books')),
      body: ValueListenableBuilder(
          valueListenable: Hive.box('books').listenable(),
          builder: (context, Box booksBox, _) {
            return ListView.builder(
              itemCount: booksBox.length,
              itemBuilder: (context, index) {
                final element = booksBox.getAt(index)!;
                final book = Book.xd(id: element['id'], name: element['name'], description: element['description'], price: element['price']);
                return ListTile(
                  title: Text(book.name),
                  subtitle: Text(book.description),
                  trailing: Row( // Add edit and delete buttons
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.edit),
                        onPressed: () {
                           _nameController.text = book.name;
                            _descriptionController.text = book.description;
                            _priceController.text = book.price.toString();

                           showDialog(
                              context: context,
                              builder: (context) => AlertDialog(
                                title: const Text('Edit Book'),
                                content: Form( // Wrap with Form
                                  key: _formKey,  // Assign the form key
                                  child: Column(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      TextFormField(
                                        controller: _nameController,
                                        decoration: const InputDecoration(labelText: 'Name'),
                                        validator: (value) => value == null || value.isEmpty ? 'Please enter a name' : null,
                                      ),
                                      TextFormField(
                                        controller: _descriptionController,
                                        decoration: const InputDecoration(labelText: 'Description'),
                                        validator: (value) => value == null || value.isEmpty ? 'Please enter a description' : null,

                                      ),
                                      TextFormField(
                                        controller: _priceController,
                                        decoration: const InputDecoration(labelText: 'Price'),
                                        keyboardType: TextInputType.number,
                                        validator: (value) => value == null || value.isEmpty ? 'Please enter a price' : null,
                                      ),
                                    ],
                                  ),
                                ),
                                actions: [
                                  TextButton(
                                    onPressed: () => Navigator.of(context).pop(),
                                    child: const Text('Cancel'),
                                  ),
                                  TextButton(
                                    onPressed: () => _createOrUpdateBook(booksBox, book, index), // Pass the book to update
                                    child: const Text('Save'),
                                  ),
                                ],
                              )


                          );
                        },
                      ),
                      IconButton(
                        icon: const Icon(Icons.delete),
                        onPressed: () async {
                          Hive.box('books').deleteAt(index);
                          if (await isOnline()) {
                            await booksCollection.doc(book.id).delete();
                          }
                          if (mounted) {
                            setState(() {});
                          }
                        },
                      ),
                    ],
                  ),

                );
              },
            );
          }

      ),
      floatingActionButton: FloatingActionButton( // Add book button
        onPressed: () {
         _nameController.clear();
          _descriptionController.clear();
          _priceController.clear();
          showDialog(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text('Add Book'),
              content: Form( // Wrap with Form
                key: _formKey,  // Assign the form key
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    TextFormField(
                      controller: _nameController,
                      decoration: const InputDecoration(labelText: 'Name'),
                      validator: (value) => value == null || value.isEmpty ? 'Please enter a name' : null,

                    ),
                    TextFormField(
                      controller: _descriptionController,
                      decoration: const InputDecoration(labelText: 'Description'),
                      validator: (value) => value == null || value.isEmpty ? 'Please enter a description' : null,

                    ),
                    TextFormField(
                      controller: _priceController,
                      decoration: const InputDecoration(labelText: 'Price'),
                      keyboardType: TextInputType.number,
                      validator: (value) => value == null || value.isEmpty ? 'Please enter a price' : null,
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Cancel'),
                ),
                TextButton(
                  onPressed: _createOrUpdateBook,
                  child: const Text('Add'),
                ),
              ],
            ),
          );
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}
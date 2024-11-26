import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';
import './user_state.dart';
import 'package:provider/provider.dart';
import 'book.dart';
import 'book_details.dart';


class BookListPage extends StatefulWidget {
  const BookListPage({super.key});

  @override
  _BookListPageState createState() => _BookListPageState();
}


class _BookListPageState extends State<BookListPage> {
  bool isFavourite(int bookId, int userId) {
    print("bookId = $bookId; userId = $userId");
    for (int i = 0; i < Hive.box('favourites').length; i++) {
      var el = Hive.box('favourites').getAt(i);
      if (el['bookId'] == bookId && el['userId'] == userId) {
        print('true');
        return true;
      }
    }
    print('false');
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
              final book = Book.xd(id: element['id'], name: element['name'], description: element['description'], price: element['price'], isFavourite: element['isFavourite']);
              return Consumer<UserNotifierModel>(builder: (context, userModel, child) {
                return ListTile(
                    title: Text(book.name),
                    subtitle: Text(book.description),
                    trailing: IconButton(
                      icon: Icon(isFavourite(book.id, userModel.selectedUser['id']) ? Icons.favorite : Icons.favorite_border), // Or Icons.favorite if already favourited
                      onPressed: () {
                        _toggleFavourite(book, index, userModel.selectedUser['id']); // Implement favourite logic
                      },
                    ),
                    onTap: () {
                      // Navigate to details page
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
          );
        }
      )
    );
  }

  void _toggleFavourite(Book book, int index, int userId) {
    final favouritesBox = Hive.box('favourites');
    int maxFavouritesId = 0;
    for (int i = 0; i < favouritesBox.length; i++) {
      if (favouritesBox.getAt(i)['id'] > maxFavouritesId) {
        maxFavouritesId = favouritesBox.getAt(i)['id'] + 1;
      }
    }

    if (isFavourite(book.id, userId)) {
      for (int i = 0; i < favouritesBox.length; i++) {
        var el = favouritesBox.getAt(i);
        if (el['userId'] == userId && el['bookId'] == book.id) {
          favouritesBox.deleteAt(i);
          break;
        }
      }
    } else {
      favouritesBox.add({
        'id': maxFavouritesId,
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
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _priceController = TextEditingController();

  void _createOrUpdateBook([Box? booksBox, Book? book, int? index]) async {  // Optional book for editing
    booksBox ??= Hive.box('books');

    if (_formKey.currentState!.validate()) {
      final newBook = Book.xd(
        id: book?.id ?? booksBox.length + 1, // Assign new ID or keep existing
        name: _nameController.text,
        description: _descriptionController.text,
        price: double.parse(_priceController.text),
        isFavourite: book?.isFavourite ?? false,
      );
      if (book == null || index == null) { // Create
        booksBox.add(newBook.toJson());
      } else { // Update
        // await booksBox.delete(index);

        book.name = _nameController.text;
        book.description = _descriptionController.text;
        book.price = double.parse(_priceController.text);
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
                final book = Book.xd(id: element['id'], name: element['name'], description: element['description'], price: element['price'], isFavourite: element['isFavourite']);
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
                        onPressed: () {
                          // Delete the book from Hive
                          Hive.box('books').deleteAt(index);

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
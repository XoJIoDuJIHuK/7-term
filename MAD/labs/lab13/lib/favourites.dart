import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'book.dart';
import './book_details.dart';



class FavouritesPage extends StatefulWidget {
  final String userId;

  const FavouritesPage({super.key, required this.userId});

  @override
  _FavouritesPageState createState() => _FavouritesPageState(userId: userId);
}


class _FavouritesPageState extends State<FavouritesPage> {
  final String userId;

  _FavouritesPageState({required this.userId});

  Map getBook(String id) {
    for (int i = 0; i < Hive.box('books').length; i++) {
      var el = Hive.box('books').getAt(i);
      if (el['id'] == id) {
        return el;
      }
    }
    return {};
  }

  @override
  Widget build(BuildContext context) {
    var booksBox = Hive.box('books');
    var favouriteBox = Hive.box('favourites');

    return Scaffold(
      appBar: AppBar(title: const Text('Favourites')),
      body: ValueListenableBuilder(

        valueListenable: booksBox.listenable(),
        builder: (context, Box booksBox, _) {
          final favouriteBooks = favouriteBox.values
              .where(
                (e) => e['userId'] == userId,
              )
              .map((e) => getBook(e['bookId']))
              .toList();
          
          return ListView.builder(
            itemCount: favouriteBooks.length,
            itemBuilder: (context, index) {
              final e = favouriteBooks[index];
              final book = Book.xd(id: e['id'], name: e['name'], description: e['description'], price: e['price']);
              return ListTile(
                title: Text(book.name),
                subtitle: Text(book.description),
                trailing: IconButton(
                  icon: const Icon(Icons.favorite), // Remove from favourites icon
                  onPressed: () async {
                    for (int i = 0; i < favouriteBox.length; i++) {
                      var el = favouriteBox.getAt(i);
                      if (el['userId'] == userId && el['bookId'] == book.id) {
                        await favouriteBox.deleteAt(i);
                        // book.isFavourite = false;
                        // await booksBox.put(i, book.toJson());
                        break;
                      }
                    }
                    setState(() {});
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
            },
          );
        },
      ),
    );
  }
}
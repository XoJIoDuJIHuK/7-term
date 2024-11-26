import 'package:flutter/material.dart';
import 'book.dart'; // Import your Book model

class BookDetailsPage extends StatelessWidget {
  final Book book;

  const BookDetailsPage({super.key, required this.book});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(book.name),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Description: ${book.description}'),
            Text('Price: \$${book.price.toStringAsFixed(2)}'),
          ],
        ),
      ),
    );
  }
}
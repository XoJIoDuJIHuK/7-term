class BookService {
  static final List<Map<String, dynamic>> _bookList = [];

  static Future<void> initLists() async {
    print("ListService initialized.");
    _bookList.clear();
  }

  static void addBook(Map<String, dynamic> book) {
    _bookList.add(book);
  }

  static List<Map<String, dynamic>> getAllBooks() {
    return List.unmodifiable(_bookList);
  }

  static void updateBookById(String id, Map<String, dynamic> updatedBook) {
    final index = _bookList.indexWhere((book) => book['id'] == id);
    if (index != -1) {
      _bookList[index] = updatedBook;
      print('Book with id $id has been updated.');
    } else {
      print('Error: book with id $id not found.');
    }
  }

  static Map<String, dynamic>? getBookById(String bookId) {
    return _bookList.firstWhere(
      (book) => book['id'] == bookId
    );
  }

  static void deleteBookById(String id) {
    final index = _bookList.indexWhere((book) => book['id'] == id);
    if (index != -1) {
      _bookList.removeAt(index);
      print('Boo with id $id has been deleted.');
    } else {
      print('Error: book with id $id not found.');
    }
  }
}

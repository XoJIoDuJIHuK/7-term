// lib/database_helper.dart
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:logging/logging.dart';

final _log = Logger('MyApp');

class DatabaseHelper {
  static final DatabaseHelper _instance = DatabaseHelper._internal();
  factory DatabaseHelper() => _instance;
  static Database? _database;

  DatabaseHelper._internal();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'workers.db');
    _log.info("DB path: $path");

    return await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE workers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            hoursWorked INTEGER
          )
        ''');
      },
    );
  }

  Future<int> insertWorker(Map<String, dynamic> worker) async {
    final db = await database;
    _log.info('Inserting worker');
    _log.info(worker);
    return await db.insert('workers', worker);
  }

  Future<List<Map<String, dynamic>>> getWorkers() async {
    final db = await database;
    final workers = await db.query('workers');
    _log.info('Fetching workers');
    _log.info(workers);
    return workers;
  }

  Future<int> updateWorker(Map<String, dynamic> worker) async {
    final db = await database;
    _log.info('Updating worker');
    _log.info(worker);
    return await db.update(
      'workers',
      worker,
      where: 'id = ?',
      whereArgs: [worker['id']],
    );
  }

  Future<int> deleteWorker(int id) async {
    final db = await database;
    _log.info('Deleting worker');
    _log.info(id);
    return await db.delete(
      'workers',
      where: 'id = ?',
      whereArgs: [id],
    );
  }
}

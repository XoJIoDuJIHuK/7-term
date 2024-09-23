import 'dart:async';
import 'dart:js_interop';

abstract class Workable {
  String performWork();
}

abstract class Worker implements Workable {
  String name;
  int hoursWorked;

  Worker(this.name, this.hoursWorked);

  String get workerName => name;
  void set workerName(newName) => name = newName;

  Worker.namedConstructor()
      : name = "Lexa",
        hoursWorked = 1;

  /// Optional positional param with default value
  void logWork([String logMessage = "Work logged"]) {
    print('$name: $logMessage');
  }

  /// Named param
  void completeTask({required String task}) {
    print('$name completed task: $task');
  }

  /// Function param
  void processTask(Function taskProcessor) {
    taskProcessor();
  }

  static int totalWorkers = 0;

  static void incrementWorkerCount() {
    totalWorkers++;
  }

  /// JSON Serialization
  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'hoursWorked': hoursWorked,
    };
  }

  static Worker fromJson(Map<String, dynamic> json, WorkerFactory factory) {
    return factory.createWorker(
      json['name'] as String,
      json['hoursWorked'] as int,
    );
  }
}

/// Mixins
mixin LoggerMixin on Worker {
  void logInfo(String message) {
    print('[INFO] $name: $message');
  }
}

mixin TaskProcessorMixin on Worker {
  void processWithLogging(Function taskProcessor) {
    print('Processing task...');
    processTask(taskProcessor);
    print('Task processing completed.');
  }
}

class Engineer extends Worker with LoggerMixin, TaskProcessorMixin
    implements Comparable<Engineer> {
  Engineer(super.name, super.hoursWorked) {
    Worker.incrementWorkerCount();
  }

  @override
  String performWork() {
    return '$name is drinking coffee...';
  }

  @override
  int compareTo(Engineer other) {
    return name.compareTo(other.name);
  }

  // Асинхронный метод
  Future<void> performAsyncWork() async {
    await Future.delayed(const Duration(seconds: 2), () {
      print('$name completed async work.');
    });
  }
}

class Manager extends Worker with LoggerMixin, TaskProcessorMixin
    implements Comparable<Manager> {
  Manager(super.name, super.hoursWorked) {
    Worker.incrementWorkerCount();
  }

  @override
  String performWork() {
    return '$name is doing nothing...';
  }

  @override
  int compareTo(Manager other) {
    return name.compareTo(other.name);
  }
}

class Technician extends Worker with LoggerMixin, TaskProcessorMixin
    implements Comparable<Technician> {
  Technician(super.name, super.hoursWorked) {
    Worker.incrementWorkerCount();
  }

  @override
  String performWork() {
    return '$name is reinstalling Windows...';
  }

  @override
  int compareTo(Technician other) {
    return name.compareTo(other.name);
  }
}

// Iterable and Iterator
class WorkerIterable implements Iterable<Worker> {
  final List<Worker> _workers;

  WorkerIterable(this._workers);

  @override
  Iterator<Worker> get iterator => WorkerIterator(_workers);

  @override
  bool any(bool Function(Worker element) test) {
    // TODO: implement any
    throw UnimplementedError();
  }

  @override
  Iterable<R> cast<R>() {
    // TODO: implement cast
    throw UnimplementedError();
  }

  @override
  bool contains(Object? element) {
    // TODO: implement contains
    throw UnimplementedError();
  }

  @override
  Worker elementAt(int index) {
    // TODO: implement elementAt
    throw UnimplementedError();
  }

  @override
  bool every(bool Function(Worker element) test) {
    // TODO: implement every
    throw UnimplementedError();
  }

  @override
  Iterable<T> expand<T>(Iterable<T> Function(Worker element) toElements) {
    // TODO: implement expand
    throw UnimplementedError();
  }

  @override
  // TODO: implement first
  Worker get first => throw UnimplementedError();

  @override
  Worker firstWhere(bool Function(Worker element) test, {Worker Function()? orElse}) {
    // TODO: implement firstWhere
    throw UnimplementedError();
  }

  @override
  T fold<T>(T initialValue, T Function(T previousValue, Worker element) combine) {
    // TODO: implement fold
    throw UnimplementedError();
  }

  @override
  Iterable<Worker> followedBy(Iterable<Worker> other) {
    // TODO: implement followedBy
    throw UnimplementedError();
  }

  @override
  void forEach(void Function(Worker element) action) {
    // TODO: implement forEach
  }

  @override
  // TODO: implement isEmpty
  bool get isEmpty => throw UnimplementedError();

  @override
  // TODO: implement isNotEmpty
  bool get isNotEmpty => throw UnimplementedError();

  @override
  String join([String separator = ""]) {
    // TODO: implement join
    throw UnimplementedError();
  }

  @override
  // TODO: implement last
  Worker get last => throw UnimplementedError();

  @override
  Worker lastWhere(bool Function(Worker element) test, {Worker Function()? orElse}) {
    // TODO: implement lastWhere
    throw UnimplementedError();
  }

  @override
  // TODO: implement length
  int get length => throw UnimplementedError();

  @override
  Iterable<T> map<T>(T Function(Worker e) toElement) {
    // TODO: implement map
    throw UnimplementedError();
  }

  @override
  Worker reduce(Worker Function(Worker value, Worker element) combine) {
    // TODO: implement reduce
    throw UnimplementedError();
  }

  @override
  // TODO: implement single
  Worker get single => throw UnimplementedError();

  @override
  Worker singleWhere(bool Function(Worker element) test, {Worker Function()? orElse}) {
    // TODO: implement singleWhere
    throw UnimplementedError();
  }

  @override
  Iterable<Worker> skip(int count) {
    // TODO: implement skip
    throw UnimplementedError();
  }

  @override
  Iterable<Worker> skipWhile(bool Function(Worker value) test) {
    // TODO: implement skipWhile
    throw UnimplementedError();
  }

  @override
  Iterable<Worker> take(int count) {
    // TODO: implement take
    throw UnimplementedError();
  }

  @override
  Iterable<Worker> takeWhile(bool Function(Worker value) test) {
    // TODO: implement takeWhile
    throw UnimplementedError();
  }

  @override
  List<Worker> toList({bool growable = true}) {
    // TODO: implement toList
    throw UnimplementedError();
  }

  @override
  Set<Worker> toSet() {
    // TODO: implement toSet
    throw UnimplementedError();
  }

  @override
  Iterable<Worker> where(bool Function(Worker element) test) {
    // TODO: implement where
    throw UnimplementedError();
  }

  @override
  Iterable<T> whereType<T>() {
    // TODO: implement whereType
    throw UnimplementedError();
  }
}

class WorkerIterator implements Iterator<Worker> {
  final List<Worker> _workers;
  int _currentIndex = -1;

  WorkerIterator(this._workers);

  @override
  Worker get current {
    if (_currentIndex >= 0 && _currentIndex < _workers.length) {
      return _workers[_currentIndex];
    } else {
      throw Exception('Current is null');
    }
  }

  @override
  bool moveNext() {
    if (_currentIndex < _workers.length - 1) {
      _currentIndex++;
      return true;
    }
    return false;
  }
}


abstract class WorkerFactory {
  WorkerFactory();
  Worker createWorker(String name, int hoursWorked);
}

class EngineerFactory extends WorkerFactory {
  @override
  Worker createWorker(String name, int hoursWorked) {
    return Engineer(name, hoursWorked);
  }
}

class ManagerFactory extends WorkerFactory {
  @override
  Worker createWorker(String name, int hoursWorked) {
    return Manager(name, hoursWorked);
  }
}

class TechnicianFactory extends WorkerFactory {
  @override
  Worker createWorker(String name, int hoursWorked) {
    return Technician(name, hoursWorked);
  }
}

// Single Subscription Stream
Stream<Worker> createSingleSubscriptionStream(List<Worker> workers) async* {
  for (var worker in workers) {
    yield worker;
    await Future.delayed(const Duration(seconds: 1));
  }
}

// Broadcast Stream
Stream<Worker> createBroadcastStream(List<Worker> workers) {
  final controller = StreamController<Worker>.broadcast();

  Future(() async {
    for (var worker in workers) {
      controller.add(worker);
      await Future.delayed(const Duration(seconds: 1));
    }
    controller.close();
  });

  return controller.stream;
}

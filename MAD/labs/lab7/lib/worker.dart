// lib/worker.dart
class Worker {
  final int? id;
  final String name;
  final int hoursWorked;

  Worker({
    this.id,
    required this.name,
    required this.hoursWorked
  });

  // Convert a Worker object to a Map
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'hoursWorked': hoursWorked,
    };
  }

  // Create a Worker from a Map
  factory Worker.fromMap(Map<String, dynamic> map) {
    return Worker(
      id: map['id'] as int,
      name: map['name'] as String,
      hoursWorked: map['hoursWorked'] as int,
    );
  }
}

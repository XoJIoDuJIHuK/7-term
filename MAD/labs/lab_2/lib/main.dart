import 'package:flutter/material.dart';
import 'worker.dart';

WorkerFactory engineerFactory = EngineerFactory();
WorkerFactory managerFactory = ManagerFactory();
WorkerFactory technicianFactory = TechnicianFactory();

List<Worker> workers = [
  engineerFactory.createWorker('Alice', 40),
  managerFactory.createWorker('Bob', 35),
  technicianFactory.createWorker('Charlie', 30),
];

final singleStreamShowcase = Expanded(
  child: StreamBuilder<Worker>(
    stream: createSingleSubscriptionStream(workers),
    builder: (context, snapshot) {
      if (snapshot.connectionState == ConnectionState.waiting) {
        return const Center(child: CircularProgressIndicator());
      } else if (snapshot.hasError) {
        return Center(child: Text('Error: ${snapshot.error}'));
      } else if (!snapshot.hasData) {
        return const Center(child: Text('No data available'));
      } else {
        var worker = snapshot.data!;
        return ListView(
          children: [
            ListTile(
              title: Text(worker.name),
              subtitle: Text('Hours Worked: ${worker.hoursWorked}'),
            ),
          ],
        );
      }
    },
  ),
);
final broadcastStreamShowcase = Expanded(
  child: StreamBuilder<Worker>(
    stream: createBroadcastStream(workers),
    builder: (context, snapshot) {
      if (snapshot.connectionState == ConnectionState.waiting) {
        return const Center(child: CircularProgressIndicator());
      } else if (snapshot.hasError) {
        return Center(child: Text('Error: ${snapshot.error}'));
      } else if (!snapshot.hasData) {
        return const Center(child: Text('No data available'));
      } else {
        var worker = snapshot.data!;
        return ListView(
          children: [
            ListTile(
              title: Text(worker.name),
              subtitle: Text('Hours Worked: ${worker.hoursWorked}'),
            ),
          ],
        );
      }
    },
  ),
);

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: WorkerListScreen(
        workers: workers,
        singleStreamShowcase: singleStreamShowcase,
        broadcastStreamShowcase: broadcastStreamShowcase,
      ),
    );
  }
}

class WorkerListScreen extends StatelessWidget {
  final List<Worker> workers;
  final Expanded singleStreamShowcase;
  final Expanded broadcastStreamShowcase;

  WorkerListScreen({
    super.key,
    required this.workers,
    required this.singleStreamShowcase,
    required this.broadcastStreamShowcase
  });


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Workers List'),
      ),
      body: Column(
        children: [
          Expanded(
              child: ListView.builder(
                itemCount: workers.length,
                itemBuilder: (context, index) {
                  var worker = workers[index];
                  return ListTile(
                    title: Text(worker.name),
                    subtitle: Text('Hours Worked: ${worker.hoursWorked}'),
                    onTap: () async {
                      String workResult = worker.performWork();
                      worker.completeTask(task: 'Task A');
                      worker.processTask(
                              () => print('${worker.name} is processing a task.'));

                      // Demonstrating async method
                      if (worker is Engineer) {
                        await (worker).performAsyncWork();
                      } else if (worker is Manager) {
                        worker.processWithLogging(
                                () => print('Just manager processing task')
                        );
                      } else if (worker is Technician) {
                        worker.logInfo('Lmao');
                      }

                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(workResult),
                        ),
                      );
                    },
                  );
                },
              ),
          ),
          const Divider(),
          const Text('Single Subscription Stream', style: TextStyle(
              fontSize: 18, fontWeight: FontWeight.bold)
          ),
          singleStreamShowcase,
          singleStreamShowcase,
          const Divider(),
          const Text('Broadcast Stream', style: TextStyle(
              fontSize: 18, fontWeight: FontWeight.bold)
          ),
          broadcastStreamShowcase,
          broadcastStreamShowcase,
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          try {
            throw Exception('Example exception');
          } catch (e) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Caught an exception: $e'),
              ),
            );
          }

          // Break, continue
          for (var i = 0; i < 5; i++) {
            if (i == 2) continue;
            if (i == 4) break;
            print('i = $i');
          }

          // List, Set, Map
          print('List, Set, Map');
          var list = [1, 2, 3];
          assert(list.length == 3);
          assert(list[1] == 2);

          Set<int> myset = {1, 2, 3};
          print(myset);
          myset.add(1); // Adding duplicate item
          print(myset);

          var halogens = {
            'fluorine',
            'chlorine',
            'bromine',
            'iodine',
            'astatine'
          };
          var elements = <String>{};
          elements.add('fluorine');
          elements.addAll(halogens);
          print(elements);
          assert(elements.length == 5);

          print('Total workers: ${Worker.totalWorkers}');
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}

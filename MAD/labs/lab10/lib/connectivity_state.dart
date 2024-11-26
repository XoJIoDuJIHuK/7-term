import 'package:flutter_bloc/flutter_bloc.dart';


class ConnectivityCubit extends Cubit<bool> {
  ConnectivityCubit() : super(false);

  void set(newState) async => emit(newState);
}

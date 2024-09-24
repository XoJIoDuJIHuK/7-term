struct CA { // блок управления секцией
    char ipaddr[15]; // ip-адрес (xxx.xxx.xxx.xxx) координтора
    char resurce[20]; // имя ресурса
    enum STATUS {
        NOINIT, // начальное состояние
        INIT, // выполнена инициализация
        ENTER, // выполнен вход в секцию
        LEAVE, // выполнен выход из секции
        WAIT // ожидание входа
    } status; // состояние
};
CA InitCA(
    char ipaddr[15], // инициалзировать критическую секцию status-> INIT/NOINIT // ip-адрес (xxx.xxx.xxx.xxx) координтора
    char resurce[20] // имя ресурса
);
bool EnterCA( // войти в секцию status-> ENTER/WAIT -> ENTER
    CA& са // блок управления секцией 
);
bool LeaveCA( // покинуть секцию status-> LEAVE
    CA& са // блок управления секцией
);
bool CloseCA( // закрыть секцию status-> NOINIT
    CA& са // блок управления секцией
);
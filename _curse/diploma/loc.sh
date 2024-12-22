#!/bin/bash

# Массив исключений
EXCLUDE_DIRS=(
    ".venv"
    ".git"
    "__pycache__"
    "node_modules"
)

# Генерация параметров исключения
build_exclude_params() {
    local exclude_params=""
    for dir in "${EXCLUDE_DIRS[@]}"; do
        exclude_params+=" -not -path '*/$dir/*'"
    done
    echo "$exclude_params"
}

count_python_lines() {
    local total_lines=0
    local file_count=0
    local exclude_params=$(build_exclude_params)

    # Динамическое построение команды find с исключениями
    local find_command="find . -type f -name '*.py' ${exclude_params}"

    # Массив для хранения файлов
    mapfile -d '' python_files < <(eval "$find_command -print0")

    # Обработка найденных файлов
    for file in "${python_files[@]}"; do
        lines=$(wc -l < "$file")
        total_lines=$((total_lines + lines))
        file_count=$((file_count + 1))

        printf "Файл: %-50s | Строк: %5d\n" "$file" "$lines"
    done

    echo "----------------------------------------"
    printf "Всего файлов:      %d\n" "$file_count"
    printf "Общее число строк: %d\n" "$total_lines"
}

# Основной блок
main() {
    # Проверка наличия Python-файлов с исключениями
    local exclude_params=$(build_exclude_params)
    local python_files=$(eval "find . -type f -name '*.py' ${exclude_params}")

    if [ -z "$python_files" ]; then
        echo "Python-файлы не найдены"
        exit 1
    fi

    echo "Статистика Python-файлов:"
    echo "----------------------------------------"

    count_python_lines
}

# Запуск основной функции
main
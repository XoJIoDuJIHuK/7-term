const winston = require('winston');
const path = require('path');
const stackTrace = require('stacktrace-js');
const { format } = winston;

// Директория для сохранения логов
const logDirectory = path.join(__dirname, '../logs');

// Форматированный вывод логов
const customFormat = format.printf(({ timestamp, level, message, stack }) => {
    return `${timestamp} [${level}]: ${message} ${stack ? `\n${stack}` : ''}`;
});

// Общая конфигурация для winston
const logger = winston.createLogger({
    format: format.combine(
        format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }), 
        customFormat
    ),
    transports: [
        new winston.transports.Console(),
        new winston.transports.File({ 
            filename: path.join(logDirectory, 'logs.log')
        })
    ]
});

module.exports = logger;

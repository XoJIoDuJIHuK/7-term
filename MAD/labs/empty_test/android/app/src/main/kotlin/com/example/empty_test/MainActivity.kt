package com.example.empty_test

import android.os.Bundle
import io.flutter.embedding.android.FlutterActivity
import io.flutter.plugin.common.MethodChannel
import android.util.Log
import io.flutter.embedding.engine.FlutterEngine
import android.app.ActivityManager
import android.content.Context

class MainActivity: FlutterActivity() {
    private val CHANNEL = "cpu_usage_channel"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        Log.d("MainActivity", "OMEGALUL")
        logMemoryInfo()
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            Log.d("MainActivity", "Before logMemoryInfo")
            logMemoryInfo()
            if (call.method == "getMemoryInfo") {
                val memoryInfo = getMemoryInfo()
                if (memoryInfo != null) {
                    result.success(memoryInfo)
                } else {
                    result.error("UNAVAILABLE", "Memory info not available.", null)
                }
            } else {
                result.notImplemented()
            }
            Log.d("MainActivity", "After logMemoryInfo")
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("MainActivity", "onCreate")
        logMemoryInfo()
    }

    // Function to log total and used RAM
    private fun logMemoryInfo() {
        val memoryInfo = getMemoryInfo()
        Log.d("MainActivity", "Memory Info: $memoryInfo")
    }

    private fun getMemoryInfo(): String? {
        return try {
            val activityManager = getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
            val memoryInfo = ActivityManager.MemoryInfo()
            activityManager.getMemoryInfo(memoryInfo)

            val totalMemory = memoryInfo.totalMem
            val availableMemory = memoryInfo.availMem
            val usedMemory = totalMemory - availableMemory

            val result = "Total RAM: ${totalMemory / (1024 * 1024)} MB, Used RAM: ${usedMemory / (1024 * 1024)} MB"
            result
        } catch (e: Exception) {
            Log.e("MainActivity", e.toString())
            null
        }
    }
}
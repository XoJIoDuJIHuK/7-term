package com.example.empty_test

import android.os.Bundle
import io.flutter.embedding.android.FlutterActivity
import io.flutter.plugin.common.MethodChannel
import android.util.Log
import io.flutter.embedding.engine.FlutterEngine
import android.app.ActivityManager
import android.content.Context
import java.util.Calendar
import android.content.Intent
import android.provider.AlarmClock
import android.content.ContentValues
import android.content.ContextWrapper
import android.content.IntentFilter
import android.os.BatteryManager
import android.os.Build.VERSION
import android.os.Build.VERSION_CODES

class MainActivity: FlutterActivity() {
    private val CHANNEL = "cpu_usage_channel"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        Log.d("MainActivity", "OMEGALUL")
//        logMemoryInfo()
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            Log.d("MainActivity", "Before ${call.method}")
//            logMemoryInfo()
            if (call.method == "createAlarm") {
                val calendar = Calendar.getInstance()
                val hour = calendar.get(Calendar.HOUR_OF_DAY)
                val minute = calendar.get(Calendar.MINUTE)
                openAlarmClock(hour, minute, "LMAO Alarm")
            } else if (call.method == "getBatteryLevel") {
                getBatteryLevel();
            } else {
                result.notImplemented()
            }
            Log.d("MainActivity", "After logMemoryInfo")
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("MainActivity", "onCreate")
    }

    private fun openAlarmClock(hour: Int, minute: Int, message: String) {
        val intent = Intent(AlarmClock.ACTION_SET_ALARM).apply {
            putExtra(AlarmClock.EXTRA_HOUR, hour)
            putExtra(AlarmClock.EXTRA_MINUTES, minute)
            putExtra(AlarmClock.EXTRA_MESSAGE, message)
        }

        if (intent.resolveActivity(packageManager) != null) {
            startActivity(intent)
        } else {
            Log.e("MainActivity", "Unable to find matching activity")
        }
    }

    private fun getBatteryLevel(): Int {
        val batteryLevel: Int
        if (VERSION.SDK_INT >= VERSION_CODES.LOLLIPOP) {
            val batteryManager = getSystemService(Context.BATTERY_SERVICE) as BatteryManager
            batteryLevel = batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
        } else {
            val intent = ContextWrapper(applicationContext).registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
            batteryLevel = intent!!.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) * 100 / intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
        }

        Log.d("MainActivity", "Battery level: " + batteryLevel);

        return batteryLevel
    }

}
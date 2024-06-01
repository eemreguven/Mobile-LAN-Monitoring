package com.mrguven.mobilelanmonitor

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.lifecycle.Observer
import androidx.recyclerview.widget.LinearLayoutManager
import com.mrguven.mobilelanmonitor.api.ApiService
import com.mrguven.mobilelanmonitor.repository.Repository
import com.mrguven.mobilelanmonitor.viewmodel.MainViewModel
import com.mrguven.mobilelanmonitor.viewmodel.MainViewModelFactory
import com.mrguven.mobilelanmonitor.adapter.ClientAdapter
import com.mrguven.mobilelanmonitor.adapter.ThreatAdapter
import com.mrguven.mobilelanmonitor.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {

    private val viewModel: MainViewModel by viewModels {
        MainViewModelFactory(application, Repository(ApiService.create()))
    }

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            Toast.makeText(this, "Notification permission granted", Toast.LENGTH_SHORT).show()
        } else {
            Toast.makeText(this, "Notification permission denied", Toast.LENGTH_SHORT).show()
        }
    }

    private var lastNotificationTime: Long = 0
    private val notificationInterval: Long = 30 * 1000 // 30 seconds
    private val handler = Handler(Looper.getMainLooper())
    private val notificationRunnable = Runnable {
        viewModel.threats.value?.lastOrNull()?.let { latestThreat ->
            showThreatNotification(this, "Threat detected from ${latestThreat.ip} at ${latestThreat.timestamp}")
        }
    }

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Create notification channel
        createNotificationChannel(this)

        // Check and request notification permission if needed
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            when {
                ActivityCompat.checkSelfPermission(
                    this,
                    Manifest.permission.POST_NOTIFICATIONS
                ) == PackageManager.PERMISSION_GRANTED -> {
                    // Permission already granted
                }
                else -> {
                    // Permission not granted, request permission
                    requestPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
                }
            }
        }

        binding.clientRecyclerView.layoutManager = LinearLayoutManager(this)
        binding.threatRecyclerView.layoutManager = LinearLayoutManager(this)

        val clientAdapter = ClientAdapter(ApiService.create())
        val threatAdapter = ThreatAdapter()

        binding.clientRecyclerView.adapter = clientAdapter
        binding.threatRecyclerView.adapter = threatAdapter

        viewModel.clients.observe(this, Observer { clients ->
            clientAdapter.submitList(clients)
        })

        viewModel.threats.observe(this, Observer { threats ->
            threatAdapter.submitList(threats)
            if (threats.isNotEmpty()) {
                val currentTime = System.currentTimeMillis()
                if (currentTime - lastNotificationTime >= notificationInterval) {
                    handler.post(notificationRunnable)
                    lastNotificationTime = currentTime
                }
            }
        })

        viewModel.error.observe(this, Observer { errorMessage ->
            binding.mainContent.visibility = View.GONE
            binding.errorLayout.visibility = View.VISIBLE
            binding.errorTextView.text = errorMessage
        })

        binding.retryButton.setOnClickListener {
            binding.mainContent.visibility = View.VISIBLE
            binding.errorLayout.visibility = View.GONE
            viewModel.retryFetchingData()
        }
    }

    private fun createNotificationChannel(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val name = "Threat Notification Channel"
            val descriptionText = "Channel for threat notifications"
            val importance = NotificationManager.IMPORTANCE_HIGH
            val channel = NotificationChannel("THREAT_CHANNEL_ID", name, importance).apply {
                description = descriptionText
            }

            val notificationManager: NotificationManager =
                context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun showThreatNotification(context: Context, message: String) {
        if (ActivityCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED) {
            val intent = Intent(context, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            }
            val pendingIntent: PendingIntent = PendingIntent.getActivity(context, 0, intent, PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)

            val builder = NotificationCompat.Builder(context, "THREAT_CHANNEL_ID")
                .setSmallIcon(R.drawable.ic_launcher_foreground) // Set the notification icon
                .setContentTitle("Threat Detected")
                .setContentText(message)
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setContentIntent(pendingIntent)
                .setAutoCancel(true)

            with(NotificationManagerCompat.from(context)) {
                notify(1, builder.build())
            }
        } else {
            Toast.makeText(context, "Notification permission is missing", Toast.LENGTH_SHORT).show()
        }
    }
}

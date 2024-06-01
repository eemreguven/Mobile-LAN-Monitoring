package com.mrguven.mobilelanmonitor.model

data class Client(
    val ip: String,
    val upload_speed: Double,
    val download_speed: Double,
    val connected_to_internet: Boolean,
    val timestamp: String,
    val threat_detected: Boolean,
    val cpu_usage: Double,
    val memory_usage: Double,
    val packet_sent: Int,
    val packet_recv: Int,
    val error_in: Int,
    val error_out: Int,
    val drop_in: Int,
    val drop_out: Int,
    )

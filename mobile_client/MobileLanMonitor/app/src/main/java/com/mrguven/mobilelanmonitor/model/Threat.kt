package com.mrguven.mobilelanmonitor.model

data class Threat(
    val ip: String,
    val timestamp: String,
    val is_threat: Boolean
)
